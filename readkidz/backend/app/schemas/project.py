"""
ReadKidz Platform - Project Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class CharacterBase(BaseModel):
    name: str
    description: Optional[str] = None
    traits: Optional[Dict[str, str]] = None  # {hair: "golden", eyes: "blue", ...}


class CharacterCreate(CharacterBase):
    reference_image_url: Optional[str] = None
    similarity_score: int = 80


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    reference_image_url: Optional[str] = None
    similarity_score: Optional[int] = None
    traits: Optional[Dict[str, str]] = None


class CharacterResponse(CharacterBase):
    id: int
    project_id: int
    reference_image_url: Optional[str]
    similarity_score: int
    created_at: datetime

    class Config:
        from_attributes = True


class PageBase(BaseModel):
    page_number: int
    story_text: Optional[str] = None
    prompt: Optional[str] = None


class PageCreate(PageBase):
    pass


class PageUpdate(BaseModel):
    story_text: Optional[str] = None
    prompt: Optional[str] = None
    image_url: Optional[str] = None
    animation_type: Optional[str] = None
    transition_type: Optional[str] = None


class PageResponse(PageBase):
    id: int
    project_id: int
    image_url: Optional[str]
    thumbnail_url: Optional[str]
    audio_url: Optional[str]
    audio_duration: Optional[int]
    animation_type: Optional[str]
    transition_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    project_type: str = "picture_book"
    target_age: Optional[str] = None
    language: str = "zh-TW"


class ProjectCreate(ProjectBase):
    style_id: Optional[int] = None
    aspect_ratio: str = "16:9"
    has_narration: bool = True
    voice_id: Optional[str] = None
    background_music_id: Optional[str] = None


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_age: Optional[str] = None
    language: Optional[str] = None
    style_id: Optional[int] = None
    aspect_ratio: Optional[str] = None
    has_narration: Optional[bool] = None
    voice_id: Optional[str] = None
    background_music_id: Optional[str] = None
    is_public: Optional[bool] = None


class ProjectResponse(ProjectBase):
    id: int
    user_id: int
    status: str
    style_id: Optional[int]
    aspect_ratio: str
    has_narration: bool
    voice_id: Optional[str]
    background_music_id: Optional[str]
    character_mat: Optional[Dict[str, Any]]
    cover_image_url: Optional[str]
    pdf_url: Optional[str]
    video_url: Optional[str]
    is_public: bool
    youtube_url: Optional[str]
    kdp_asin: Optional[str]
    created_at: datetime
    updated_at: datetime
    pages: List[PageResponse] = []
    characters: List[CharacterResponse] = []

    class Config:
        from_attributes = True


class ProjectListResponse(BaseModel):
    id: int
    title: str
    project_type: str
    status: str
    cover_image_url: Optional[str]
    page_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
