"""Profile inline keyboard — Uzbek labels."""


def _fmt_balance(balance: int) -> str:
    """Balance in so'm (stored as tiyin)."""
    return f"{int(balance/100):,} so'm".replace(",", " ")


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def profile_keyboard(is_developer: bool = False) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text="💰 Balans", callback_data="profile:balance")],
        [InlineKeyboardButton(text="📥 Yuklamalar", callback_data="profile:downloads")],
        [InlineKeyboardButton(text="❤️ Sevimlilar", callback_data="profile:favorites")],
        [InlineKeyboardButton(text="🎁 Kunlik bonus", callback_data="profile:bonus")],
        [InlineKeyboardButton(text="🔗 Referral havola", callback_data="profile:referral")],
    ]
    if is_developer:
        rows.append([InlineKeyboardButton(text="🛠 Dasturchi paneli", callback_data="dev:panel")])
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="menu:back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
