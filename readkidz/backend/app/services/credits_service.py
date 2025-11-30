"""
ReadKidz Platform - Credits Management Service
Handles user credits, subscriptions, and billing
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, UserCredits, Subscription, SubscriptionTier
from app.core.config import settings

logger = logging.getLogger(__name__)


# Subscription tier configurations
TIER_CONFIGS = {
    SubscriptionTier.FREE: {
        "credits": 1500,
        "expiry_days": 30,
        "max_pages": 5,
        "max_concurrent": 1,
        "has_watermark": True,
        "storage_days": 30,
        "templates": 2,
        "styles": 6,
    },
    SubscriptionTier.TRIAL: {
        "credits": 3000,
        "expiry_days": 7,
        "max_pages": 12,
        "max_concurrent": 2,
        "has_watermark": False,
        "storage_days": 7,
        "templates": 40,
        "styles": 30,
    },
    SubscriptionTier.STANDARD: {
        "credits": 12000,  # 10000 + 2000 bonus
        "expiry_days": 30,
        "max_pages": 40,
        "max_concurrent": 4,
        "has_watermark": False,
        "storage_days": 30,
        "templates": 100,
        "styles": 60,
    },
    SubscriptionTier.PROFESSIONAL: {
        "credits": 30000,
        "expiry_days": 90,
        "max_pages": 50,
        "max_concurrent": 5,
        "has_watermark": False,
        "storage_days": 90,
        "templates": 100,
        "styles": 60,
    },
    SubscriptionTier.SUPER: {
        "credits": 60000,
        "expiry_days": 180,
        "max_pages": 60,
        "max_concurrent": 8,
        "has_watermark": False,
        "storage_days": 180,
        "templates": 100,
        "styles": 60,
    },
}

# Pricing (in USD)
TIER_PRICING = {
    SubscriptionTier.FREE: 0,
    SubscriptionTier.TRIAL: 3,
    SubscriptionTier.STANDARD: 10,
    SubscriptionTier.PROFESSIONAL: 30,  # Often discounted to $20
    SubscriptionTier.SUPER: 60,  # Often discounted to $42
}


class CreditsService:
    """Service for managing user credits and subscriptions"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_credits(self, user_id: int) -> Optional[UserCredits]:
        """Get user's credit balance"""
        result = await self.db.execute(
            select(UserCredits).where(UserCredits.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_user_subscription(self, user_id: int) -> Optional[Subscription]:
        """Get user's subscription info"""
        result = await self.db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def initialize_free_user(self, user: User) -> Tuple[UserCredits, Subscription]:
        """Initialize credits and subscription for a new free user"""
        now = datetime.utcnow()
        expires_at = now + timedelta(days=settings.CREDITS_EXPIRY_DAYS)

        # Create credits
        credits = UserCredits(
            user_id=user.id,
            balance=settings.FREE_CREDITS,
            total_earned=settings.FREE_CREDITS,
            total_spent=0,
            expires_at=expires_at,
        )
        self.db.add(credits)

        # Create free subscription
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
        self.db.add(subscription)

        await self.db.commit()
        await self.db.refresh(credits)
        await self.db.refresh(subscription)

        return credits, subscription

    async def check_and_deduct_credits(
        self,
        user_id: int,
        amount: int,
        operation: str,
    ) -> Tuple[bool, str]:
        """
        Check if user has enough credits and deduct if so.

        Args:
            user_id: User ID
            amount: Amount of credits to deduct
            operation: Description of the operation

        Returns:
            Tuple of (success, message)
        """
        credits = await self.get_user_credits(user_id)

        if not credits:
            return False, "Credits not found for user"

        # Check expiry
        if credits.expires_at and credits.expires_at < datetime.utcnow():
            return False, "Credits have expired. Please renew your subscription."

        # Check balance
        if credits.balance < amount:
            return False, f"Insufficient credits. Need {amount}, have {credits.balance}"

        # Deduct credits
        credits.balance -= amount
        credits.total_spent += amount

        await self.db.commit()
        logger.info(f"Deducted {amount} credits from user {user_id} for {operation}")

        return True, f"Deducted {amount} credits for {operation}"

    async def add_credits(
        self,
        user_id: int,
        amount: int,
        reason: str,
    ) -> UserCredits:
        """Add credits to user's balance"""
        credits = await self.get_user_credits(user_id)

        if not credits:
            raise ValueError("Credits not found for user")

        credits.balance += amount
        credits.total_earned += amount

        await self.db.commit()
        await self.db.refresh(credits)

        logger.info(f"Added {amount} credits to user {user_id}: {reason}")
        return credits

    async def upgrade_subscription(
        self,
        user_id: int,
        new_tier: SubscriptionTier,
        payment_id: str,
        payment_provider: str = "stripe",
    ) -> Subscription:
        """Upgrade user's subscription tier"""
        subscription = await self.get_user_subscription(user_id)
        credits = await self.get_user_credits(user_id)

        if not subscription or not credits:
            raise ValueError("User subscription/credits not found")

        config = TIER_CONFIGS[new_tier]
        now = datetime.utcnow()
        expires_at = now + timedelta(days=config["expiry_days"])

        # Update subscription
        subscription.tier = new_tier
        subscription.started_at = now
        subscription.expires_at = expires_at
        subscription.is_active = True
        subscription.payment_id = payment_id
        subscription.payment_provider = payment_provider
        subscription.max_pages_per_story = config["max_pages"]
        subscription.max_concurrent_tasks = config["max_concurrent"]
        subscription.has_watermark = config["has_watermark"]
        subscription.storage_days = config["storage_days"]

        # Add credits
        credits.balance += config["credits"]
        credits.total_earned += config["credits"]
        credits.expires_at = expires_at

        await self.db.commit()
        await self.db.refresh(subscription)

        logger.info(f"User {user_id} upgraded to {new_tier.value}")
        return subscription

    async def check_limits(
        self,
        user_id: int,
        operation: str,
        value: int = 0,
    ) -> Tuple[bool, str]:
        """
        Check if user is within their subscription limits.

        Args:
            user_id: User ID
            operation: Type of limit check (pages, concurrent_tasks)
            value: Value to check against limit

        Returns:
            Tuple of (within_limits, message)
        """
        subscription = await self.get_user_subscription(user_id)

        if not subscription:
            return False, "Subscription not found"

        if not subscription.is_active:
            return False, "Subscription is not active"

        if subscription.expires_at and subscription.expires_at < datetime.utcnow():
            return False, "Subscription has expired"

        if operation == "pages":
            if value > subscription.max_pages_per_story:
                return False, f"Page limit exceeded. Max {subscription.max_pages_per_story} pages allowed for your plan."

        if operation == "concurrent_tasks":
            if value >= subscription.max_concurrent_tasks:
                return False, f"Concurrent task limit reached. Max {subscription.max_concurrent_tasks} tasks allowed."

        return True, "OK"

    def get_tier_config(self, tier: SubscriptionTier) -> dict:
        """Get configuration for a subscription tier"""
        return TIER_CONFIGS.get(tier, TIER_CONFIGS[SubscriptionTier.FREE])

    def get_tier_price(self, tier: SubscriptionTier) -> float:
        """Get price for a subscription tier"""
        return TIER_PRICING.get(tier, 0)

    def estimate_operation_cost(self, operation: str, **kwargs) -> int:
        """Estimate credits cost for an operation"""
        if operation == "story":
            page_count = kwargs.get("page_count", 12)
            base = settings.COST_STORY_GENERATION
            extra = max(0, page_count - 12) * 5
            return base + extra

        if operation == "illustration":
            count = kwargs.get("count", 1)
            return settings.COST_IMAGE_GENERATION * count

        if operation == "video":
            page_count = kwargs.get("page_count", 12)
            has_narration = kwargs.get("has_narration", True)
            base = settings.COST_VIDEO_GENERATION
            page_cost = page_count * 10
            narration = page_count * 5 if has_narration else 0
            return base + page_cost + narration

        if operation == "tts":
            char_count = kwargs.get("char_count", 500)
            base = settings.COST_TTS_GENERATION
            extra = max(0, char_count - 500) // 500 * 5
            return base + extra

        if operation == "chatps":
            return settings.COST_CHATPS_EDIT

        return 0
