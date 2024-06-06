from pydantic import BaseModel, Field
from typing import Optional, Union, List, Dict, Any, Literal
from uuid import uuid4


class Character(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(description="角色名称", example="Elon musk")
    alias: Optional[List[str]] = Field(default_factory=list, description="角色别称、昵称", example="Elon")
    gender: Optional[str] = Field(default=None, description="Female, Male, or Other. If not mentioned, then None.", example="Male")
    age: Optional[Union[str, int]] = Field(default=None, description="Age number or description. If not mentioned, then None.", examples="Young adult")
    appearance: Optional[str] = Field(default=None, description="The inherent appearance characteristics of the character, such as facial features, face shape, body shape, etc.", example="Orange long hair, deep eyes")
    personality: Optional[str] = Field(default=None, description="Personality traits, interests and hobbies, dislikes, speech patterns and catchphrases, habitual gestures, and body language. If not mentioned, then None.", example=None)
    background: Optional[str] = Field(default=None, description="角色的背景设定，例如职业、教育背景、家庭背景等", example="Single, parents divorced, sophomore in college")
    value_and_beliefs: Optional[str] = Field(default=None, description="Values, beliefs and more principles. If not mentioned, then None.", example="Non-religious, longing for freedom")
    summary: Optional[str] = Field(default=None, description="character introduction less than 3 sentences, concise but distinctive")


class Frame(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    type: Literal["picture", "description", "dialogue", "inner thought"]
    content: str
    scene_id: str
    start_idx: int
    end_idx: int
    character_names: List[str]
    index: Optional[int]


class Scene(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    content: str
    novel_id: str
    start_idx: int
    end_idx: int
    summary: Optional[str] = Field(default=None)
    index: Optional[int] = Field(default=None)


class Novel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: Optional[str] = Field(default=None)
    content: str = Field(description="小说原始文本")
    author: Optional[str] = Field(default=None, description="小说作者名称，如果小说作者包含多个人，则使用' & '拼接多个作者名称")
    summary: Optional[str] = Field(default=None, description="小说故事简介")
    categories: Optional[List[str]] = Field(default_factory=List)
