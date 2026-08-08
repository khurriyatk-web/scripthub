"""Project routes — list, detail, create, update, delete."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models.project import ProjectStatus
from models.user import Role
from routes.deps import get_current_user, require_admin
from services.project_service import (
    create_project, get_project, list_projects, update_project, delete_project,
    increment_views,
)

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str = Field(..., max_length=128)
    short_description: str = Field(..., max_length=255)
    full_description: str
    technologies: str = ""
    tags: str = ""
    price: int = 0
    discount_percent: int = 0
    version: str = "1.0.0"
    category_id: str | None = None
    github_link: str | None = None
    demo_video: str | None = None
    documentation: str | None = None
    requirements: str | None = None
    license: str = "MIT"


class ProjectUpdate(BaseModel):
    name: str | None = None
    short_description: str | None = None
    full_description: str | None = None
    technologies: str | None = None
    tags: str | None = None
    price: int | None = None
    discount_percent: int | None = None
    version: str | None = None
    category_id: str | None = None
    github_link: str | None = None
    demo_video: str | None = None
    documentation: str | None = None
    requirements: str | None = None
    license: str | None = None
    status: ProjectStatus | None = None


@router.get("")
async def projects_list(
    category_id: str | None = None,
    sort: str = Query("new", regex="^(new|popular|price_low|price_high|rating|discount)$"),
    search: str | None = None,
    limit: int = Query(20, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_session),
):
    """Public marketplace listing."""
    items = await list_projects(
        db, category_id=category_id, sort=sort, search=search, limit=limit, offset=offset
    )
    return {
        "items": [
            {
                "id": p.id,
                "name": p.name,
                "short_description": p.short_description,
                "price": p.price,
                "discount_percent": p.discount_percent,
                "discounted_price": p.discounted_price,
                "rating_avg": p.rating_avg,
                "rating_count": p.rating_count,
                "sales_count": p.sales_count,
                "technologies": p.technologies,
                "tags": p.tags,
                "version": p.version,
                "is_featured": p.is_featured,
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "developer": {"id": p.developer_id},
                "category_id": p.category_id,
            }
            for p in items
        ]
    }


@router.get("/{project_id}")
async def project_detail(project_id: str, db: AsyncSession = Depends(get_session)):
    p = await get_project(db, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    await increment_views(db, project_id)
    return {
        "id": p.id,
        "name": p.name,
        "short_description": p.short_description,
        "full_description": p.full_description,
        "technologies": p.technologies,
        "tags": p.tags,
        "price": p.price,
        "discount_percent": p.discount_percent,
        "discounted_price": p.discounted_price,
        "version": p.version,
        "requirements": p.requirements,
        "license": p.license,
        "documentation": p.documentation,
        "github_link": p.github_link,
        "demo_video": p.demo_video,
        "demo_images": p.demo_images,
        "views": p.views,
        "sales_count": p.sales_count,
        "rating_avg": p.rating_avg,
        "rating_count": p.rating_count,
        "status": p.status.value,
        "developer_id": p.developer_id,
        "category_id": p.category_id,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


@router.post("")
async def create_new_project(
    payload: ProjectCreate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Developer creates a new project (starts as draft)."""
    if user.role not in (Role.developer, Role.admin, Role.moderator):
        raise HTTPException(status_code=403, detail="Developer account required")
    discounted = int(payload.price * (1 - payload.discount_percent / 100))
    p = await create_project(
        db,
        developer_id=user.id,
        status=ProjectStatus.draft,
        discounted_price=discounted,
        **payload.model_dump(),
    )
    return {"id": p.id, "status": p.status.value}


@router.put("/{project_id}")
async def edit_project(
    project_id: str,
    payload: ProjectUpdate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    p = await get_project(db, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    if p.developer_id != user.id and user.role not in (Role.admin, Role.moderator):
        raise HTTPException(status_code=403, detail="Not your project")
    data = payload.model_dump(exclude_none=True)
    if "discount_percent" in data or "price" in data:
        price = data.get("price", p.price)
        disc = data.get("discount_percent", p.discount_percent)
        data["discounted_price"] = int(price * (1 - disc / 100))
    updated = await update_project(db, project_id, **data)
    return {"id": updated.id, "status": updated.status.value}


@router.delete("/{project_id}")
async def remove_project(
    project_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    p = await get_project(db, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    if p.developer_id != user.id and user.role not in (Role.admin, Role.moderator):
        raise HTTPException(status_code=403, detail="Not your project")
    await delete_project(db, project_id)
    return {"deleted": True}
