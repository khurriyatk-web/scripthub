"""Store settings routes — merchant card config, store info."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models.store_settings import StoreSettings
from routes.deps import require_admin

router = APIRouter()


class StoreSettingsUpdate(BaseModel):
    merchant_card_number: str | None = None
    merchant_card_holder: str | None = None
    merchant_bank: str | None = None
    merchant_phone: str | None = None
    store_name: str | None = None
    store_description: str | None = None
    support_username: str | None = None


async def get_or_create_settings(db: AsyncSession) -> StoreSettings:
    result = await db.execute(select(StoreSettings).limit(1))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = StoreSettings()
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.get("")
async def get_store_settings(db: AsyncSession = Depends(get_session)):
    """Public store settings — shown to buyers at checkout."""
    s = await get_or_create_settings(db)
    return {
        "store_name": s.store_name,
        "store_description": s.store_description,
        "currency": s.currency,
        "merchant_card_number": s.merchant_card_number,
        "merchant_card_holder": s.merchant_card_holder,
        "merchant_bank": s.merchant_bank,
        "merchant_phone": s.merchant_phone,
        "support_username": s.support_username,
    }


@router.put("")
async def update_store_settings(
    payload: StoreSettingsUpdate,
    admin=Depends(require_admin),
    db: AsyncSession = Depends(get_session),
):
    s = await get_or_create_settings(db)
    data = payload.model_dump(exclude_none=True)
    for key, value in data.items():
        setattr(s, key, value)
    await db.commit()
    return {"updated": True}
