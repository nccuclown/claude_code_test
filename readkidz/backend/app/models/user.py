"""
ReadKidz Platform - User Models
"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from .base import BaseModel


class SubscriptionTier(str, Enum):
    FREE = "free"
    TRIAL = "trial"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    SUPER = "super"


class User(BaseModel):
    """User account model"""
    __tablename__ = "users"

    # Basic info
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True)
    display_name = Column(String(200))
    avatar_url = Column(String(500))

    # Authentication
    hashed_password = Column(String(255))  # Optional for OAuth users
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # OAuth
    google_id = Column(String(100), unique=True, index=True)
    facebook_id = Column(String(100), unique=True, index=True)

    # Settings
    language = Column(String(10), default="zh-TW")  # Interface language
    is_parent_account = Column(Boolean, default=False)

    # Relationships
    credits = relationship("UserCredits", back_populates="user", uselist=False)
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    projects = relationship("Project", back_populates="user")


class UserCredits(BaseModel):
    """User credits balance and history"""
    __tablename__ = "user_credits"

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Integer, default=1500)  # Free tier starts with 1500 credits
    total_earned = Column(Integer, default=1500)
    total_spent = Column(Integer, default=0)
    expires_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="credits")


class Subscription(BaseModel):
    """User subscription information"""
    __tablename__ = "subscriptions"

    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE)
    started_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    payment_provider = Column(String(50))  # stripe, oceanpayment
    payment_id = Column(String(100))

    # Plan limits
    max_pages_per_story = Column(Integer, default=5)
    max_concurrent_tasks = Column(Integer, default=1)
    has_watermark = Column(Boolean, default=True)
    storage_days = Column(Integer, default=30)

    # Relationships
    user = relationship("User", back_populates="subscription")
