"""Category routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models.category import Category
from routes.deps import require_admin

router = APIRouter()


class CategoryCreate(BaseModel):
    name: str
    slug: str
    icon: str | None = None
    description: str | None = None


@router.get("")
async def list_categories(db: AsyncSession = Depends(get_session)):
    result = await db.execute(
        select(Category).where(Category.is_active == True).order_by(Category.sort_order)
    )
    cats = result.scalars().all()
    return {
        "items": [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "icon": c.icon,
                "description": c.description,
            }
            for c in cats
        ]
    }


@router.post("")
async def create_category(
    payload: CategoryCreate,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    cat = Category(**payload.model_dump())
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return {"id": cat.id, "name": cat.name}


@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(select(Category).where(Category.id == category_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    cat.is_active = False
    await db.commit()
    return {"deleted": True}
