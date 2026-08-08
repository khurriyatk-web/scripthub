"""Admin panel routes — product approval, rejection, archive, pending payments."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models.user import User, Role
from models.project import Project, ProjectStatus
from models.order import Order, OrderStatus
from models.payment import Payment, PaymentStatus
from routes.deps import require_admin

router = APIRouter()


@router.get("/pending-payments")
async def pending_payments(
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    """List all pending card payments awaiting admin confirmation."""
    result = await db.execute(
        select(Payment, Order, Project)
        .join(Order, Payment.order_id == Order.id)
        .join(Project, Order.project_id == Project.id)
        .where(Payment.status == PaymentStatus.pending)
        .order_by(Payment.created_at.desc())
    )
    rows = result.all()
    return {
        "items": [
            {
                "payment_id": p.id,
                "order_id": o.id,
                "amount": o.amount,
                "project_name": proj.name,
                "buyer_id": o.user_id,
                "buyer_card": p.provider_payment_id or "",
                "status": p.status.value,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p, o, proj in rows
        ]
    }


@router.post("/payments/{payment_id}/confirm")
async def confirm_payment(
    payment_id: str,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    """Confirm a pending payment — completes the order."""
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status != PaymentStatus.pending:
        raise HTTPException(status_code=400, detail="Payment already processed")

    from datetime import datetime
    payment.status = PaymentStatus.succeeded
    payment.raw_response = f"Confirmed by admin {admin.id} at {datetime.utcnow()}"

    order_result = await db.execute(select(Order).where(Order.id == payment.order_id))
    order = order_result.scalar_one_or_none()
    if order:
        order.status = OrderStatus.completed
        order.paid_at = datetime.utcnow()

        proj_result = await db.execute(select(Project).where(Project.id == order.project_id))
        project = proj_result.scalar_one_or_none()
        if project:
            project.sales_count += 1

        from models.download import Download
        existing = await db.execute(
            select(Download).where(
                Download.user_id == order.user_id,
                Download.project_id == order.project_id,
            )
        )
        if not existing.scalar_one_or_none():
            db.add(Download(user_id=order.user_id, project_id=order.project_id))

    await db.commit()
    return {"status": "completed", "order_id": order.id if order else None}


@router.post("/payments/{payment_id}/reject")
async def reject_payment(
    payment_id: str,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    """Reject a pending payment."""
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status != PaymentStatus.pending:
        raise HTTPException(status_code=400, detail="Payment already processed")

    from datetime import datetime
    payment.status = PaymentStatus.failed
    payment.raw_response = f"Rejected by admin {admin.id} at {datetime.utcnow()}"

    order_result = await db.execute(select(Order).where(Order.id == payment.order_id))
    order = order_result.scalar_one_or_none()
    if order:
        order.status = OrderStatus.failed

    await db.commit()
    return {"status": "rejected"}


@router.get("/pending-projects")
async def pending_projects(
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    """List projects awaiting approval."""
    result = await db.execute(
        select(Project).where(Project.status == ProjectStatus.pending).order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()
    return {
        "items": [
            {
                "id": p.id,
                "name": p.name,
                "short_description": p.short_description,
                "price": p.price,
                "developer_id": p.developer_id,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in projects
        ]
    }


@router.post("/projects/{project_id}/approve")
async def approve_project(
    project_id: str,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    """Approve a pending project — publish it."""
    await db.execute(
        update(Project).where(Project.id == project_id).values(status=ProjectStatus.published)
    )
    await db.commit()
    return {"status": "published"}


@router.post("/projects/{project_id}/reject")
async def reject_project(
    project_id: str,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    """Reject a pending project."""
    await db.execute(
        update(Project).where(Project.id == project_id).values(status=ProjectStatus.rejected)
    )
    await db.commit()
    return {"status": "rejected"}


@router.post("/projects/{project_id}/archive")
async def archive_project(
    project_id: str,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    """Archive a project (soft delete)."""
    await db.execute(
        update(Project).where(Project.id == project_id).values(status=ProjectStatus.archived)
    )
    await db.commit()
    return {"status": "archived"}


@router.post("/projects/{project_id}/restore")
async def restore_project(
    project_id: str,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    """Restore an archived project back to published."""
    await db.execute(
        update(Project).where(Project.id == project_id).values(status=ProjectStatus.published)
    )
    await db.commit()
    return {"status": "published"}


@router.get("/archived-projects")
async def archived_projects(
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    """List archived projects."""
    result = await db.execute(
        select(Project).where(Project.status == ProjectStatus.archived).order_by(Project.created_at.desc())
    )
    projects = result.scalars().all()
    return {
        "items": [
            {
                "id": p.id,
                "name": p.name,
                "short_description": p.short_description,
                "price": p.price,
                "developer_id": p.developer_id,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in projects
        ]
    }
