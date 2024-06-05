from langchain_core.runnables import ConfigurableField
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain import hub
from langchain.runnables.hub import HubRunnable
from langchain.chains.base import Chain
import os

from chimera.core import Character, CharacterList


def create_characters_extractor_agent():
    chat_model = ChatOpenAI(model=os.environ.get("MODEL"), base_url=os.environ.get("OPENAI_BASE_URL"), api_key=os.environ.get("OPENAI_API_KEY"), temperature=0.3).configurable_fields(
        model_name=ConfigurableField(id="model_name", name="model_name"),
        openai_api_base=ConfigurableField(id="openai_base_url", name="openai_base_url"),
        openai_api_key=ConfigurableField(id="openai_api_key", name="openai_api_key"),
        temperature=ConfigurableField(id="temperature",name="temperature", description="The temperature of the LLM"),
        )
    output_parser = JsonOutputParser(pydantic_object=CharacterList)
    prompt = hub.pull("kky/extract_characters").partial(format_instruction=output_parser.get_format_instructions())
    chain = prompt | chat_model | output_parser
    return chain
