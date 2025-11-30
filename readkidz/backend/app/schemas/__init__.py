"""
ReadKidz Platform - Pydantic Schemas
"""
from .user import (
    UserCreate, UserUpdate, UserResponse, UserLogin,
    TokenResponse, CreditsResponse
)
from .project import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    PageCreate, PageUpdate, PageResponse,
    CharacterCreate, CharacterUpdate, CharacterResponse
)
from .content import (
    StoryGenerateRequest, StoryResponse,
    IllustrationGenerateRequest, IllustrationResponse,
    VideoGenerateRequest, VideoResponse,
    AudioGenerateRequest, AudioResponse,
    ChatPSEditRequest
)
from .template import (
    TemplateResponse, StyleResponse, VoiceResponse, MusicResponse
)

__all__ = [
    # User
    "UserCreate", "UserUpdate", "UserResponse", "UserLogin",
    "TokenResponse", "CreditsResponse",
    # Project
    "ProjectCreate", "ProjectUpdate", "ProjectResponse",
    "PageCreate", "PageUpdate", "PageResponse",
    "CharacterCreate", "CharacterUpdate", "CharacterResponse",
    # Content
    "StoryGenerateRequest", "StoryResponse",
    "IllustrationGenerateRequest", "IllustrationResponse",
    "VideoGenerateRequest", "VideoResponse",
    "AudioGenerateRequest", "AudioResponse",
    "ChatPSEditRequest",
    # Template
    "TemplateResponse", "StyleResponse", "VoiceResponse", "MusicResponse",
]
