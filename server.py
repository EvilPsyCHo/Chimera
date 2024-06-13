import sys
import os
from pathlib import Path
import openai
import streamlit as st
import json
from pydantic import BaseModel
from typing import List, Union, Optional
from fastapi import FastAPI
from langserve import add_routes
from chimera.agent import (create_extract_novel_agent, create_split_novel_to_scenes_agent, create_extract_characters_agent, create_split_scene_to_frames_agent, create_generate_sd_prompt_agent, create_roleplay_agent,
                           ExtractCharactersInput, ExtractNovelInput, SplitSceneToFramesInput, SplitNovelToScenesInput, GenerateSDPromptAgentInput, RoleplayInput)
from chimera.memory import CharMemory
from chimera.core import Session, Message, Character, User

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--memory_path")
    args = parser.parse_args()

    # extract_novel_info_agent = create_extract_novel_agent()
    # extract_chars_agent = create_extract_characters_agent()
    # split_novel_agent = create_split_novel_to_scenes_agent()
    # split_scene_agent = create_split_scene_to_frames_agent()
    # generate_sd_prompt_agent = create_generate_sd_prompt_agent()
    # roleplay_agent = create_simple_roleplay_agent()
    # app = FastAPI(title="DEMO App")

    # add_routes(app, extract_novel_info_agent, path="/extract_novel", input_type=ExtractNovelInput)
    # add_routes(app, extract_chars_agent, path="/extract_chars", input_type=ExtractCharactersInput)
    # add_routes(app, split_novel_agent, path="/split_novel_to_scenes", input_type=SplitNovelToScenesInput)
    # add_routes(app, split_scene_agent, path="/split_scene_to_frames", input_type=SplitSceneToFramesInput)
    # add_routes(app, generate_sd_prompt_agent, path="/generate_sd_prompt", input_type=GenerateSDPromptAgentInput)
    # add_routes(app, roleplay_agent, path="/roleplay", input_type=SimpleRoleplayInput)

    app = FastAPI()
    database = CharMemory(args.memory_path, "char")
    roleplay_agent = create_roleplay_agent()

    class ChatRequest(BaseModel):
        messages: List[Message]
        turn: Union[Character, User]
        scene_index: int

    class ChatResponse(BaseModel):
        content: str

    @app.post("/chat", response_model=ChatResponse)
    async def chat(request: ChatRequest):
        memory = database.query(request.messages[-1].content, request.turn.name, request.scene_index)
        response = CharMemory.invoke({"messages": request.messages, "turn": request.turn, "memory": memory})
        return ChatResponse(content=response)


    # if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
