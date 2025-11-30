"""
ReadKidz Platform - Template and Style Models
"""
from sqlalchemy import Column, String, Integer, Boolean, Text, JSON
from .base import BaseModel


class Template(BaseModel):
    """Story template for quick start"""
    __tablename__ = "templates"

    # Basic info
    name = Column(String(200), nullable=False)
    name_zh = Column(String(200))  # Chinese name
    description = Column(Text)
    description_zh = Column(Text)

    # Classification
    category = Column(String(100))  # adventure, bedtime, animals, etc.
    tags = Column(JSON)  # ["fantasy", "friendship", ...]
    age_range = Column(String(20))  # "3-5", "6-8"

    # Template content
    story_outline = Column(Text)  # Story structure/outline
    sample_prompts = Column(JSON)  # Sample prompts for each page
    page_count = Column(Integer, default=12)

    # Visual
    thumbnail_url = Column(String(500))
    preview_images = Column(JSON)  # List of preview image URLs

    # Suggested style
    default_style_id = Column(Integer)

    # Availability
    is_free = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    # Usage stats
    use_count = Column(Integer, default=0)


class Style(BaseModel):
    """Art style for illustrations"""
    __tablename__ = "styles"

    # Basic info
    name = Column(String(200), nullable=False)
    name_zh = Column(String(200))  # Chinese name
    description = Column(Text)
    description_zh = Column(Text)

    # Classification
    category = Column(String(100))  # classic, official
    tags = Column(JSON)

    # Style settings
    style_prompt = Column(Text)  # Prompt modifier for this style
    negative_prompt = Column(Text)  # Negative prompt for this style

    # Visual samples
    thumbnail_url = Column(String(500))
    sample_images = Column(JSON)  # List of sample image URLs

    # Availability
    is_free = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)

    # Compatibility
    supported_ratios = Column(JSON, default=["16:9", "4:3", "1:1", "3:4", "9:16"])

    # Usage stats
    use_count = Column(Integer, default=0)


class Voice(BaseModel):
    """Voice option for TTS"""
    __tablename__ = "voices"

    # Basic info
    name = Column(String(200), nullable=False)
    name_zh = Column(String(200))
    description = Column(Text)

    # Provider info
    provider = Column(String(50))  # elevenlabs, azure, google
    provider_voice_id = Column(String(100))

    # Characteristics
    gender = Column(String(20))  # male, female, neutral
    age_group = Column(String(20))  # child, adult
    language = Column(String(20))  # en, zh, ja, etc.
    accent = Column(String(50))  # american, british, etc.

    # Sample
    sample_audio_url = Column(String(500))

    # Availability
    is_child_voice = Column(Boolean, default=False)
    is_free = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)


class BackgroundMusic(BaseModel):
    """Background music options"""
    __tablename__ = "background_music"

    # Basic info
    name = Column(String(200), nullable=False)
    name_zh = Column(String(200))
    description = Column(Text)

    # File info
    audio_url = Column(String(500))
    duration = Column(Integer)  # Duration in seconds
    bpm = Column(Integer)

    # Classification
    mood = Column(String(50))  # calm, happy, adventurous
    genre = Column(String(50))  # classical, ambient, playful

    # Availability
    is_free = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
