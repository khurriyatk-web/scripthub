"""Main menu reply keyboard — Uzbek labels."""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Primary reply keyboard shown under the chat input."""
    kb = [
        [KeyboardButton(text="🛍 Bozor"), KeyboardButton(text="📦 Kategoriyalar")],
        [KeyboardButton(text="🔍 Qidirish"), KeyboardButton(text="❤️ Sevimlilar")],
        [KeyboardButton(text="📥 Yuklamalar"), KeyboardButton(text="🛒 Buyurtmalar")],
        [KeyboardButton(text="👤 Profil"), KeyboardButton(text="🎁 Kunlik bonus")],
        [KeyboardButton(text="💬 Yordam"), KeyboardButton(text="⚙️ Sozlamalar")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def back_keyboard() -> InlineKeyboardMarkup:
    """Inline 'back to menu' button."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="menu:back")]
    ])


def mini_app_keyboard(frontend_url: str) -> InlineKeyboardMarkup:
    """Inline keyboard with Mini App button."""
    from aiogram.types import WebAppInfo
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="📱 Ilovani ochish",
            web_app=WebAppInfo(url=frontend_url),
        )],
    ])
