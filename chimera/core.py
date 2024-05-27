from pydantic import BaseModel, Field
from typing import Optional, Union, List, Dict, Any, Literal


class Character(BaseModel):
    name: str = Field(description="角色名称", example="Elon musk")
    alias: List[str] = Field(default_factory=list, description="角色别称、昵称", example="Elon")
    gender: Optional[str] = Field(default=None, description="Female, Male, or Other. If not mentioned, then None.", example="Male")
    age: Optional[Union[str, int]] = Field(default=None, description="Age number or description. If not mentioned, then None.", examples="Young adult")
    appearance: Optional[str] = Field(default=None, description="The inherent appearance characteristics of the character, such as facial features, face shape, body shape, etc.", example="Orange long hair, deep eyes")
    personality: Optional[str] = Field(default=None, description="Personality traits, interests and hobbies, dislikes, speech patterns and catchphrases, habitual gestures, and body language. If not mentioned, then None.", example=None)
    background: Optional[str] = Field(default=None, description="角色的背景设定，例如职业、教育背景、家庭背景等", example="Single, parents divorced, sophomore in college")
    value_and_beliefs: Optional[str] = Field(default=None, description="Values, beliefs and more principles. If not mentioned, then None.", example="Non-religious, longing for freedom")
    summary: Optional[str] = Field(default=None, description="character introduction less than 3 sentences, concise but distinctive")


class Frame(BaseModel):
    '''帧(Frame)是场景(Scene)中的一个片段，可以是某名角色的"对话"或"内心独白", 也可以是一段"场景描述"或"剧情说明"。
    - "对话"或"内心独白"对应的角色有且只有一个
    - "场景描述"是一段视觉场景的描述，对应角色可以是零个或多个，
    - "剧情说明"是一段关于剧情推进、解释、说明的描述，对应的角色可以是零个或多个，'''
    type: Literal["对话", "内心独白", "场景描述", "剧情说明"]
    character_names: List[str] = Field(default_factory=list)
    content: str = Field(description="对话内容、内心独白内容、场景描述内容或剧情说明内容，需与原文保持完全一致。")


class Scene(BaseModel):
    '''场景(Scene)指故事中发生一段连续剧情，一般场景中的一些要素是连续的，例如地点、时间或人物。场景可能是一段对话，则每一帧(frame)为某位角色的发言，可能是一段情节的描述，例如一支军队的行军过程，每一帧(frame)是对行军过程中的一些场景或剧情的说明'''
    frames: List[Frame]


class KeyObject(BaseModel):
    '''小说中被反复提及的关键对象，可能是物品、环境场景或其他'''
    name: str = Field(description="关键对象的名称")
    alias: Union[List[str]] = Field(default_factory=list, description="关键对象的别称")
    description: str = Field(default=None, description="关键对象的详细描述")


class NovelChunk(BaseModel):
    scenes: List[Scene]
    key_objects: List[KeyObject]
    characters: List[Character]
