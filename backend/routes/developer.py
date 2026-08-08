"""Developer dashboard routes — real-time sales stats, revenue, charts."""
from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models.user import User, Role
from models.project import Project, ProjectStatus
from models.order import Order, OrderStatus
from models.review import Review
from routes.deps import get_current_user

router = APIRouter()


@router.get("/dashboard")
async def developer_dashboard(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Real-time developer dashboard: revenue, sales, project stats, recent orders."""
    if user.role not in (Role.developer, Role.admin):
        raise HTTPException(status_code=403, detail="Dasturchi huquqi kerak")

    # Total stats
    total_projects = await db.scalar(
        select(func.count(Project.id)).where(Project.developer_id == user.id)
    )
    published = await db.scalar(
        select(func.count(Project.id)).where(
            Project.developer_id == user.id,
            Project.status == ProjectStatus.published,
        )
    )
    pending = await db.scalar(
        select(func.count(Project.id)).where(
            Project.developer_id == user.id,
            Project.status == ProjectStatus.pending,
        )
    )
    draft = await db.scalar(
        select(func.count(Project.id)).where(
            Project.developer_id == user.id,
            Project.status == ProjectStatus.draft,
        )
    )

    # Sales stats
    total_sales = await db.scalar(
        select(func.count(Order.id))
        .join(Project, Order.project_id == Project.id)
        .where(Project.developer_id == user.id, Order.status == OrderStatus.completed)
    )
    total_revenue = await db.scalar(
        select(func.coalesce(func.sum(Order.amount), 0))
        .join(Project, Order.project_id == Project.id)
        .where(Project.developer_id == user.id, Order.status == OrderStatus.completed)
    )
    total_views = await db.scalar(
        select(func.coalesce(func.sum(Project.views), 0))
        .where(Project.developer_id == user.id)
    )
    avg_rating = await db.scalar(
        select(func.coalesce(func.avg(Project.rating_avg), 0))
        .where(Project.developer_id == user.id)
    )

    # Last 7 days revenue (for chart)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_revenue = await db.execute(
        select(
            func.date(Order.created_at).label("date"),
            func.sum(Order.amount).label("revenue"),
            func.count(Order.id).label("sales"),
        )
        .join(Project, Order.project_id == Project.id)
        .where(
            Project.developer_id == user.id,
            Order.status == OrderStatus.completed,
            Order.created_at >= seven_days_ago,
        )
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
    )
    daily_data = [
        {"date": str(row.date), "revenue": row.revenue or 0, "sales": row.sales or 0}
        for row in daily_revenue
    ]

    # Top projects by sales
    top_projects_result = await db.execute(
        select(Project)
        .where(Project.developer_id == user.id)
        .order_by(Project.sales_count.desc())
        .limit(5)
    )
    top_projects = [
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "sales_count": p.sales_count,
            "rating_avg": p.rating_avg,
            "status": p.status.value,
            "revenue": p.sales_count * (p.discounted_price or p.price),
        }
        for p in top_projects_result.scalars().all()
    ]

    # Recent orders
    recent_orders_result = await db.execute(
        select(Order, Project)
        .join(Project, Order.project_id == Project.id)
        .where(Project.developer_id == user.id)
        .order_by(Order.created_at.desc())
        .limit(10)
    )
    recent_orders = [
        {
            "id": o.id,
            "project_name": p.name,
            "amount": o.amount,
            "status": o.status.value,
            "created_at": o.created_at.isoformat() if o.created_at else None,
        }
        for o, p in recent_orders_result.all()
    ]

    return {
        "totals": {
            "projects": total_projects or 0,
            "published": published or 0,
            "pending": pending or 0,
            "draft": draft or 0,
            "sales": total_sales or 0,
            "revenue": total_revenue or 0,
            "views": total_views or 0,
            "avg_rating": round(float(avg_rating or 0), 2),
        },
        "daily_revenue": daily_data,
        "top_projects": top_projects,
        "recent_orders": recent_orders,
    }


@router.get("/projects")
async def developer_projects(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """List all projects by this developer with sales stats."""
    if user.role not in (Role.developer, Role.admin):
        raise HTTPException(status_code=403, detail="Dasturchi huquqi kerak")

    result = await db.execute(
        select(Project)
        .where(Project.developer_id == user.id)
        .order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()
    return {
        "items": [
            {
                "id": p.id,
                "name": p.name,
                "short_description": p.short_description,
                "price": p.price,
                "discounted_price": p.discounted_price,
                "discount_percent": p.discount_percent,
                "status": p.status.value,
                "sales_count": p.sales_count,
                "rating_avg": p.rating_avg,
                "rating_count": p.rating_count,
                "views": p.views,
                "revenue": p.sales_count * (p.discounted_price or p.price),
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in projects
        ]
    }
