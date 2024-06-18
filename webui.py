
import sys
import os
from pathlib import Path
import openai
import streamlit as st
import json

save_path = Path(__file__).parent / "data"

from chimera.agent import create_extract_novel_agent, create_split_novel_to_scenes_agent, create_extract_characters_agent, create_split_scene_to_frames_agent, create_generate_sd_prompt_agent
from chimera.core import Novel, Scene, Frame, Character
from chimera.memory import CharMemory, NovelGlobalMemory


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


def search_character(name, characters):
    for c in characters:
        if (name == c.name) or (name in c.alias):
            return c


def get_active_characters_desc(scene, chars):
    desc = "Active characters:\n"
    for sc in scene["character_names"]:
        for c in chars:
            if (c["name"] == sc) or (sc in c["alias"]):
                desc += f"- Name: {c['name']}, Gender: {c['gender']}, Summary: {c['summary']}\n"
                break
    return desc.strip()

extract_novel_info_agent = create_extract_novel_agent()
extract_chars_agent = create_extract_characters_agent()
split_novel_agent = create_split_novel_to_scenes_agent()
split_scene_agent = create_split_scene_to_frames_agent()
generate_sd_prompt_agent = create_generate_sd_prompt_agent()


st.markdown('''### Prompt
- [小说信息提取](https://smith.langchain.com/prompts/extract_novel_info?organizationId=951d1030-1685-5ba0-bdfd-d516f2214386)
- [小说角色提取](https://smith.langchain.com/prompts/extract_characters?organizationId=951d1030-1685-5ba0-bdfd-d516f2214386)
- [小说划分场景](https://smith.langchain.com/prompts/split_novel_to_scenes?organizationId=951d1030-1685-5ba0-bdfd-d516f2214386)
- [场景划分frame](https://smith.langchain.com/prompts/split_scene_to_frames?organizationId=951d1030-1685-5ba0-bdfd-d516f2214386)
''')


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

    novel_path = save_path / novel.name
    novel_path.mkdir(exist_ok=True, parents=True)
    with open(novel_path / "novel.json", "w") as f:
        f.write(json.dumps(novel.dict(), indent=4, ensure_ascii=False))
    

    st.write("<<STEP 2>> 提取小说角色")
    with st.spinner(f"Extract characters ..."):
        characters = extract_chars_agent.invoke({"input": text})
    for char in characters:
        st.text(char.json(indent=4, ensure_ascii=False))
    with open(novel_path / "characters.json", "w") as f:
        f.write(json.dumps([c.dict() for c in characters], indent=4, ensure_ascii=False))
    character_names_and_alias = set([c.name for c in characters]) | set()

    st.write("检查主角是否全部包含在提取角色中 ...")
    for lc in novel.leading_character_names:
        if search_character(lc, characters) is None:
            st.write(f"主要角色{lc}未在角色列表中")
    st.write("检查完毕")
    


    st.write("<<STEP 3>> 分割小说场景")
    with st.spinner("split scenes ..."):
        scenes = split_novel_agent.invoke(novel.dict())
    scene_split_score = get_split_score([[s.start_idx, s.end_idx] for s in scenes], len(novel.content))
    st.write(f"重叠文本占比（越低越好）: {scene_split_score['overlap_rate'] * 100:.1f}%, 忽略文本占比（越低越好）: {scene_split_score['overlook_rate']*100:.1f}%")
    for scene in scenes:
        st.text(scene.json(indent=4, ensure_ascii=False))
        st.write("检查主角是否全部包含在提取角色中 ...")
        for c in scene.character_names:
            if search_character(lc, characters) is None:
                st.write(f"主要角色{lc}未在角色列表中")
        st.write("检查完毕")
    with open(novel_path / "scenes.json", "w") as f:
        f.write(json.dumps([c.dict() for c in scenes], indent=4, ensure_ascii=False))


    st.write("<<STEP 4>> 分割小说帧")
    scene_frames = {}
    for i, scene in enumerate(scenes):
        with st.spinner(f"split {i}th scene frames ..."):
            desc = get_active_characters_desc(scene.dict(), map(lambda x: x.dict(), characters))
            frames = split_scene_agent.invoke({"characters_desc": desc, **scene.dict()})
        scene_frames[scene.id] = [f.dict() for f in frames]
        frame_split_score = get_split_score([[f.start_idx, f.end_idx] for f in frames], len(scene.content))
        st.write(f"重叠文本占比（越低越好）: {frame_split_score['overlap_rate'] * 100:.1f}%, 忽略文本占比（越低越好）: {frame_split_score['overlook_rate']*100:.1f}%")
        for f in frames:
            st.text(f.json(indent=4, ensure_ascii=False))
    with open(novel_path / "frames.json", "w") as f:
        f.write(json.dumps(scene_frames, indent=4, ensure_ascii=False))
    

    st.write("<<STEP 5>> 存储记忆")
    memory = CharMemory(str(novel_path), "char")
    for scene in scenes:
        for f in scene_frames[scene.id]:
            if f["type"] == "dialogue":
                memory.add(f["content"], scene.index, f["speaker_name"])
            else:
                for char in f["participant_names"]:
                    memory.add(f["content"], scene.index, char)
    
    novel_memory = NovelGlobalMemory(str(novel_path), str(Path(__file__).parent/"models"/"text2vec-base-chinese"))
    novel_memory.add(novel.content)

    st.write("<<STEP 6>> 转化sd prompt")

    sd_prompt = {}
    for scene_id, frames in scene_frames.items():
        sd_prompt[scene_id] = []
        for f in frames:
            if f["type"] == "description":
                context = novel_memory.query(f["content"])
                input_characters = []
                for c in characters:
                    if c.name in f["participant_names"]:
                        input_characters.append(c.dict())

                pic = generate_sd_prompt_agent.invoke({"frame": f, "context": context, "characters": input_characters})
                sd_prompt[scene_id].append(pic)
                st.text(json.dumps(pic, indent=4, ensure_ascii=False))
    with open(novel_path / "sd_prompts.json", "w") as f:
        f.write(json.dumps(sd_prompt, indent=4, ensure_ascii=False))


    # sd_prompt = {}
    # for scene_id, frames in scene_frames.items():
    #     sd_prompt[scene_id] = []
    #     input_frames = []
    #     for f in frames:
    #         if f["type"] == "description":
    #             input_frames.append(f)
    #         else:
    #             if len(input_frames) > 0:
    #                 input_character_names = list(set([name for f in input_frames if f["participant_names"] for name in f["participant_names"]]))
    #                 input_characters = []
    #                 for c in characters:
    #                     if c.name in input_character_names:
    #                         input_characters.append(c.dict())

    #                 pic = generate_sd_prompt_agent.invoke({"frames": input_frames, "characters": input_characters})
    #                 input_frames = []
    #                 sd_prompt[scene_id].append(pic)
    #                 st.text(json.dumps(pic, indent=4, ensure_ascii=False))
    # with open(novel_path / "sd_prompts.json", "w") as f:
    #     f.write(json.dumps(sd_prompt, indent=4, ensure_ascii=False))
