"""Marketplace inline keyboards — UZS pricing."""


def _format_price(price: int, discounted: int = 0, discount_percent: int = 0) -> str:
    """Format price in UZS (som). Values are in tiyin (1 som = 100 tiyin)."""
    if price == 0:
        return "BEPUL"
    som = price / 100
    if discount_percent > 0 and discounted > 0:
        return f"~~{int(price/100):,} som~~ -> {int(discounted/100):,} som (-{discount_percent}%)".replace(",", " ")
    return f"{int(som):,} som".replace(",", " ")


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def marketplace_keyboard() -> InlineKeyboardMarkup:
    """Marketplace sorting/filter options."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔥 Mashhur", callback_data="market:trending"),
            InlineKeyboardButton(text="🆕 Yangi", callback_data="market:new"),
        ],
        [
            InlineKeyboardButton(text="💰 Arzon", callback_data="market:price_low"),
            InlineKeyboardButton(text="⭐ Reyting", callback_data="market:rating"),
        ],
        [
            InlineKeyboardButton(text="🏷 Chegirma", callback_data="market:discount"),
            InlineKeyboardButton(text="📦 Kategoriyalar", callback_data="categories:list"),
        ],
        [InlineKeyboardButton(text="🔍 Qidirish", callback_data="market:search")],
    ])


def project_card_keyboard(project_id: str, price: int, purchased: bool = False) -> InlineKeyboardMarkup:
    """Action buttons for a single project card."""
    buttons: list[list[InlineKeyboardButton]] = []

    if purchased or price == 0:
        buttons.append([InlineKeyboardButton(text="📥 Yuklab olish", callback_data=f"download:{project_id}")])
    else:
        buttons.append([InlineKeyboardButton(text="🛒 Sotib olish", callback_data=f"buy:{project_id}")])

    buttons.append([
        InlineKeyboardButton(text="❤️", callback_data=f"fav:{project_id}"),
        InlineKeyboardButton(text="👁 Tafsilot", callback_data=f"detail:{project_id}"),
        InlineKeyboardButton(text="⭐ Sharh", callback_data=f"review:{project_id}"),
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
