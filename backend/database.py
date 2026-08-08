"""Async SQLAlchemy engine, session factory, and declarative base.

The engine is created once at import time.  `async_session_maker` is the
factory used by every service / route that needs a DB session.  `Base` is
the declarative base all models inherit from.

Switching to PostgreSQL later is a one-line change to DATABASE_URL in .env.
"""
from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config.settings import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    future=True,
)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


async def init_db() -> None:
    """Create all tables.  Called once on startup."""
    # Import models so they register with Base.metadata
    import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """FastAPI dependency: yields an async DB session."""
    async with async_session_maker() as session:
        yield session
