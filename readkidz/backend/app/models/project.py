"""
ReadKidz Platform - Project Models
"""
from enum import Enum
from sqlalchemy import Column, String, Integer, Boolean, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import BaseModel


class ProjectType(str, Enum):
    PICTURE_BOOK = "picture_book"
    VIDEO = "video"
    SONG = "song"


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    GENERATING = "generating"
    COMPLETED = "completed"
    PUBLISHED = "published"
    FAILED = "failed"


class Project(BaseModel):
    """Main project container for books, videos, songs"""
    __tablename__ = "projects"

    # Basic info
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    project_type = Column(SQLEnum(ProjectType), default=ProjectType.PICTURE_BOOK)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.DRAFT)

    # Content settings
    target_age = Column(String(50))  # e.g., "3-5", "6-8"
    language = Column(String(20), default="zh-TW")
    style_id = Column(Integer, ForeignKey("styles.id"))

    # Image settings
    aspect_ratio = Column(String(10), default="16:9")  # 16:9, 4:3, 1:1, 3:4, 9:16

    # Video settings (if applicable)
    has_narration = Column(Boolean, default=True)
    voice_id = Column(String(100))
    background_music_id = Column(String(100))

    # Character Mat reference
    character_mat = Column(JSON)  # Store character reference info

    # Output files
    cover_image_url = Column(String(500))
    pdf_url = Column(String(500))
    video_url = Column(String(500))

    # Publishing
    is_public = Column(Boolean, default=False)
    youtube_url = Column(String(500))
    kdp_asin = Column(String(20))

    # Relationships
    user = relationship("User", back_populates="projects")
    pages = relationship("ProjectPage", back_populates="project", order_by="ProjectPage.page_number")
    characters = relationship("Character", back_populates="project")
    style = relationship("Style")


class ProjectPage(BaseModel):
    """Individual page in a project/book"""
    __tablename__ = "project_pages"

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    page_number = Column(Integer, nullable=False)

    # Content
    story_text = Column(Text)  # The story text for this page
    prompt = Column(Text)  # The prompt used for image generation
    image_url = Column(String(500))  # Generated/uploaded image
    thumbnail_url = Column(String(500))

    # Audio
    audio_url = Column(String(500))  # TTS audio for this page
    audio_duration = Column(Integer)  # Duration in seconds

    # Animation settings (for video)
    animation_type = Column(String(50))  # zoom_in, pan_left, etc.
    transition_type = Column(String(50))  # fade, slide, etc.

    # Relationships
    project = relationship("Project", back_populates="pages")


class Character(BaseModel):
    """Character definition for Character Mat feature"""
    __tablename__ = "characters"

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)

    # Character Mat settings
    reference_image_url = Column(String(500))  # White background reference
    similarity_score = Column(Integer, default=80)  # 0-100, how closely to match

    # Character traits (for prompt generation)
    traits = Column(JSON)  # {hair: "golden curly", eyes: "blue", etc.}

    # Relationships
    project = relationship("Project", back_populates="characters")
