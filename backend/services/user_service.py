"""User service — registration, lookup, role checks, ban management."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User, Role
from utils.security import hash_password, verify_password


async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> User | None:
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_referral_code(db: AsyncSession, code: str) -> User | None:
    result = await db.execute(select(User).where(User.referral_code == code))
    return result.scalar_one_or_none()


async def create_user(
    db: AsyncSession,
    *,
    telegram_id: int | None = None,
    username: str | None = None,
    full_name: str | None = None,
    email: str | None = None,
    password: str | None = None,
    referred_by: str | None = None,
) -> User:
    """Create a new user. Generates a unique 8-char referral code."""
    import secrets

    user = User(
        telegram_id=telegram_id,
        username=username,
        full_name=full_name,
        email=email,
        password_hash=hash_password(password) if password else None,
        referral_code=secrets.token_urlsafe(6),
        referred_by=referred_by,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate(db: AsyncSession, email: str, password: str) -> User | None:
    """Return the user if email+password match, else None."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user and user.password_hash and verify_password(password, user.password_hash):
        return user
    return None


async def update_role(db: AsyncSession, user_id: str, role: Role) -> None:
    await db.execute(update(User).where(User.id == user_id).values(role=role))
    await db.commit()


async def ban_user(db: AsyncSession, user_id: str, reason: str) -> None:
    await db.execute(
        update(User).where(User.id == user_id).values(is_banned=True, ban_reason=reason)
    )
    await db.commit()


async def unban_user(db: AsyncSession, user_id: str) -> None:
    await db.execute(
        update(User).where(User.id == user_id).values(is_banned=False, ban_reason=None)
    )
    await db.commit()


async def claim_daily_bonus(db: AsyncSession, user_id: str) -> int:
    """Award 100 cents if last claim was > 24h ago. Returns the amount or 0."""
    user = await get_user_by_id(db, user_id)
    if not user:
        return 0
    now = datetime.utcnow()
    if user.daily_bonus_claimed_at and (now - user.daily_bonus_claimed_at) < timedelta(hours=24):
        return 0
    bonus = 100
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(balance=User.balance + bonus, daily_bonus_claimed_at=now)
    )
    await db.commit()
    return bonus


async def list_users(db: AsyncSession, limit: int = 50, offset: int = 0) -> Sequence[User]:
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
    )
    return result.scalars().all()
