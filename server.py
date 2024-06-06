import sys
import os
from pathlib import Path
import openai
import streamlit as st
import json

from fastapi import FastAPI
from langserve import add_routes
from chimera.agent import (create_extract_novel_agent, create_split_novel_to_scenes_agent, create_extract_characters_agent, create_split_scene_to_frames_agent,
                           ExtractCharactersInput, ExtractNovelInput, SplitSceneToFramesInput, SplitNovelToScenesInput)

extract_novel_info_agent = create_extract_novel_agent()
extract_chars_agent = create_extract_characters_agent()
split_novel_agent = create_split_novel_to_scenes_agent()
split_scene_agent = create_split_scene_to_frames_agent()


app = FastAPI(title="Retrieval App")

add_routes(app, extract_novel_info_agent, path="/extract_novel", input_type=ExtractNovelInput)
add_routes(app, extract_chars_agent, path="/extract_chars", input_type=ExtractCharactersInput)
add_routes(app, split_novel_agent, path="/split_novel_to_scenes", input_type=SplitNovelToScenesInput)
add_routes(app, split_scene_agent, path="/split_scene_to_frames", input_type=SplitSceneToFramesInput)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
