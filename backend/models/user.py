"""User model — the core account entity.

Roles: ``user``, ``developer``, ``moderator``, ``admin``.
"""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Enum, DateTime, Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Role(str, enum.Enum):
    user = "user"
    developer = "developer"
    moderator = "moderator"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_id: Mapped[int | None] = mapped_column(Integer, unique=True, index=True, nullable=True)
    username: Mapped[str | None] = mapped_column(String(64), index=True, nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.user, nullable=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    ban_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    warnings: Mapped[int] = mapped_column(Integer, default=0)
    is_verified_developer: Mapped[bool] = mapped_column(Boolean, default=False)
    balance: Mapped[int] = mapped_column(Integer, default=0)  # in cents
    avatar_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferred_language: Mapped[str] = mapped_column(String(8), default="uz")
    referral_code: Mapped[str] = mapped_column(String(16), unique=True, index=True)
    referred_by: Mapped[str | None] = mapped_column(String(36), nullable=True)
    daily_bonus_claimed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    projects: Mapped[list["Project"]] = relationship("Project", back_populates="developer")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="user")
    favorites: Mapped[list["Favorite"]] = relationship("Favorite", back_populates="user")

    def __repr__(self) -> str:
        return f"<User {self.username or self.id} role={self.role}>"
