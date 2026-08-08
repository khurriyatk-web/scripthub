"""Seed service — creates default categories and an admin user on first run."""
from __future__ import annotations

import logging
import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from database import async_session_maker
from models.user import User, Role
from models.category import Category
from models.store_settings import StoreSettings

logger = logging.getLogger("scripthub.seed")

DEFAULT_CATEGORIES = [
    ("Web", "web", "🌐", "Web applications & sites"),
    ("Mobile", "mobile", "📱", "Mobile apps"),
    ("Backend", "backend", "⚙️", "Backend & API services"),
    ("Bots", "bots", "🤖", "Telegram & Discord bots"),
    ("Scripts", "scripts", "📜", "Automation scripts"),
    ("Templates", "templates", "🎨", "UI templates & themes"),
    ("Courses", "courses", "📚", "Educational materials"),
    ("Tools", "tools", "🔧", "Developer tools & utilities"),
]


async def seed_defaults() -> None:
    """Create default categories and admin account if they don't exist."""
    async with async_session_maker() as db:
        # Admin user
        result = await db.execute(select(User).where(User.role == Role.admin).limit(1))
        if not result.scalar_one_or_none():
            admin = User(
                email="admin@scripthub.uz",
                password_hash="$2b$12$placeholder",  # set via setup.sh or manually
                role=Role.admin,
                full_name="Administrator",
                referral_code=secrets.token_urlsafe(6),
            )
            db.add(admin)
            logger.info("Created default admin user (admin@scripthub.uz)")

        # Categories
        for name, slug, icon, desc in DEFAULT_CATEGORIES:
            result = await db.execute(select(Category).where(Category.slug == slug))
            if not result.scalar_one_or_none():
                db.add(Category(name=name, slug=slug, icon=icon, description=desc))
                logger.info(f"Created category: {name}")

        # Store settings (default)
        result = await db.execute(select(StoreSettings).limit(1))
        if not result.scalar_one_or_none():
            db.add(StoreSettings(
                store_name="ScriptHub",
                store_description="Manba kod bozori",
                currency="UZS",
            ))
            logger.info("Created default store settings")

        await db.commit()
