"""
ReadKidz Platform - Content Generation Schemas
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


# Story Generation
class StoryGenerateRequest(BaseModel):
    """Request to generate a story"""
    prompt: str  # User's story idea/prompt
    mode: str = "original"  # original, adaptation
    template_id: Optional[int] = None  # Use template as base
    page_count: int = 12
    target_age: str = "3-6"
    language: str = "zh-TW"
    narrative_style: str = "warm"  # humorous, warm, adventure


class StoryPageContent(BaseModel):
    page_number: int
    text: str
    image_prompt: str  # Suggested prompt for illustration


class StoryResponse(BaseModel):
    id: int
    project_id: int
    title: str
    pages: List[StoryPageContent]
    word_count: int
    page_count: int
    narrative_style: str
    status: str
    credits_used: int
    created_at: datetime

    class Config:
        from_attributes = True


# Illustration Generation
class IllustrationGenerateRequest(BaseModel):
    """Request to generate an illustration"""
    prompt: str
    style_id: Optional[int] = None
    aspect_ratio: str = "16:9"
    character_id: Optional[int] = None  # For Character Mat
    use_character_mat: bool = False
    negative_prompt: Optional[str] = None
    seed: Optional[int] = None


class IllustrationResponse(BaseModel):
    id: int
    project_id: int
    page_id: Optional[int]
    prompt: str
    style_id: Optional[int]
    image_url: str
    thumbnail_url: Optional[str]
    width: int
    height: int
    status: str
    credits_used: int
    created_at: datetime

    class Config:
        from_attributes = True


# Video Generation
class VideoGenerateRequest(BaseModel):
    """Request to generate a video from project"""
    project_id: int
    resolution: str = "1080p"
    visual_style_id: Optional[int] = None
    animation_types: List[str] = ["zoom_in", "pan_left"]  # Animation types for pages
    transition_type: str = "fade"
    voice_id: Optional[str] = None
    background_music_id: Optional[str] = None
    has_subtitles: bool = True
    subtitle_font: str = "default"
    font_effect: str = "none"


class VideoResponse(BaseModel):
    id: int
    project_id: int
    video_url: Optional[str]
    thumbnail_url: Optional[str]
    duration: Optional[int]
    resolution: str
    status: str
    progress: int
    credits_used: int
    created_at: datetime

    class Config:
        from_attributes = True


# Audio/TTS Generation
class AudioGenerateRequest(BaseModel):
    """Request to generate audio/TTS"""
    text: str
    voice_id: str
    language: str = "zh-TW"
    speed: int = 100  # 50-200
    pitch: int = 100  # 50-200


class AudioResponse(BaseModel):
    id: int
    project_id: int
    page_id: Optional[int]
    audio_url: str
    duration: int
    voice_id: str
    status: str
    credits_used: int
    created_at: datetime

    class Config:
        from_attributes = True


# ChatPS AI Image Editor
class ChatPSEditRequest(BaseModel):
    """Request to edit image using natural language"""
    image_url: str  # Original image URL
    instruction: str  # Natural language edit instruction
    # e.g., "Make the dragon's scales blue"
    # e.g., "Add a moon in the sky"


class ChatPSEditResponse(BaseModel):
    original_image_url: str
    edited_image_url: str
    instruction: str
    credits_used: int


# One-Click Video Request (Combined)
class OneClickVideoRequest(BaseModel):
    """Request for one-click video generation from prompt"""
    prompt: str  # Story idea
    style_id: Optional[int] = None
    voice_id: Optional[str] = None
    background_music_id: Optional[str] = None
    page_count: int = 12
    target_age: str = "3-6"
    language: str = "zh-TW"
    # Use random for unspecified settings
    use_random_settings: bool = False


class GenerationStatusResponse(BaseModel):
    """Generic status response for any generation task"""
    task_id: str
    task_type: str  # story, illustration, video, audio
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    credits_used: int = 0
