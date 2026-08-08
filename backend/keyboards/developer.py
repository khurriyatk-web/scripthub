"""Developer panel inline keyboard — Uzbek labels."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def developer_panel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Loyiha qo'shish", callback_data="dev:add")],
        [InlineKeyboardButton(text="📋 Mening loyihalarim", callback_data="dev:projects")],
        [InlineKeyboardButton(text="📊 Statistika", callback_data="dev:stats")],
        [InlineKeyboardButton(text="💰 Daromad", callback_data="dev:revenue")],
        [InlineKeyboardButton(text="⭐ Sharhlar", callback_data="dev:reviews")],
        [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="profile:me")],
    ])
