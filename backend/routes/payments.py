"""Payment routes — card payment with buyer card info, checkout."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models.order import Order, OrderStatus
from models.payment import Payment, PaymentMethod, PaymentStatus
from models.project import Project, ProjectStatus
from models.download import Download
from routes.deps import get_current_user
from routes.store import get_or_create_settings

router = APIRouter()


class CardCheckout(BaseModel):
    order_id: str
    buyer_card_number: str  # buyer's card (masked, last 4 used)
    buyer_card_holder: str  # buyer's card holder name


@router.post("/card")
async def card_payment(
    payload: CardCheckout,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Manual card payment: buyer enters their card number + holder name.

    The buyer transfers money to the merchant's card (shown in store settings),
    then enters their own card info as proof. Admin confirms manually.
    """
    result = await db.execute(select(Order).where(Order.id == payload.order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your order")
    if order.status == OrderStatus.completed:
        raise HTTPException(status_code=400, detail="Already paid")

    # Mask card number (keep only last 4 digits)
    masked = "*" * max(len(payload.buyer_card_number) - 4, 0) + payload.buyer_card_number[-4:]

    payment = Payment(
        order_id=order.id,
        method=PaymentMethod.card,
        status=PaymentStatus.pending,
        amount=order.amount,
        currency="UZS",
        provider="manual",
        provider_payment_id=f"card:{masked}:{payload.buyer_card_holder}",
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)

    return {
        "payment_id": payment.id,
        "status": "pending",
        "amount": order.amount,
        "currency": "UZS",
        "message": "To'lov qabul qilindi. Admin tasdiqlashini kuting.",
    }


@router.get("/merchant-card")
async def merchant_card_info(
    db: AsyncSession = Depends(get_session),
):
    """Return the merchant card info for the buyer to transfer money to."""
    s = await get_or_create_settings(db)
    if not s.merchant_card_number:
        return {
            "merchant_card_number": "",
            "merchant_card_holder": "",
            "merchant_bank": "",
            "merchant_phone": "",
            "message": "Do'kon sozlanmalarida karta ma'lumotlari kiritilmagan.",
        }
    return {
        "merchant_card_number": s.merchant_card_number,
        "merchant_card_holder": s.merchant_card_holder,
        "merchant_bank": s.merchant_bank,
        "merchant_phone": s.merchant_phone,
    }


@router.post("/confirm/{payment_id}")
async def confirm_payment(
    payment_id: str,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Admin confirms a manual card payment — completes the order."""
    if user.role.value not in ("admin", "moderator"):
        raise HTTPException(status_code=403, detail="Admin access required")

    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status != PaymentStatus.pending:
        raise HTTPException(status_code=400, detail="Payment already processed")

    payment.status = PaymentStatus.succeeded
    payment.raw_response = f"Confirmed by admin {user.id} at {datetime.utcnow()}"

    # Complete the order
    order_result = await db.execute(select(Order).where(Order.id == payment.order_id))
    order = order_result.scalar_one_or_none()
    if order:
        order.status = OrderStatus.completed
        order.paid_at = datetime.utcnow()

        # Increment sales count
        proj_result = await db.execute(select(Project).where(Project.id == order.project_id))
        project = proj_result.scalar_one_or_none()
        if project:
            project.sales_count += 1

        # Create download record
        existing_dl = await db.execute(
            select(Download).where(
                Download.user_id == order.user_id,
                Download.project_id == order.project_id,
            )
        )
        if not existing_dl.scalar_one_or_none():
            db.add(Download(user_id=order.user_id, project_id=order.project_id))

    await db.commit()
    return {"status": "completed", "order_id": order.id if order else None}
