"""Developer handler — add project, list projects, stats (UZS)."""
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import async_session_maker
from services.user_service import get_user_by_telegram_id
from services.project_service import list_projects, create_project
from models.project import ProjectStatus
from models.user import Role
from keyboards.developer import developer_panel_keyboard

router = Router()


class AddProjectStates(StatesGroup):
    name = State()
    short_description = State()
    full_description = State()
    price = State()
    technologies = State()


def _fmt_price(price: int) -> str:
    if price == 0:
        return "BEPUL"
    return f"{int(price/100):,} som".replace(",", " ")


def _fmt_balance(balance: int) -> str:
    return f"{int(balance/100):,} som".replace(",", " ")


@router.callback_query(F.data == "dev:panel")
async def dev_panel(callback: CallbackQuery):
    async with async_session_maker() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
    if not user or user.role not in (Role.developer, Role.admin):
        await callback.answer("Dasturchi huquqi kerak.", show_alert=True)
        return
    await callback.message.edit_text("🛠 <b>Dasturchi paneli</b>", reply_markup=developer_panel_keyboard())
    await callback.answer()


@router.callback_query(F.data == "dev:add")
async def dev_add_start(callback: CallbackQuery, state: FSMContext):
    async with async_session_maker() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
    if not user or user.role not in (Role.developer, Role.admin):
        await callback.answer("Dasturchi huquqi kerak.", show_alert=True)
        return
    await callback.message.answer("📝 <b>Loyiha nomini</b> yuboring:")
    await state.set_state(AddProjectStates.name)
    await callback.answer()


@router.message(AddProjectStates.name)
async def dev_add_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("📝 <b>Qisqa tavsif</b> yuboring (max 255 belgi):")
    await state.set_state(AddProjectStates.short_description)


@router.message(AddProjectStates.short_description)
async def dev_add_short(message: Message, state: FSMContext):
    await state.update_data(short_description=message.text[:255])
    await message.answer("📝 <b>To'liq tavsif</b> yuboring:")
    await state.set_state(AddProjectStates.full_description)


@router.message(AddProjectStates.full_description)
async def dev_add_full(message: Message, state: FSMContext):
    await state.update_data(full_description=message.text)
    await message.answer("💰 <b>Narx somda</b> yuboring (masalan: 50000 yoki 0 — bepul):")
    await state.set_state(AddProjectStates.price)


@router.message(AddProjectStates.price)
async def dev_add_price(message: Message, state: FSMContext):
    try:
        price = int(float(message.text) * 100)  # som -> tiyin
        if price < 0:
            raise ValueError
    except ValueError:
        await message.answer("Noto'g'ri narx. Son yuboring (masalan: 50000):")
        return
    await state.update_data(price=price)
    await message.answer("🛠 <b>Texnologiyalar</b> yuboring (vergul bilan, masalan: Python, FastAPI, React):")
    await state.set_state(AddProjectStates.technologies)


@router.message(AddProjectStates.technologies)
async def dev_add_tech(message: Message, state: FSMContext):
    await state.update_data(technologies=message.text)
    data = await state.get_data()
    await state.clear()

    async with async_session_maker() as db:
        user = await get_user_by_telegram_id(db, message.from_user.id)
        if not user:
            await message.answer("Xato: foydalanuvchi topilmadi.")
            return
        project = await create_project(
            db,
            developer_id=user.id,
            name=data["name"],
            short_description=data["short_description"],
            full_description=data["full_description"],
            price=data["price"],
            discounted_price=data["price"],
            technologies=data["technologies"],
            status=ProjectStatus.draft,
        )

    await message.answer(
        f"✅ <b>{project.name}</b> loyihasi draft sifatida yaratildi!\n\n"
        f"Fayl yuklash va nashr qilish uchun ilovani oching."
    )


@router.callback_query(F.data == "dev:projects")
async def dev_my_projects(callback: CallbackQuery):
    async with async_session_maker() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        if not user:
            await callback.answer("Foydalanuvchi topilmadi.")
            return
        from sqlalchemy import select
        from models.project import Project
        result = await db.execute(
            select(Project).where(Project.developer_id == user.id).order_by(Project.created_at.desc()).limit(10)
        )
        projects = result.scalars().all()
    if not projects:
        await callback.answer("Loyihalar yoq.", show_alert=True)
        return
    text = "📋 <b>Mening loyihalarim</b>\n\n"
    for p in projects:
        text += f"• <b>{p.name}</b> — {_fmt_price(p.price)} [{p.status.value}]\n"
    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "dev:stats")
async def dev_stats(callback: CallbackQuery):
    from sqlalchemy import select, func
    from models.project import Project
    from models.order import Order, OrderStatus
    async with async_session_maker() as db:
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        if not user:
            await callback.answer("Foydalanuvchi topilmadi.")
            return
        total = await db.scalar(select(func.count(Project.id)).where(Project.developer_id == user.id))
        sales = await db.scalar(
            select(func.count(Order.id))
            .join(Project, Order.project_id == Project.id)
            .where(Project.developer_id == user.id, Order.status == OrderStatus.completed)
        )
        revenue = await db.scalar(
            select(func.coalesce(func.sum(Order.amount), 0))
            .join(Project, Order.project_id == Project.id)
            .where(Project.developer_id == user.id, Order.status == OrderStatus.completed)
        )
    text = (
        f"📊 <b>Statistika</b>\n\n"
        f"📦 Loyihalar: {total}\n"
        f"🛒 Sotuvlar: {sales}\n"
        f"💰 Daromad: {_fmt_balance(revenue)}\n"
    )
    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(F.data == "dev:revenue")
async def dev_revenue(callback: CallbackQuery):
    await dev_stats(callback)


@router.callback_query(F.data == "dev:reviews")
async def dev_reviews(callback: CallbackQuery):
    await callback.answer("Sharhlar paneli tez orada!", show_alert=True)
