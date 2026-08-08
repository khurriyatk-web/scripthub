"""Bot package — Aiogram dispatcher, handlers, keyboards, middlewares."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config.settings import settings

logger = logging.getLogger("scripthub.bot")

bot: Bot | None = None
dp: Dispatcher | None = None
_polling_task: asyncio.Task | None = None


def _init() -> tuple[Bot, Dispatcher]:
    """Create Bot + Dispatcher instances (idempotent)."""
    global bot, dp
    if bot is None:
        bot = Bot(
            token=settings.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
        )
    if dp is None:
        dp = Dispatcher()
        # Register routers
        from handlers import register_all_routers
        register_all_routers(dp)
    return bot, dp


async def start_bot() -> None:
    """Start the bot in background polling mode."""
    global _polling_task
    if not settings.bot_token:
        logger.warning("BOT_TOKEN not set — bot disabled.")
        return

    b, d = _init()
    me = await b.get_me()
    logger.info(f"Bot started: @{me.username}")

    # Run polling in background (non-blocking for FastAPI)
    _polling_task = asyncio.create_task(_polling_loop(b, d))


async def _polling_loop(b: Bot, d: Dispatcher) -> None:
    """Internal polling coroutine."""
    try:
        await d.start_polling(b, skip_updates=True)
    except Exception as e:
        logger.error(f"Bot polling error: {e}")


async def stop_bot() -> None:
    """Gracefully stop the bot."""
    global _polling_task, bot
    if _polling_task:
        _polling_task.cancel()
        try:
            await _polling_task
        except asyncio.CancelledError:
            pass
    if bot:
        await bot.session.close()
    logger.info("Bot stopped.")


async def process_update(update_data: dict[str, Any]) -> None:
    """Process a single update (used in webhook mode)."""
    from aiogram.types import Update
    b, d = _init()
    update = Update.model_validate(update_data, context={"bot": b})
    await d.feed_update(b, update)
