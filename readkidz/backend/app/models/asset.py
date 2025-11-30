"""
ReadKidz Platform - Asset Model (User Uploads)
"""
from enum import Enum
from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum
from .base import BaseModel


class AssetType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"


class Asset(BaseModel):
    """User uploaded asset"""
    __tablename__ = "assets"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))

    # File info
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500))
    file_type = Column(SQLEnum(AssetType))
    mime_type = Column(String(100))
    file_size = Column(Integer)  # Size in bytes

    # Storage
    storage_path = Column(String(500))  # Path in storage
    url = Column(String(500))  # Public URL
    thumbnail_url = Column(String(500))

    # Image specific
    width = Column(Integer)
    height = Column(Integer)

    # Audio/Video specific
    duration = Column(Integer)  # Duration in seconds
