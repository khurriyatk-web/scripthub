"""User routes — profile, favorites, downloads, daily bonus."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models.favorite import Favorite
from models.download import Download
from routes.deps import get_current_user
from services.user_service import claim_daily_bonus

router = APIRouter()


class ProfileUpdate(BaseModel):
    full_name: str | None = None
    bio: str | None = None
    email: str | None = None
    preferred_language: str | None = None


@router.get("/me")
async def my_profile(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "username": user.username,
        "full_name": user.full_name,
        "email": user.email,
        "role": user.role.value,
        "balance": user.balance,
        "is_verified_developer": user.is_verified_developer,
        "bio": user.bio,
        "avatar_path": user.avatar_path,
        "referral_code": user.referral_code,
        "preferred_language": user.preferred_language,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


@router.put("/me")
async def update_profile(
    payload: ProfileUpdate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    data = payload.model_dump(exclude_none=True)
    for key, value in data.items():
        setattr(user, value)
    await db.commit()
    return {"updated": True}


@router.post("/daily-bonus")
async def daily_bonus(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    amount = await claim_daily_bonus(db, user.id)
    if amount == 0:
        raise HTTPException(status_code=429, detail="Already claimed today")
    return {"bonus": amount, "balance": user.balance + amount}


@router.get("/favorites")
async def list_favorites(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(Favorite).where(Favorite.user_id == user.id).order_by(Favorite.created_at.desc())
    )
    favs = result.scalars().all()
    return {
        "items": [
            {"project_id": f.project_id, "created_at": f.created_at.isoformat() if f.created_at else None}
            for f in favs
        ]
    }


@router.post("/favorites/{project_id}")
async def add_favorite(
    project_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    existing = await db.execute(
        select(Favorite).where(Favorite.user_id == user.id, Favorite.project_id == project_id)
    )
    if existing.scalar_one_or_none():
        return {"favorited": True}
    fav = Favorite(user_id=user.id, project_id=project_id)
    db.add(fav)
    await db.commit()
    return {"favorited": True}


@router.delete("/favorites/{project_id}")
async def remove_favorite(
    project_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    await db.execute(
        delete(Favorite).where(Favorite.user_id == user.id, Favorite.project_id == project_id)
    )
    await db.commit()
    return {"favorited": False}


@router.get("/downloads")
async def my_downloads(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(Download).where(Download.user_id == user.id).order_by(Download.created_at.desc())
    )
    downloads = result.scalars().all()
    return {
        "items": [
            {
                "project_id": d.project_id,
                "created_at": d.created_at.isoformat() if d.created_at else None,
            }
            for d in downloads
        ]
    }
