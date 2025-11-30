"""
ReadKidz Platform - Authentication API Routes (Simplified for Demo)
"""
import hashlib
import secrets
import base64
import json
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserCredits, Subscription, SubscriptionTier
from app.schemas.user import (
    UserCreate, UserResponse, TokenResponse, CreditsResponse
)

router = APIRouter()

# Simple password hashing (for demo - use bcrypt in production)
def hash_password(password: str) -> str:
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return hash_password(plain_password) == hashed_password

# Simple token generation (for demo - use JWT in production)
def create_access_token(user_id: int) -> str:
    """Create a simple access token"""
    data = {
        "user_id": user_id,
        "exp": (datetime.utcnow() + timedelta(days=7)).timestamp()
    }
    token_data = json.dumps(data)
    return base64.b64encode(token_data.encode()).decode()

def decode_access_token(token: str) -> Optional[int]:
    """Decode token and return user_id"""
    try:
        token_data = base64.b64decode(token.encode()).decode()
        data = json.loads(token_data)
        if data["exp"] < datetime.utcnow().timestamp():
            return None
        return data["user_id"]
    except Exception:
        return None

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login", auto_error=False)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


async def get_current_user_optional(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if not token:
        return None
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None


@router.post("/register", response_model=TokenResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user account"""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        display_name=user_data.display_name or user_data.username,
        hashed_password=hash_password(user_data.password) if user_data.password else None,
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Initialize credits and subscription
    now = datetime.utcnow()
    expires_at = now + timedelta(days=settings.CREDITS_EXPIRY_DAYS)

    credits = UserCredits(
        user_id=user.id,
        balance=settings.FREE_CREDITS,
        total_earned=settings.FREE_CREDITS,
        expires_at=expires_at,
    )
    db.add(credits)

    subscription = Subscription(
        user_id=user.id,
        tier=SubscriptionTier.FREE,
        started_at=now,
        expires_at=expires_at,
        is_active=True,
        max_pages_per_story=5,
        max_concurrent_tasks=1,
        has_watermark=True,
        storage_days=30,
    )
    db.add(subscription)
    await db.commit()

    # Create access token
    access_token = create_access_token(user.id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Login with email and password"""
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user.id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.get("/google")
async def google_login():
    """Initiate Google OAuth login"""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured. Please use email/password login.",
        )

    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid%20email%20profile"
    )

    return {"url": google_auth_url}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user information"""
    return UserResponse.model_validate(current_user)


@router.get("/me/credits", response_model=CreditsResponse)
async def get_current_user_credits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's credits balance"""
    result = await db.execute(
        select(UserCredits).where(UserCredits.user_id == current_user.id)
    )
    credits = result.scalar_one_or_none()

    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()

    if not credits:
        raise HTTPException(status_code=404, detail="Credits not found")

    return CreditsResponse(
        balance=credits.balance,
        total_earned=credits.total_earned,
        total_spent=credits.total_spent,
        expires_at=credits.expires_at,
        subscription_tier=subscription.tier.value if subscription else "free",
    )
