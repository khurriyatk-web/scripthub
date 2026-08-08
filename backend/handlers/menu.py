"""Menu handler — main menu navigation (Uzbek)."""
from __future__ import annotations

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from keyboards.main import main_menu_keyboard
from keyboards.marketplace import marketplace_keyboard
from keyboards.profile import profile_keyboard

router = Router()


@router.message(F.text == "🏠 Home")
async def home(message: Message):
    await message.answer(
        "🏠 <b>Bosh sahifa</b>\n\nScriptHub'ga xush kelibsiz!",
        reply_markup=main_menu_keyboard(),
    )


@router.message(F.text == "🛍 Bozor")
async def marketplace(message: Message):
    await message.answer(
        "🛍 <b>Bozor</b>\n\nManba kod loyihalarini ko'ring:",
        reply_markup=marketplace_keyboard(),
    )


@router.message(F.text == "👤 Profil")
async def profile(message: Message):
    await message.answer("👤 <b>Profil</b>", reply_markup=profile_keyboard())


@router.message(F.text == "❓ FAQ")
async def faq(message: Message):
    text = (
        "<b>❓ Tez-tez so'raladigan savollar</b>\n\n"
        "<b>Kod qanday sotib olinadi?</b>\n"
        "Bozorni ko'ring, loyihani tanlang va \"Sotib olish\" tugmasini bosing.\n\n"
        "<b>Kod qanday sotiladi?</b>\n"
        "Profildan dasturchi huquqi oling, keyin loyiha qo'shing.\n\n"
        "<b>To'lov usullari?</b>\n"
        "Karta orqali (so'm) va hisob balansi.\n\n"
        "<b>Pul qaytarish mumkinmi?</b>\n"
        "Xariddan keyin 24 soat ichida yordam bilan bog'laning."
    )
    await message.answer(text)


@router.message(F.text == "⚙️ Sozlamalar")
async def settings(message: Message):
    await message.answer("⚙️ Sozlamalar — til va bildirishnomalar tez orada.")


@router.message(F.text == "📢 Yangiliklar")
async def news(message: Message):
    await message.answer("📢 Yangiliklar hozircha yo'q. Tez orada!")


@router.callback_query(F.data == "menu:back")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text("🏠 Bosh menyu", reply_markup=None)
    await callback.message.answer("Tanlang:", reply_markup=main_menu_keyboard())
    await callback.answer()
