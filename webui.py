
import sys
import os
from pathlib import Path
import openai
import streamlit as st
import json

from chimera.agent import create_characters_extractor_agent, create_novel_splitter_agent, create_scene_extractor_agent

characters_extractor = create_characters_extractor_agent()
novel_splitter = create_novel_splitter_agent()
scene_extractor = create_scene_extractor_agent()


def get_split_score(split_idxes, novel_len):
    overlap = 0
    overlook = 0
    for i in range(1, len(split_idxes)):
        s0, e0 = split_idxes[i-1][0], split_idxes[i-1][1]
        s1, e1 = split_idxes[i][0], split_idxes[i][1]
        overlap += max(0, e0 - s1)
        overlook = max(0, s1 - e0)
    
    overlook += novel_len - split_idxes[-1][1]
    overlook += split_idxes[0][0]
    return {
        "overlap": overlap / novel_len,
        "overlook": overlook / novel_len,
    }


st.markdown('''### Prompt
- [小说划分场景](https://smith.langchain.com/prompts/split_novel_to_scenes?organizationId=951d1030-1685-5ba0-bdfd-d516f2214386)
- [小说角色提取](https://smith.langchain.com/prompts/extract_characters?organizationId=951d1030-1685-5ba0-bdfd-d516f2214386)
- [小说场景提取](https://smith.langchain.com/prompts/extract_scene?organizationId=951d1030-1685-5ba0-bdfd-d516f2214386)''')


with st.form(key="extract novel"):
    text = st.text_area("novel", height=200)
    extract_button = st.form_submit_button(label='提取小说')


if extract_button:
    st.text(f"Model: {os.environ.get('MODEL')}")
    st.write("<<STEP 1>> 分割小说场景文本")
    with st.spinner("split scenes raw text ..."):
        split_info = novel_splitter.invoke(dict(input=text))
    scnees_split_idxes = split_info["scnees_split_idxes"]
    split_score = get_split_score(split_info["scnees_split_idxes"], len(text))
    
    st.write(f"重叠文本占比（越低越好）: {split_score['overlook'] * 100:.1f}%, 忽略文本占比（越低越好）: {split_score['overlap']*100:.1f}%")
    scenes_raw_texts = split_info["scenes_raw_text"]
    for i, s in enumerate(scenes_raw_texts):
        st.write(f"scene {i+1}: {s[:10]} ... {s[-10:]}")
    st.write("<<STEP 2>> 提取小说场景")

    for i, s in enumerate(scenes_raw_texts):
        with st.spinner(f"Extract scenes {i+1}"):
            scene = scene_extractor.invoke({"input": text})
        st.write(f"scene {i+1}")
        st.text(json.dumps(scene, indent=4, ensure_ascii=False))
    
    st.text("<<STEP 3>> 提取小说角色")

    with st.spinner(f"Extract characters ..."):
        characters = characters_extractor.invoke({"input": text})
    st.text(json.dumps(characters, indent=4, ensure_ascii=False))
