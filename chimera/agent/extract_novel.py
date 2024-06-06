from langchain_core.runnables import ConfigurableField
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain import hub
from langchain.runnables.hub import HubRunnable
from langchain.chains.base import Chain
import os
from pydantic import BaseModel, Field
from typing import Optional, Union, List, Dict, Any, Literal
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from chimera.core import Novel


class NovelInfo(BaseModel):
    summary: str = Field(description="根据小说故事，使用3到5句话描写一段引人入胜的小说简介")
    categories: List[str] = Field(description="小说风格、要素标签，标签可以为多个，标签一般为2～4个字组成的单词或短语，例如：奇幻、科幻、都市、搞笑、悬疑、警匪等")
    leading_character_names: Optional[List[str]] = Field(default_factory=list, description="小说中的主要角色名称")


def _extract_novel(x):
    return Novel(**x["extracted"], **x["input"])


class ExtractNovelInput(BaseModel):
    content: str
    name: Optional[str]
    author: Optional[str]


def create_extract_novel_agent(with_parser=True):
    # input: name, author, content
    chat_model = ChatOpenAI(model=os.environ.get("MODEL"), base_url=os.environ.get("OPENAI_BASE_URL"), api_key=os.environ.get("OPENAI_API_KEY"), temperature=0.3).configurable_fields(
        model_name=ConfigurableField(id="model_name", name="model_name"),
        openai_api_base=ConfigurableField(id="openai_base_url", name="openai_base_url"),
        openai_api_key=ConfigurableField(id="openai_api_key", name="openai_api_key"),
        temperature=ConfigurableField(id="temperature",name="temperature", description="The temperature of the LLM"),
        )
    output_parser = JsonOutputParser(pydantic_object=NovelInfo)
    prompt = hub.pull("kky/extract_novel_info").partial(format_instruction=output_parser.get_format_instructions())
    chain = RunnableParallel(extracted = prompt | chat_model | output_parser, input=RunnablePassthrough()) | RunnableLambda(_extract_novel)
    return chain
