"""Project service — CRUD, search, filtering, sorting."""
from __future__ import annotations

from typing import Sequence

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from models.project import Project, ProjectStatus


async def create_project(db: AsyncSession, **kwargs) -> Project:
    project = Project(**kwargs)
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def get_project(db: AsyncSession, project_id: str) -> Project | None:
    result = await db.execute(select(Project).where(Project.id == project_id))
    return result.scalar_one_or_none()


async def list_projects(
    db: AsyncSession,
    *,
    category_id: str | None = None,
    status: ProjectStatus = ProjectStatus.published,
    sort: str = "new",
    search: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> Sequence[Project]:
    """Fetch projects with optional filtering, searching, and sorting."""
    q = select(Project).where(Project.status == status)

    if category_id:
        q = q.where(Project.category_id == category_id)

    if search:
        pattern = f"%{search}%"
        q = q.where(
            or_(
                Project.name.ilike(pattern),
                Project.short_description.ilike(pattern),
                Project.tags.ilike(pattern),
                Project.technologies.ilike(pattern),
            )
        )

    sort_map = {
        "new": Project.created_at.desc(),
        "popular": Project.sales_count.desc(),
        "price_low": Project.price.asc(),
        "price_high": Project.price.desc(),
        "rating": Project.rating_avg.desc(),
        "discount": Project.discount_percent.desc(),
    }
    q = q.order_by(sort_map.get(sort, Project.created_at.desc()))

    q = q.limit(limit).offset(offset)
    result = await db.execute(q)
    return result.scalars().all()


async def count_projects(db: AsyncSession, status: ProjectStatus = ProjectStatus.published) -> int:
    result = await db.execute(
        select(func.count(Project.id)).where(Project.status == status)
    )
    return result.scalar_one()


async def increment_views(db: AsyncSession, project_id: str) -> None:
    await db.execute(
        Project.__table__.update()
        .where(Project.id == project_id)
        .values(views=Project.views + 1)
    )
    await db.commit()


async def update_project(db: AsyncSession, project_id: str, **kwargs) -> Project | None:
    project = await get_project(db, project_id)
    if not project:
        return None
    for key, value in kwargs.items():
        setattr(project, key, value)
    await db.commit()
    await db.refresh(project)
    return project


async def delete_project(db: AsyncSession, project_id: str) -> bool:
    project = await get_project(db, project_id)
    if not project:
        return False
    await db.delete(project)
    await db.commit()
    return True
