from chimera.agent.roleplay_chat import create_simple_roleplay_agent
from chimera.memory import CharMemory
import os
from pathlib import Path

chat_agent = create_simple_roleplay_agent()
save_path = Path(__file__).parent / "data"
novel_list = list(map(lambda x: x.name, save_path.iterdir()))
user = {"name": "kky"}

import streamlit as st
from pathlib import Path
import json


def role_response(text):
    st.session_state["messages"].append(
        {"role": "user", "content": text, "type": "user", "turn": user}
    )
    output = chat_agent.invoke({"messages": st.session_state["messages"], "turn": st.session_state["character"]})
    st.session_state["messages"].append(
        {"role": "assistant", "content": output, "type": "character", "turn": st.session_state["character"]}
    )
    return output



with st.form(key="chat"):
    novel = st.text_input("novel")
    char_name = st.text_input("character name")
    scene_index = st.text_input("scene index")
    submit = st.form_submit_button(label='加载')

if submit:
    with open(save_path/novel/"characters.json", "r") as f:
        chars = json.load(f)
    char = None
    for c in chars:
        if c["name"] == char_name:
            char = c
    st.session_state["character"] = char
    st.session_state["user"] = user
    st.session_state["messages"] = []
    st.session_state["scene_index"] = int(scene_index)
    st.session_state["memory"] = CharMemory(str(save_path / novel), "char")


user_input = st.text_input("user input")
if user_input:
    retrieval = st.session_state["memory"].query(user_input, scene_index=st.session_state["scene_index"], character_name=st.session_state["character"]["name"])
    st.write("Memory:")
    st.text(retrieval)
    response = role_response(user_input)
    st.write("response:")
    st.write(response)
