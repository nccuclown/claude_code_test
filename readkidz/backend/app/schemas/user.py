"""
ReadKidz Platform - User Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    display_name: Optional[str] = None


class UserCreate(UserBase):
    password: Optional[str] = None  # Optional for OAuth users


class UserUpdate(BaseModel):
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    language: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    username: Optional[str]
    display_name: Optional[str]
    avatar_url: Optional[str]
    language: str
    is_active: bool
    is_verified: bool
    is_parent_account: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class CreditsResponse(BaseModel):
    balance: int
    total_earned: int
    total_spent: int
    expires_at: Optional[datetime]
    subscription_tier: str

    class Config:
        from_attributes = True


class SubscriptionResponse(BaseModel):
    tier: str
    started_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    max_pages_per_story: int
    max_concurrent_tasks: int
    has_watermark: bool
    storage_days: int

    class Config:
        from_attributes = True
