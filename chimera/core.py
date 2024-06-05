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


class CharacterList(BaseModel):
    characters: List[Character]



class Dialogue(BaseModel):
    '''Dialogue指一名角色的发言及附带动作、表情、心理活动'''
    type: Literal["dialogue"]
    character_name: str = Field(description="说话的角色名称")
    content: str = Field(description="角色发言，需与原文保持完全一致")
    additional: Optional[str] = Field(default=None, description="角色发言过程中附带动作、表情、心理活动描写，需与原文保持完全一致。例如：她站起来说道")


class InnerThought(BaseModel):
    '''InnerThought指一位角色的内心想法及附带的动作、表情'''
    type: Literal["inner thought"]
    character_name: str = Field(description="角色名称")
    content: str = Field(description="角色内心活动或想法，需与原文保持完全一致")
    additional: Optional[str] = Field(default=None, description="角色的内心活动过程中附带的动作、表情，需与原文保持一致")


class Description(BaseModel):
    '''Description是一段剧情解释或说明文字，可以不包含任何角色，也可以包含一个或多个角色'''
    type: Literal["description"]
    character_names: Optional[List[str]] = Field(default_factory=list)
    content: str = Field(description="小说原文")


class Picture(BaseModel):
    ''' Picture是小说中视觉、听觉、味觉等感官描述性文字所组成的画面'''
    type: Literal["picture"]
    content: str = Field(description="视觉、听觉、味觉等感官描述性内容，需与原文保持完全一致")
    character_names: Optional[List[str]] = Field(default_factory=list, description="Picture中出现的角色名称")



class Scene(BaseModel):
    '''场景(Scene)指故事中发生一段连续剧情，一般场景中的一些要素是连续的，例如地点、时间或人物。场景中会发生角色对话（Dialogue），角色内心活动（InnerThought），感官描写（Picture）或剧情说明（Description)'''
    name: str = Field(description="Scene name, generally named with location, time, or event.")
    environment: str = Field(description="贯穿整个场景视觉环境，描写语言尽可能保持与原文一致")
    summary: str = Field(description="场景发生的故事简介")
    frames: List[Union[Picture, Description, InnerThought, Dialogue]]
