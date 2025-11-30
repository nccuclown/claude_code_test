"""
ReadKidz Platform - User API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User, Subscription
from app.schemas.user import UserUpdate, UserResponse, SubscriptionResponse
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    """Get current user's profile"""
    return UserResponse.model_validate(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update current user's profile"""
    if update_data.username:
        # Check if username is taken
        result = await db.execute(
            select(User).where(
                User.username == update_data.username,
                User.id != current_user.id,
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = update_data.username

    if update_data.display_name:
        current_user.display_name = update_data.display_name

    if update_data.avatar_url:
        current_user.avatar_url = update_data.avatar_url

    if update_data.language:
        current_user.language = update_data.language

    await db.commit()
    await db.refresh(current_user)

    return UserResponse.model_validate(current_user)


@router.get("/subscription", response_model=SubscriptionResponse)
async def get_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's subscription details"""
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return SubscriptionResponse.model_validate(subscription)


@router.get("/settings")
async def get_settings(
    current_user: User = Depends(get_current_user),
):
    """Get user settings"""
    return {
        "language": current_user.language,
        "is_parent_account": current_user.is_parent_account,
    }


@router.put("/settings")
async def update_settings(
    language: str = None,
    is_parent_account: bool = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user settings"""
    if language:
        current_user.language = language

    if is_parent_account is not None:
        current_user.is_parent_account = is_parent_account

    await db.commit()

    return {
        "language": current_user.language,
        "is_parent_account": current_user.is_parent_account,
    }
