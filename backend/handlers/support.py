"""Support handler — ticket creation and FAQ (Uzbek)."""
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import async_session_maker
from models.support_ticket import SupportTicket, TicketStatus
from services.user_service import get_user_by_telegram_id

router = Router()


class SupportStates(StatesGroup):
    subject = State()
    message = State()


@router.message(F.text == "💬 Yordam")
async def support_start(message: Message, state: FSMContext):
    await message.answer("💬 <b>Mavzu</b> yuboring (qisqacha muammo tavsifi):")
    await state.set_state(SupportStates.subject)


@router.message(SupportStates.subject)
async def support_subject(message: Message, state: FSMContext):
    await state.update_data(subject=message.text[:255])
    await message.answer("💬 Endi <b>xabar</b> yuboring (muammoni batafsil yozing):")
    await state.set_state(SupportStates.message)


@router.message(SupportStates.message)
async def support_message(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()
    async with async_session_maker() as db:
        user = await get_user_by_telegram_id(db, message.from_user.id)
        if not user:
            await message.answer("Xato: foydalanuvchi topilmadi. /start yuboring.")
            return
        ticket = SupportTicket(
            user_id=user.id,
            subject=data["subject"],
            message=message.text,
            status=TicketStatus.open,
        )
        db.add(ticket)
        await db.commit()
    await message.answer(
        f"✅ Yordam so'rovi yaratildi!\n\n"
        f"<b>Mavzu:</b> {data['subject']}\n"
        f"Tez orada javob beramiz."
    )
