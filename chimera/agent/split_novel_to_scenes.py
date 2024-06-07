
from langchain_core.runnables import ConfigurableField
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain import hub
import os
from pydantic import BaseModel, Field
from typing import Optional, Union, List, Dict, Any, Literal
import numpy as np
from operator import itemgetter
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda

from ..core import Scene, Novel
from .utils import find_best_match_position


class SceneSplitter(BaseModel):
    '''场景指故事中发生一段连续剧情，一般场景中的一些要素是连续的，例如地点、时间或人物。'''
    name: str = Field(description="场景名称")
    summary: str = Field(description="场景中的时间、环境、人物、事件的简介")
    start_sentence: str = Field(description="原文中代表该场景开始时的句子，句子必须和原文保持完全一致，用于将故事切分为场景")
    end_sentence: str = Field(description="原文中代表该场景结束的句子，句子必须和原文保持完全一致，用于将故事切分为场景")
    character_names: List[str] = Field(description="场景中的角色名称列表")


class SceneSplitters(BaseModel):
    scene_splitters: List[SceneSplitter] = Field(description="上一个场景的end_sentence与下一个场景的start_sentence应该在原文中是紧邻的两句话")



def convert_splitter_to_scenes(x):
    novel, splitter = x["novel"], x["splitter"]
    scenes = []
    for index, splitter in enumerate(splitter["scene_splitters"]):
        s_idx, e_idx = find_best_match_position(novel["content"], splitter["start_sentence"])[0], find_best_match_position(novel["content"], splitter["end_sentence"])[1]
        scenes.append(Scene(
            name = splitter["name"],
            content = novel["content"][s_idx: e_idx],
            novel_id = novel["id"],
            start_idx = s_idx,
            end_idx=e_idx,
            summary = splitter["summary"],
            index = index,
            character_names=splitter["character_names"]
        ))
    return scenes


class SplitNovelToScenesInput(Novel):
    ...


def create_split_novel_to_scenes_agent():
    chat_model = ChatOpenAI(model=os.environ.get("MODEL"), base_url=os.environ.get("OPENAI_BASE_URL"), api_key=os.environ.get("OPENAI_API_KEY"), temperature=0.3).configurable_fields(
        model_name=ConfigurableField(id="model_name", name="model_name"),
        openai_api_base=ConfigurableField(id="openai_base_url", name="openai_base_url"),
        openai_api_key=ConfigurableField(id="openai_api_key", name="openai_api_key"),
        temperature=ConfigurableField(id="temperature",name="temperature", description="The temperature of the LLM"),
        )
    output_parser = JsonOutputParser(pydantic_object=SceneSplitters)
    prompt = hub.pull("kky/split_novel_to_scenes").partial(format_instruction=output_parser.get_format_instructions())
    chain = {"novel": RunnablePassthrough(), "splitter": prompt | chat_model | output_parser} | RunnableLambda(convert_splitter_to_scenes)
    return chain
