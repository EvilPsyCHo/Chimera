
import sys
import os
from pathlib import Path
import openai
import streamlit as st
import json

from chimera.agent import create_extract_novel_agent, create_split_novel_to_scenes_agent, create_extract_characters_agent, create_split_scene_to_frames_agent
from chimera.core import Novel, Scene, Frame, Character

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
        "overlap_rate": overlap / novel_len,
        "overlook_rate": overlook / novel_len,
    }

extract_novel_info_agent = create_extract_novel_agent()
extract_chars_agent = create_extract_characters_agent()
split_novel_agent = create_split_novel_to_scenes_agent()
split_scene_agent = create_split_scene_to_frames_agent()


st.markdown('''### Prompt
- [小说信息提取](https://smith.langchain.com/prompts/extract_novel_info?organizationId=951d1030-1685-5ba0-bdfd-d516f2214386)
- [小说角色提取](https://smith.langchain.com/prompts/extract_characters?organizationId=951d1030-1685-5ba0-bdfd-d516f2214386)
- [小说划分场景](https://smith.langchain.com/prompts/split_novel_to_scenes?organizationId=951d1030-1685-5ba0-bdfd-d516f2214386)
- [场景划分frame](https://smith.langchain.com/prompts/split_scene_to_frames?organizationId=951d1030-1685-5ba0-bdfd-d516f2214386)
'''
            )


with st.form(key="extract novel"):
    novel_name = st.text_input("novel name")
    novel_author = st.text_input("novel author")
    text = st.text_area("novel content", height=200)
    extract_button = st.form_submit_button(label='提取小说')


if extract_button:
    st.write(f"Model {os.environ.get('MODEL')}")

    st.write("<<STEP 1>> 提取小说信息")
    with st.spinner(f"Extract novel info ..."):
        novel = extract_novel_info_agent.invoke(dict(content=text, name=novel_name, author=novel_author))
    st.text(novel.json(indent=4, ensure_ascii=False))
    

    st.write("<<STEP 2>> 提取小说角色")
    with st.spinner(f"Extract characters ..."):
        characters = extract_chars_agent.invoke({"input": text})
    for char in characters:
        st.text(char.json(indent=4, ensure_ascii=False))


    st.write("<<STEP 3>> 分割小说场景")
    with st.spinner("split scenes ..."):
        scenes = split_novel_agent.invoke(novel.dict())
    scene_split_score = get_split_score([[s.start_idx, s.end_idx] for s in scenes], len(novel.content))
    st.write(f"重叠文本占比（越低越好）: {scene_split_score['overlook_rate'] * 100:.1f}%, 忽略文本占比（越低越好）: {scene_split_score['overlap_rate']*100:.1f}%")
    for scene in scenes:
        st.text(scene.json(indent=4, ensure_ascii=False))


    st.write("<<STEP 4>> 分割小说帧")
    scene_frames = {}
    for i, scene in enumerate(scenes):
        with st.spinner(f"split scene {i} frames ..."):
            frames = split_scene_agent.invoke(scene.dict())
        scene_frames[scene.id] = frames
        frame_split_score = get_split_score([[f.start_idx, f.end_idx] for f in frames], len(scene.content))
        st.write(f"重叠文本占比（越低越好）: {frame_split_score['overlook_rate'] * 100:.1f}%, 忽略文本占比（越低越好）: {frame_split_score['overlap_rate']*100:.1f}%")
        for f in frames:
            st.text(f.json(indent=4, ensure_ascii=False))
