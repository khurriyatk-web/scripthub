"""Pagination inline keyboard."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def pagination_keyboard(prefix: str, page: int, total_pages: int) -> InlineKeyboardMarkup:
    """Generic pagination buttons. *prefix* is the callback namespace (e.g. 'market')."""
    buttons: list[InlineKeyboardButton] = []
    if page > 1:
        buttons.append(InlineKeyboardButton(text="⬅️", callback_data=f"{prefix}:page:{page - 1}"))
    buttons.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="noop"))
    if page < total_pages:
        buttons.append(InlineKeyboardButton(text="➡️", callback_data=f"{prefix}:page:{page + 1}"))
    return InlineKeyboardMarkup(inline_keyboard=[buttons])
