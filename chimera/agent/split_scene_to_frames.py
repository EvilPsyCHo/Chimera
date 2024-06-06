
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
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from .utils import find_best_match_position
from ..core import Frame, Scene


# class Dialogue(BaseModel):
#     '''Dialogue指一名角色的发言及附带动作、表情、心理活动'''
#     type: Literal["dialogue"]
#     character_name: str = Field(description="说话的角色名称")
#     content: str = Field(description="角色发言，需与原文保持完全一致")
#     additional: Optional[str] = Field(default=None, description="角色发言过程中附带动作、表情、心理活动描写，需与原文保持完全一致。例如：她站起来说道")


# class InnerThought(BaseModel):
#     '''InnerThought指一位角色的内心想法及附带的动作、表情'''
#     type: Literal["inner thought"]
#     character_name: str = Field(description="角色名称")
#     content: str = Field(description="角色内心活动或想法，需与原文保持完全一致")
#     additional: Optional[str] = Field(default=None, description="角色的内心活动过程中附带的动作、表情，需与原文保持一致")


# class Description(BaseModel):
#     '''Description是一段剧情解释或说明文字，可以不包含任何角色，也可以包含一个或多个角色'''
#     type: Literal["description"]
#     character_names: Optional[List[str]] = Field(default_factory=list)
#     content: str = Field(description="小说原文")


# class Picture(BaseModel):
#     ''' Picture是小说中视觉、听觉、味觉等感官描述性文字所组成的画面'''
#     type: Literal["picture"]
#     content: str = Field(description="视觉、听觉、味觉等感官描述性内容，需与原文保持完全一致")
#     character_names: Optional[List[str]] = Field(default_factory=list, description="Picture中出现的角色名称")

class FrameSplitter(BaseModel):
    '''Frame是故事中的一个片段，片段有4种类型，分别是picture, description, dialogue, inner thought。'''
    type: Literal["picture", "description", "dialogue", "inner thought"]
    start_sentence: str
    start_sentence: str = Field(description="原文中代表该Frame开始时的句子，句子必须和原文保持完全一致，用于将故事片段切分为Frame")
    end_sentence: str = Field(description="原文中代表该Frame开始时的句子，句子必须和原文保持完全一致，用于将故事片段切分为Frame")
    character_names: List[str]



class FrameSplitters(BaseModel):
    frame_splitters: List[FrameSplitter] = Field(description="上一个frame的end_sentence与下一个frame的start_sentence应该在原文中是紧邻的两句话")


def convert_splitter_to_frame(x):
    scene, splitter = x["scene"], x["splitter"]
    frames = []
    for index, splitter in enumerate(splitter["frame_splitters"]):
        s_idx, e_idx = find_best_match_position(scene["content"], splitter["start_sentence"])[0], find_best_match_position(scene["content"], splitter["end_sentence"])[1]
        frames.append(Frame(
            type = splitter["type"],
            content = scene["content"][s_idx: e_idx],
            scene_id = scene["id"],
            start_idx = s_idx,
            end_idx=e_idx,
            character_names = splitter["character_names"],
            index = index
        ))
    return frames

class SplitSceneToFramesInput(Scene):
    ...


def create_split_scene_to_frames_agent():
    chat_model = ChatOpenAI(model=os.environ.get("MODEL"), base_url=os.environ.get("OPENAI_BASE_URL"), api_key=os.environ.get("OPENAI_API_KEY"), temperature=0.3).configurable_fields(
        model_name=ConfigurableField(id="model_name", name="model_name"),
        openai_api_base=ConfigurableField(id="openai_base_url", name="openai_base_url"),
        openai_api_key=ConfigurableField(id="openai_api_key", name="openai_api_key"),
        temperature=ConfigurableField(id="temperature",name="temperature", description="The temperature of the LLM"),
        )
    output_parser = JsonOutputParser(pydantic_object=FrameSplitters)
    prompt = hub.pull("kky/split_scene_to_frames").partial(format_instruction=output_parser.get_format_instructions())
    chain = {"scene": RunnablePassthrough(), "splitter": prompt | chat_model | output_parser} | RunnableLambda(convert_splitter_to_frame)
    return chain
