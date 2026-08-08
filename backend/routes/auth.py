"""Auth routes — Telegram login, email/password register + login, JWT issuance."""
from __future__ import annotations

import hashlib
import hmac
import json
from urllib.parse import unquote, parse_qsl

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from database import get_session
from models.user import User, Role
from services.user_service import get_user_by_telegram_id, create_user, get_user_by_email, authenticate
from utils.security import create_access_token

router = APIRouter()


class TelegramLogin(BaseModel):
    init_data: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""


class DevLogin(BaseModel):
    email: str
    password: str


def _validate_init_data(init_data: str) -> dict | None:
    try:
        parsed = dict(parse_qsl(init_data))
    except Exception:
        return None

    hash_val = parsed.pop("hash", None)
    if not hash_val:
        return None

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))

    secret_key = hmac.new(
        b"WebAppData", settings.bot_token.encode(), hashlib.sha256
    ).digest()

    computed = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(computed, hash_val):
        return None

    user_json = parsed.get("user")
    if not user_json:
        return None
    return json.loads(unquote(user_json))


@router.post("/telegram")
async def telegram_login(payload: TelegramLogin, db: AsyncSession = Depends(get_session)):
    tg_user = _validate_init_data(payload.init_data)
    if not tg_user:
        raise HTTPException(status_code=401, detail="Invalid Telegram data")

    tg_id = tg_user.get("id")
    user = await get_user_by_telegram_id(db, tg_id)

    if not user:
        user = await create_user(
            db,
            telegram_id=tg_id,
            username=tg_user.get("username"),
            full_name=tg_user.get("first_name", "") + " " + tg_user.get("last_name", ""),
        )

    if user.is_banned:
        raise HTTPException(status_code=403, detail="Hisobingiz bloklangan")

    token = create_access_token(user.id, {"role": user.role.value, "tg_id": tg_id})
    return {
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role.value,
            "balance": user.balance,
            "is_verified_developer": user.is_verified_developer,
            "email": user.email,
            "referral_code": user.referral_code,
        },
    }


@router.post("/register")
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_session)):
    """Email/password registration for web users."""
    existing = await get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(status_code=409, detail="Bu email allaqachon ro'yxatdan o'tgan")

    user = await create_user(
        db,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
    )

    token = create_access_token(user.id, {"role": user.role.value})
    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "balance": user.balance,
            "is_verified_developer": user.is_verified_developer,
            "referral_code": user.referral_code,
        },
    }


@router.post("/login")
async def dev_login(payload: DevLogin, db: AsyncSession = Depends(get_session)):
    """Email/password login."""
    user = await authenticate(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Email yoki parol noto'g'ri")
    if user.is_banned:
        raise HTTPException(status_code=403, detail="Hisobingiz bloklangan")
    token = create_access_token(user.id, {"role": user.role.value})
    return {
        "token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "balance": user.balance,
            "is_verified_developer": user.is_verified_developer,
            "referral_code": user.referral_code,
        },
    }


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    """Return current user info from JWT token."""
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "username": user.username,
            "role": user.role.value,
            "balance": user.balance,
            "is_verified_developer": user.is_verified_developer,
            "referral_code": user.referral_code,
            "telegram_id": user.telegram_id,
        },
    }
