"""Start handler — /start, /help, deep-linking, referral."""
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery

from config.settings import settings
from database import async_session_maker
from services.user_service import get_user_by_telegram_id, create_user, get_user_by_referral_code
from keyboards.main import main_menu_keyboard, mini_app_keyboard

router = Router()


@router.message(CommandStart(deep_link=True))
async def start_with_referral(message: Message, command):
    ref_code = command.args.replace("ref_", "") if command.args else None
    await _register_or_welcome(message, ref_code)


@router.message(CommandStart())
async def start(message: Message):
    await _register_or_welcome(message, None)


@router.message(Command("help"))
async def help_cmd(message: Message):
    text = (
        "<b>ScriptHub — Manba kod bozori</b>\n\n"
        "Buyruqlar:\n"
        "/start — Botni boshlash\n"
        "/help — Yordam\n"
        "/menu — Bosh menyu\n\n"
        "Pastdagi tugmalar orqali bozorni ko'ring."
    )
    await message.answer(text, reply_markup=main_menu_keyboard())


async def _register_or_welcome(message: Message, ref_code: str | None) -> None:
    tg_id = message.from_user.id
    async with async_session_maker() as db:
        user = await get_user_by_telegram_id(db, tg_id)
        if not user:
            referred_by = None
            if ref_code:
                referrer = await get_user_by_referral_code(db, ref_code)
                if referrer:
                    referred_by = referrer.id
            user = await create_user(
                db,
                telegram_id=tg_id,
                username=message.from_user.username,
                full_name=message.from_user.full_name,
                referred_by=referred_by,
            )

    if user.is_banned:
        await message.answer("⛔ Hisobingiz bloklangan.")
        return

    name = message.from_user.full_name or "do'st"
    text = (
        f"👋 Xush kelibsiz, <b>{name}</b>!\n\n"
        "🛍 <b>ScriptHub</b> — manba kodni xavfsiz sotib oling va soting.\n\n"
        "Pastdagi tugmalar orqali bozorni ko'ring."
    )

    await message.answer(text, reply_markup=main_menu_keyboard())
    await message.answer("📱 To'liq bozorni ochish uchun bosing:", reply_markup=mini_app_keyboard(settings.frontend_url))
