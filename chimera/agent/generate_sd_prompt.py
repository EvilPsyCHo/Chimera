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
Alias: {",".join(char["alias"]) if len(char["alias"]) > 0 else "None"}
Gender: {char["gender"]}
Age: {char["age"]}
Appearance: {char["appearance"]}
Personality: {char["personality"]}
Background: {char["background"]}
Value_and_beliefs: {char["value_and_beliefs"]}
Summary: {char["summary"]}'''


def _convert_to_input(x):
    frames = x["frames"]
    characters = "Characters:\n" + "\n\n".join([format_char(c) for c in x["characters"]])
    
    scene_id = frames[0]["scene_id"]
    index = frames[0]["index"]
    descrption = "\n".join([f["content"] for f in frames])
    character_names = list(set([name for f in frames if f["participant_names"] for name in f["participant_names"]]))
    return {
        "scene_id": scene_id,
        "index": index,
        "description": descrption + characters,
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
