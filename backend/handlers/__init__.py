"""Handlers package — registers all bot routers."""
from aiogram import Dispatcher

from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.marketplace import router as marketplace_router
from handlers.profile import router as profile_router
from handlers.developer import router as developer_router
from handlers.support import router as support_router


def register_all_routers(dp: Dispatcher) -> None:
    """Attach all handler routers to the dispatcher."""
    dp.include_router(start_router)
    dp.include_router(menu_router)
    dp.include_router(marketplace_router)
    dp.include_router(profile_router)
    dp.include_router(developer_router)
    dp.include_router(support_router)
