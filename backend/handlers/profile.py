"""Profile handler — balance, downloads, favorites, referral, daily bonus (UZS)."""
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from config.settings import settings
from database import async_session_maker
from services.user_service import get_user_by_telegram_id, claim_daily_bonus
from keyboards.profile import profile_keyboard

router = Router()


def _fmt_balance(balance: int) -> str:
    return f"{int(balance/100):,} som".replace(",", " ")


@router.callback_query(F.data == "profile:me")
async def profile_me(callback: CallbackQuery):
    async with async_session_maker() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
    if not user:
        await callback.answer("Foydalanuvchi topilmadi. /start yuboring.")
        return
    verified = "Ha" if user.is_verified_developer else "Yoq"
    text = (
        f"👤 <b>{user.full_name or 'Foydalanuvchi'}</b>\n\n"
        f"💰 Balans: {_fmt_balance(user.balance)}\n"
        f"⭐ Tasdiqlangan: {verified}\n"
        f"🔗 Referral kod: <code>{user.referral_code}</code>\n"
        f"👥 Rol: {user.role.value}\n"
    )
    await callback.message.edit_text(text, reply_markup=profile_keyboard(is_developer=user.role.value == "developer"))
    await callback.answer()


@router.callback_query(F.data == "profile:balance")
async def profile_balance(callback: CallbackQuery):
    async with async_session_maker() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
    if user:
        await callback.answer(f"Balans: {_fmt_balance(user.balance)}", show_alert=True)
    else:
        await callback.answer("Foydalanuvchi topilmadi.")


@router.callback_query(F.data == "profile:bonus")
async def daily_bonus(callback: CallbackQuery):
    async with async_session_maker() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        if not user:
            await callback.answer("Foydalanuvchi topilmadi.")
            return
        amount = await claim_daily_bonus(db, user.id)
    if amount > 0:
        await callback.answer(f"🎁 Sizga {_fmt_balance(amount)} oldingiz!", show_alert=True)
    else:
        await callback.answer("Bugungi bonusni allaqachon oldingiz.", show_alert=True)


@router.callback_query(F.data == "profile:referral")
async def referral_link(callback: CallbackQuery):
    async with async_session_maker() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
    if not user:
        await callback.answer("Foydalanuvchi topilmadi.")
        return
    link = f"https://t.me/{settings.bot_username}?start=ref_{user.referral_code}"
    await callback.message.answer(f"🔗 Sizning referral havolangiz:\n<code>{link}</code>")
    await callback.answer()


@router.callback_query(F.data == "profile:downloads")
async def profile_downloads(callback: CallbackQuery):
    from sqlalchemy import select
    from models.download import Download
    async with async_session_maker() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        if not user:
            await callback.answer("Foydalanuvchi topilmadi.")
            return
        result = await db.execute(
            select(Download).where(Download.user_id == user.id).order_by(Download.created_at.desc()).limit(10)
        )
        downloads = result.scalars().all()
    if not downloads:
        await callback.answer("Yuklamalar yoq.", show_alert=True)
        return
    text = "📥 <b>Yuklamalar</b>\n\n"
    for d in downloads:
        text += f"• Loyiha: <code>{d.project_id[:8]}</code> — {d.created_at.strftime('%Y-%m-%d')}\n"
    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "profile:favorites")
async def profile_favorites(callback: CallbackQuery):
    from sqlalchemy import select
    from models.favorite import Favorite
    async with async_session_maker() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        if not user:
            await callback.answer("Foydalanuvchi topilmadi.")
            return
        result = await db.execute(
            select(Favorite).where(Favorite.user_id == user.id).order_by(Favorite.created_at.desc()).limit(10)
        )
        favs = result.scalars().all()
    if not favs:
        await callback.answer("Sevimlilar yoq.", show_alert=True)
        return
    text = "❤️ <b>Sevimlilar</b>\n\n"
    for f in favs:
        text += f"• <code>{f.project_id[:8]}</code>\n"
    await callback.message.answer(text)
    await callback.answer()
