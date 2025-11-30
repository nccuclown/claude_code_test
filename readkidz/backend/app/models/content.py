"""
ReadKidz Platform - Content Models (Generated Content)
"""
from enum import Enum
from sqlalchemy import Column, String, Integer, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import BaseModel


class GenerationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Story(BaseModel):
    """Generated story content"""
    __tablename__ = "stories"

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Input
    original_prompt = Column(Text)
    mode = Column(String(50), default="original")  # original, adaptation

    # Generated content
    title = Column(String(500))
    full_text = Column(Text)  # Complete story
    pages_content = Column(JSON)  # [{page_number: 1, text: "..."}, ...]

    # Metadata
    word_count = Column(Integer)
    page_count = Column(Integer)
    narrative_style = Column(String(50))  # humorous, warm, adventure

    # Generation info
    model_used = Column(String(100))  # gpt-4, claude-3
    status = Column(SQLEnum(GenerationStatus), default=GenerationStatus.PENDING)
    error_message = Column(Text)
    credits_used = Column(Integer, default=0)


class Illustration(BaseModel):
    """Generated illustration/image"""
    __tablename__ = "illustrations"

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    page_id = Column(Integer, ForeignKey("project_pages.id"))

    # Input
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text)
    style_id = Column(Integer, ForeignKey("styles.id"))

    # Character Mat
    character_id = Column(Integer, ForeignKey("characters.id"))
    use_character_mat = Column(Integer, default=False)

    # Settings
    aspect_ratio = Column(String(10), default="16:9")
    seed = Column(Integer)

    # Output
    image_url = Column(String(500))
    thumbnail_url = Column(String(500))
    width = Column(Integer)
    height = Column(Integer)

    # Generation info
    model_used = Column(String(100))  # dall-e-3, midjourney
    status = Column(SQLEnum(GenerationStatus), default=GenerationStatus.PENDING)
    error_message = Column(Text)
    credits_used = Column(Integer, default=0)


class Video(BaseModel):
    """Generated video content"""
    __tablename__ = "videos"

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Settings
    resolution = Column(String(20), default="1080p")
    duration = Column(Integer)  # Total duration in seconds
    fps = Column(Integer, default=30)

    # Visual
    visual_style_id = Column(Integer, ForeignKey("styles.id"))
    animation_types = Column(JSON)  # List of animation types used
    transition_type = Column(String(50))
    has_subtitles = Column(Integer, default=True)
    subtitle_font = Column(String(100))
    font_effect = Column(String(50))

    # Audio
    voice_id = Column(String(100))
    background_music_id = Column(String(100))
    has_narration = Column(Integer, default=True)

    # Output
    video_url = Column(String(500))
    thumbnail_url = Column(String(500))

    # Generation info
    status = Column(SQLEnum(GenerationStatus), default=GenerationStatus.PENDING)
    progress = Column(Integer, default=0)  # 0-100
    error_message = Column(Text)
    credits_used = Column(Integer, default=0)


class Audio(BaseModel):
    """Generated audio/TTS content"""
    __tablename__ = "audios"

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    page_id = Column(Integer, ForeignKey("project_pages.id"))

    # Input
    text = Column(Text, nullable=False)
    voice_id = Column(String(100))
    language = Column(String(20), default="zh-TW")

    # Settings
    speed = Column(Integer, default=100)  # Percentage: 50-200
    pitch = Column(Integer, default=100)

    # Output
    audio_url = Column(String(500))
    duration = Column(Integer)  # Duration in milliseconds
    format = Column(String(10), default="mp3")

    # Generation info
    model_used = Column(String(100))  # elevenlabs
    status = Column(SQLEnum(GenerationStatus), default=GenerationStatus.PENDING)
    error_message = Column(Text)
    credits_used = Column(Integer, default=0)
