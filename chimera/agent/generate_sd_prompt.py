from langchain_core.runnables import ConfigurableField
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser, StrOutputParser
from langchain import hub
from langchain.runnables.hub import HubRunnable
from langchain.chains.base import Chain
import os
from pydantic import BaseModel, Field
from typing import Optional, Union, List, Dict, Any, Literal
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda, RunnableAssign

from chimera.core import Frame, Character


class GenerateSDPromptAgentInput(BaseModel):
    frames: List[Frame]
    characters: List[Character]


def format_char(char):
    return f'''Name: {char["name"]}
Gender: {char["gender"]}
Age: {char["age"]}
Appearance: {char["appearance"]}
Summary: {char["summary"]}'''


def _convert_to_input(x):
    frame = x["frame"]
    characters = frame["participant_names"]
    scene_id = frame["scene_id"]
    index = frame["index"]
    descrption = f"当前场景：\n{frame['content']}\n\n场景相关的小说内容:\n{x['context']}"
    if len(x["characters"]) > 0:
        characters = "\n".join(list(map(format_char, x["characters"])))
        descrption = descrption + f'\n\n场景中的角色：\n{characters}'
    character_names = frame["participant_names"]
    return {
        "scene_id": scene_id,
        "index": index,
        "description": descrption,
        "character_names": character_names,
    }


def create_generate_sd_prompt_agent(with_parser=True):
    # input: name, author, content
    chat_model = ChatOpenAI(model=os.environ.get("MODEL"), base_url=os.environ.get("OPENAI_BASE_URL"), api_key=os.environ.get("OPENAI_API_KEY"), temperature=0.3).configurable_fields(
        model_name=ConfigurableField(id="model_name", name="model_name"),
        openai_api_base=ConfigurableField(id="openai_base_url", name="openai_base_url"),
        openai_api_key=ConfigurableField(id="openai_api_key", name="openai_api_key"),
        temperature=ConfigurableField(id="temperature",name="temperature", description="The temperature of the LLM"),
        )
    output_parser = StrOutputParser()
    prompt = hub.pull("kky/generate_sd_prompt")
    chain = RunnableLambda(_convert_to_input) | RunnablePassthrough.assign(prompt=prompt | chat_model | output_parser)
    return chain
