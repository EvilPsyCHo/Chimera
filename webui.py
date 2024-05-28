
import sys
import os
from pathlib import Path
import openai
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain import hub
import streamlit as st

# sys.path.append(str(Path(__file__).parent.parent))
from chimera.core import NovelChunk


URL = "https://oneapi.yuntu.chat/v1"
KEY = "sk-3CjP51UPhnB5WZv33cF3D4Df98E14eA18dCc1bD5E6B58d5d"
model_options = [m.id for m in openai.OpenAI(api_key=KEY, base_url=URL).models.list().data]
default_index = model_options.index("gpt-4o") if "gpt-4o" in model_options else 0
st.write("### 提取小说结构化信息")
st.write("prompt参照：https://smith.langchain.com/prompts/extract-scenes-from-novel-system?organizationId=951d1030-1685-5ba0-bdfd-d516f2214386")


def extract_novelchunk(model, prompt, text):
    chat_model = ChatOpenAI(model=model, base_url=URL, api_key=KEY)
    output_parser = PydanticOutputParser(pydantic_object=NovelChunk)
    chain = prompt | chat_model | output_parser
    res = chain.invoke(dict(input=text, format_instruction=output_parser.get_format_instructions()))
    return res


with st.form(key="extract novel"):
    prompt = hub.pull(st.text_input(label="langchainhub prompt", value= "kky/extract-scenes-from-novel-system"))
    model = st.selectbox(label="Model", options=model_options, index=default_index)
    text = st.text_area("novel", height=200)
    extract_button = st.form_submit_button(label='提取小说')

if extract_button:
    output_parser = PydanticOutputParser(pydantic_object=NovelChunk)
    prompt_value = prompt.invoke(dict(input=text, format_instruction=output_parser.get_format_instructions()))
    st.text(f"Model: {model}")
    st.text(f"Prompt: {prompt}")
    st.text(f"System Prompt: {prompt_value.messages[0].content}")
    with st.spinner():
        structured_novel = extract_novelchunk(model, prompt, text)
    st.text(structured_novel.model_dump_json(indent=4))
