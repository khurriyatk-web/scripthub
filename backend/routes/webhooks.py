"""Webhook routes — payment callbacks and Telegram bot webhook (optional)."""
from __future__ import annotations

from fastapi import APIRouter, Request, HTTPException

from config.settings import settings

router = APIRouter()


@router.post("/payment")
async def payment_webhook(request: Request):
    """Receive payment provider callbacks (e.g. Click, Payme, Stripe).

    Implement provider-specific signature verification here.
    """
    body = await request.body()
    # TODO: verify signature, update order + payment status
    return {"received": True}


@router.post("/telegram/{token}")
async def telegram_webhook(token: str, request: Request):
    """Telegram bot webhook endpoint (alternative to polling).

    Only active if BOT_TOKEN matches and webhook mode is configured.
    """
    if token != settings.bot_token:
        raise HTTPException(status_code=403, detail="Invalid token")
    from bot import process_update
    update_data = await request.json()
    await process_update(update_data)
    return {"ok": True}
