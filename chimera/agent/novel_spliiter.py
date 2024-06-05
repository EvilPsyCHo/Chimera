
from langchain_core.runnables import ConfigurableField
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain import hub
import os
from pydantic import BaseModel, Field
from typing import Optional, Union, List, Dict, Any, Literal
import numpy as np
from langchain_core.runnables import RunnableLambda
from operator import itemgetter
from langchain.chains import sequential


class SceneSplitter(BaseModel):
    '''场景指故事中发生一段连续剧情，一般场景中的一些要素是连续的，例如地点、时间或人物。'''
    summary: str = Field(description="场景中的时间、环境、人物、事件的简介")
    start_sentence: str = Field(description="原文中代表该场景开始时的句子，句子必须和原文保持完全一致，用于将故事切分为场景")
    end_sentence: str = Field(description="原文中代表该场景结束的句子，句子必须和原文保持完全一致，用于将故事切分为场景")


class SceneSplitters(BaseModel):
    scene_splitters: List[SceneSplitter] = Field(description="上一个场景的end_sentence与下一个场景的start_sentence应该在原文中是紧邻的两句话")


def levenshtein_distance(s1, s2):
    len_s1, len_s2 = len(s1), len(s2)
    dp = np.zeros((len_s1 + 1, len_s2 + 1))

    for i in range(len_s1 + 1):
        dp[i][0] = i
    for j in range(len_s2 + 1):
        dp[0][j] = j

    for i in range(1, len_s1 + 1):
        for j in range(1, len_s2 + 1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
    
    return dp[len_s1][len_s2]


def find_best_match_position(source_text, target_text):
    min_distance = float('inf')
    best_position = -1

    for i in range(len(source_text) - len(target_text) + 1):
        window = source_text[i:i + len(target_text)]
        distance = levenshtein_distance(window, target_text)
        if distance < min_distance:
            min_distance = distance
            best_position = i
    
    return best_position, best_position+len(target_text)


def index_scene_in_novel(x):
    input, output = x["input"], x["output"]
    split_idxes = []
    for splitter in output["scene_splitters"]:
        i0, i1 = find_best_match_position(input, splitter["start_sentence"]), find_best_match_position(input, splitter["end_sentence"])
        split_idxes.append([i0[0], i1[1]])
    scenes_raw_text = [input[start: end] for start, end in split_idxes]
    return {
        "scenes_raw_text": scenes_raw_text,
        "scnees_split_idxes": split_idxes,
    }



def create_novel_splitter_agent():
    chat_model = ChatOpenAI(model=os.environ.get("MODEL"), base_url=os.environ.get("OPENAI_BASE_URL"), api_key=os.environ.get("OPENAI_API_KEY"), temperature=0.3).configurable_fields(
        model_name=ConfigurableField(id="model_name", name="model_name"),
        openai_api_base=ConfigurableField(id="openai_base_url", name="openai_base_url"),
        openai_api_key=ConfigurableField(id="openai_api_key", name="openai_api_key"),
        temperature=ConfigurableField(id="temperature",name="temperature", description="The temperature of the LLM"),
        )
    output_parser = JsonOutputParser(pydantic_object=SceneSplitters)
    prompt = hub.pull("kky/split_novel_to_scenes").partial(format_instruction=output_parser.get_format_instructions())
    chain = {"input": itemgetter("input"), "output": prompt | chat_model | output_parser} | RunnableLambda(index_scene_in_novel)
    return chain
