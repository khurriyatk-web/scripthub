"""Order routes — create, list, checkout."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models.order import Order, OrderStatus
from models.project import Project, ProjectStatus
from routes.deps import get_current_user
from services.project_service import get_project

router = APIRouter()


class OrderCreate(BaseModel):
    project_id: str
    promo_code: str | None = None


@router.post("")
async def create_order(
    payload: OrderCreate,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Create an order for a project.  Free projects auto-complete."""
    project = await get_project(db, payload.project_id)
    if not project or project.status != ProjectStatus.published:
        raise HTTPException(status_code=404, detail="Project not available")

    # Check if already purchased
    existing = await db.execute(
        select(Order).where(
            Order.user_id == user.id,
            Order.project_id == project.id,
            Order.status.in_([OrderStatus.paid, OrderStatus.completed]),
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already purchased")

    amount = project.discounted_price or project.price

    # Apply promo code if provided
    promo_id = None
    if payload.promo_code:
        from models.promo_code import PromoCode
        result = await db.execute(
            select(PromoCode).where(
                PromoCode.code == payload.promo_code,
                PromoCode.is_active == True,
            )
        )
        promo = result.scalar_one_or_none()
        if promo and (promo.max_uses == 0 or promo.used_count < promo.max_uses):
            amount = int(amount * (1 - promo.discount_percent / 100))
            promo_id = promo.id
            promo.used_count += 1

    order = Order(
        user_id=user.id,
        project_id=project.id,
        amount=amount,
        status=OrderStatus.completed if amount == 0 else OrderStatus.pending,
        promo_code_id=promo_id,
        paid_at=datetime.utcnow() if amount == 0 else None,
    )
    db.add(order)
    if amount == 0:
        project.sales_count += 1
    await db.commit()
    await db.refresh(order)
    return {"id": order.id, "status": order.status.value, "amount": order.amount}


@router.get("")
async def my_orders(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(
        select(Order).where(Order.user_id == user.id).order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()
    return {
        "items": [
            {
                "id": o.id,
                "project_id": o.project_id,
                "amount": o.amount,
                "status": o.status.value,
                "created_at": o.created_at.isoformat() if o.created_at else None,
            }
            for o in orders
        ]
    }


@router.get("/{order_id}")
async def order_detail(
    order_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != user.id and user.role.value not in ("admin", "moderator"):
        raise HTTPException(status_code=403, detail="Not your order")
    return {
        "id": order.id,
        "project_id": order.project_id,
        "amount": order.amount,
        "status": order.status.value,
        "created_at": order.created_at.isoformat() if order.created_at else None,
        "paid_at": order.paid_at.isoformat() if order.paid_at else None,
    }
