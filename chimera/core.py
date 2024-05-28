from pydantic import BaseModel, Field
from typing import Optional, Union, List, Dict, Any, Literal


class Character(BaseModel):
    name: str = Field(description="角色名称", example="Elon musk")
    alias: Optional[List[str]] = Field(default_factory=list, description="角色别称、昵称", example="Elon")
    gender: Optional[str] = Field(default=None, description="Female, Male, or Other. If not mentioned, then None.", example="Male")
    age: Optional[Union[str, int]] = Field(default=None, description="Age number or description. If not mentioned, then None.", examples="Young adult")
    appearance: Optional[str] = Field(default=None, description="The inherent appearance characteristics of the character, such as facial features, face shape, body shape, etc.", example="Orange long hair, deep eyes")
    personality: Optional[str] = Field(default=None, description="Personality traits, interests and hobbies, dislikes, speech patterns and catchphrases, habitual gestures, and body language. If not mentioned, then None.", example=None)
    background: Optional[str] = Field(default=None, description="角色的背景设定，例如职业、教育背景、家庭背景等", example="Single, parents divorced, sophomore in college")
    value_and_beliefs: Optional[str] = Field(default=None, description="Values, beliefs and more principles. If not mentioned, then None.", example="Non-religious, longing for freedom")
    summary: Optional[str] = Field(default=None, description="character introduction less than 3 sentences, concise but distinctive")


class DialogueFrame(BaseModel):
    '''对话帧(DialogueFrame)是一位角色的发言，包含角色发言内容和发言过程中的肢体语言及行为。'''
    type: Literal["dialogue"]
    character_name: str = Field(default_factory=list)
    content: str = Field(description="角色发言，需与原文保持完全一致")
    action: Optional[str] = Field(description="角色发言过程中的肢体语言或行为，需与原文保持完全一致")


class DescriptionFrame(BaseModel):
    '''描述帧(DescriptionFrame)是一段人物动作描写、剧情解释说明、独白，可以不包含任何角色，也可以包含一个或多个角色'''
    type: Literal["description"]
    character_names: Optional[List[str]] = Field(default_factory=list)
    content: str = Field(description="小说原文")


class InnerThoughtFrame(BaseModel):
    '''内心活动帧(InnerThoughtFrame)是一位角色的内心想法或活动'''
    type: Literal["dialogue"]
    character_name: str = Field(default_factory=list)
    content: str = Field(description="角色内心活动或想法，需与原文保持完全一致")


class Scene(BaseModel):
    '''场景(Scene)指故事中发生一段连续剧情，一般场景中的一些要素是连续的，例如地点、时间或人物。场景中会发生角色对话（DialogueFrame），角色内心活动（InnerThoughtFrame）或剧情描写（DescriptionFrame）。'''
    frames: List[Union[DescriptionFrame, DialogueFrame, InnerThoughtFrame]]
    environment: str = Field(description="场景视觉环境描写，尽可能保持与原文一致")


class KeyObject(BaseModel):
    '''小说中被反复提及的关键对象，可能是物品、环境场景或其他'''
    name: str = Field(description="关键对象的名称")
    alias: Union[List[str]] = Field(default_factory=list, description="关键对象的别称")
    description: str = Field(default=None, description="关键对象的详细描述")


class NovelChunk(BaseModel):
    scenes: List[Scene]
    key_objects: Optional[List[KeyObject]]
    characters: Optional[List[Character]]
