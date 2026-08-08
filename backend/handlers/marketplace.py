"""Marketplace handler — browsing, search, categories, project cards (UZS)."""
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import async_session_maker
from services.project_service import list_projects
from keyboards.marketplace import project_card_keyboard

router = Router()


class SearchStates(StatesGroup):
    waiting_query = State()


def _fmt_price(price: int, discounted: int = 0, discount_percent: int = 0) -> str:
    if price == 0:
        return "BEPUL"
    if discount_percent > 0 and discounted > 0:
        return f"~~{int(price/100):,} som~~ -> {int(discounted/100):,} som (-{discount_percent}%)".replace(",", " ")
    return f"{int(price/100):,} som".replace(",", " ")


@router.callback_query(F.data == "market:trending")
async def trending(callback: CallbackQuery):
    async with async_session_maker() as db:
        projects = await list_projects(db, sort="popular", limit=5)
    await _send_project_list(callback, projects, "🔥 Mashhur")
    await callback.answer()


@router.callback_query(F.data == "market:new")
async def new_projects(callback: CallbackQuery):
    async with async_session_maker() as db:
        projects = await list_projects(db, sort="new", limit=5)
    await _send_project_list(callback, projects, "🆕 Yangi loyihalar")
    await callback.answer()


@router.callback_query(F.data == "market:price_low")
async def cheapest(callback: CallbackQuery):
    async with async_session_maker() as db:
        projects = await list_projects(db, sort="price_low", limit=5)
    await _send_project_list(callback, projects, "💰 Eng arzon")
    await callback.answer()


@router.callback_query(F.data == "market:rating")
async def top_rated(callback: CallbackQuery):
    async with async_session_maker() as db:
        projects = await list_projects(db, sort="rating", limit=5)
    await _send_project_list(callback, projects, "⭐ Yuqori reyting")
    await callback.answer()


@router.callback_query(F.data == "market:discount")
async def discounts(callback: CallbackQuery):
    async with async_session_maker() as db:
        projects = await list_projects(db, sort="discount", limit=5)
    await _send_project_list(callback, projects, "🏷 Chegirmali")
    await callback.answer()


@router.callback_query(F.data == "market:search")
async def search_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("🔍 Qidiruv sorovini yuboring:")
    await state.set_state(SearchStates.waiting_query)
    await callback.answer()


@router.message(SearchStates.waiting_query)
async def search_query(message: Message, state: FSMContext):
    query = message.text
    async with async_session_maker() as db:
        projects = await list_projects(db, search=query, limit=10)
    await state.clear()
    if not projects:
        await message.answer(f"{query} uchun natija topilmadi.")
        return
    await _send_project_list(message, projects, f"🔍 {query} natijalari")


@router.message(F.text == "🔍 Qidirish")
async def search_button(message: Message, state: FSMContext):
    await message.answer("🔍 Qidiruv sorovini yuboring:")
    await state.set_state(SearchStates.waiting_query)


@router.message(F.text == "📦 Kategoriyalar")
@router.callback_query(F.data == "categories:list")
async def categories_button(target, state: FSMContext = None):
    from sqlalchemy import select
    from models.category import Category
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    async with async_session_maker() as db:
        result = await db.execute(
            select(Category).where(Category.is_active == True).order_by(Category.sort_order)
        )
        cats = result.scalars().all()

    if not cats:
        send = target.message.answer if hasattr(target, "message") else target.answer
        await send("Kategoriyalar hozircha yoq.")
        return

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{c.icon or '📁'} {c.name}", callback_data=f"cat:{c.id}")]
        for c in cats
    ])
    send = target.message.answer if hasattr(target, "message") else target.answer
    await send("📦 Kategoriyalar:", reply_markup=kb)


async def _send_project_list(target, projects, title: str) -> None:
    if not projects:
        send = target.message.answer if hasattr(target, "message") else target.answer
        await send("Loyihalar topilmadi.")
        return

    send = target.message.answer if hasattr(target, "message") else target.answer
    await send(f"<b>{title}</b>\n\n{len(projects)} ta loyiha topildi:")
    for p in projects:
        price_text = _fmt_price(p.price, p.discounted_price, p.discount_percent)
        tech = p.technologies or "Korsatilmagan"
        text = (
            f"📦 <b>{p.name}</b>\n"
            f"{p.short_description}\n"
            f"💰 {price_text}  |  ⭐ {p.rating_avg} ({p.rating_count})  |  📥 {p.sales_count}\n"
            f"🛠 {tech}"
        )
        await send(text, reply_markup=project_card_keyboard(p.id, p.price))
