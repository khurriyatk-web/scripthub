"""Review routes — list, create, update, delete."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models.review import Review
from models.project import Project
from routes.deps import get_current_user

router = APIRouter()


class ReviewCreate(BaseModel):
    project_id: str
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None


class ReviewUpdate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = None


@router.get("/{project_id}")
async def list_reviews(project_id: str, db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(Review).where(Review.project_id == project_id).order_by(Review.created_at.desc())
    )
    reviews = result.scalars().all()
    return {
        "items": [
            {
                "id": r.id,
                "user_id": r.user_id,
                "rating": r.rating,
                "comment": r.comment,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in reviews
        ]
    }


@router.post("")
async def create_review(
    payload: ReviewCreate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    # Check for existing review
    existing = await db.execute(
        select(Review).where(Review.user_id == user.id, Review.project_id == payload.project_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="You already reviewed this project")

    review = Review(
        user_id=user.id,
        project_id=payload.project_id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    await db.flush()

    # Update project rating
    stats = await db.execute(
        select(func.avg(Review.rating), func.count(Review.id))
        .where(Review.project_id == payload.project_id)
    )
    avg, count = stats.one()
    project = await db.execute(select(Project).where(Project.id == payload.project_id))
    proj = project.scalar_one_or_none()
    if proj:
        proj.rating_avg = round(float(avg), 2) if avg else 0.0
        proj.rating_count = int(count) if count else 0
    await db.commit()
    await db.refresh(review)
    return {"id": review.id, "rating": review.rating}


@router.put("/{review_id}")
async def update_review(
    review_id: str,
    payload: ReviewUpdate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your review")
    review.rating = payload.rating
    review.comment = payload.comment
    await db.commit()
    return {"id": review.id}


@router.delete("/{review_id}")
async def delete_review(
    review_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if review.user_id != user.id and user.role.value not in ("admin", "moderator"):
        raise HTTPException(status_code=403, detail="Cannot delete this review")
    await db.delete(review)
    await db.commit()
    return {"deleted": True}
