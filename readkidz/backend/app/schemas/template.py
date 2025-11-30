"""
ReadKidz Platform - Template Schemas
"""
from typing import Optional, List
from pydantic import BaseModel


class TemplateResponse(BaseModel):
    id: int
    name: str
    name_zh: Optional[str]
    description: Optional[str]
    description_zh: Optional[str]
    category: str
    tags: List[str]
    age_range: Optional[str]
    page_count: int
    thumbnail_url: Optional[str]
    preview_images: List[str]
    is_free: bool
    use_count: int

    class Config:
        from_attributes = True


class StyleResponse(BaseModel):
    id: int
    name: str
    name_zh: Optional[str]
    description: Optional[str]
    description_zh: Optional[str]
    category: str
    tags: List[str]
    thumbnail_url: Optional[str]
    sample_images: List[str]
    is_free: bool
    supported_ratios: List[str]
    use_count: int

    class Config:
        from_attributes = True


class VoiceResponse(BaseModel):
    id: int
    name: str
    name_zh: Optional[str]
    description: Optional[str]
    gender: str
    age_group: str
    language: str
    accent: Optional[str]
    sample_audio_url: Optional[str]
    is_child_voice: bool
    is_free: bool

    class Config:
        from_attributes = True


class MusicResponse(BaseModel):
    id: int
    name: str
    name_zh: Optional[str]
    description: Optional[str]
    audio_url: Optional[str]
    duration: Optional[int]
    mood: str
    genre: str
    is_free: bool

    class Config:
        from_attributes = True


class TemplateListRequest(BaseModel):
    category: Optional[str] = None
    age_range: Optional[str] = None
    is_free: Optional[bool] = None
    search: Optional[str] = None
    limit: int = 20
    offset: int = 0


class StyleListRequest(BaseModel):
    category: Optional[str] = None
    is_free: Optional[bool] = None
    search: Optional[str] = None
    limit: int = 20
    offset: int = 0
