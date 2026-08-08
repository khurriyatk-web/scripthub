"""Shared FastAPI dependencies: current-user extraction from JWT."""
from __future__ import annotations

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models.user import User, Role
from services.user_service import get_user_by_id
from utils.security import decode_token


async def get_current_user(
    authorization: str = Header(...),
    db: AsyncSession = Depends(get_session),
) -> User:
    """Extract and verify the Bearer JWT, returning the User or 401."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user_id = payload.get("sub")
    user = await get_user_by_id(db, user_id)
    if not user or user.is_banned:
        raise HTTPException(status_code=403, detail="User not found or banned")
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """Dependency that only allows admin / moderator roles."""
    if user.role not in (Role.admin, Role.moderator):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
