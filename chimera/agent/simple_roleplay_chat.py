from langchain_core.runnables import ConfigurableField, RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser, StrOutputParser
from langchain import hub
from langchain.runnables.hub import HubRunnable
import os

from chimera.core import Session


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


def prepare_input(session):
    # process message history
    history = []
    cache = []
    turn = session["turn"]
    for mes in session["messages"]:
        if mes["type"] == "character" and mes["turn"]["id"] == turn["id"]:
            if len(cache) > 0:
                history.append(("user", "\n\n".join(cache)))
                cache = []
            history.append(("assistant", mes["content"]))
        else:
            cache.append(f"{mes['turn']['name']}: {mes['content']}")
    if len(cache) > 0:
        history.append(("user", "\n\n".join(cache)))
    
    profile = format_char(turn)
    return {
        "char_profile": profile,
        "char": turn["name"],
        "history": history,
    }


class SimpleRoleplayInput(Session):
    ...


def create_simple_roleplay_agent():
    chat_model = ChatOpenAI(model=os.environ.get("MODEL"), base_url=os.environ.get("OPENAI_BASE_URL"), api_key=os.environ.get("OPENAI_API_KEY"), temperature=0.3).configurable_fields(
        model_name=ConfigurableField(id="model_name", name="model_name"),
        openai_api_base=ConfigurableField(id="openai_base_url", name="openai_base_url"),
        openai_api_key=ConfigurableField(id="openai_api_key", name="openai_api_key"),
        temperature=ConfigurableField(id="temperature",name="temperature", description="The temperature of the LLM"),
        )
    output_parser = StrOutputParser()
    prompt = hub.pull("kky/simple_roleplay_chat")
    chain = RunnableLambda(prepare_input) | prompt | chat_model | output_parser
    return chain
