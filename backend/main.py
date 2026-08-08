"""FastAPI application factory.

Wires up CORS, routers, startup (DB init + default data), and the
Telegram bot (polling or webhook depending on configuration).
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config.settings import settings
from database import init_db
from routes import api_router


# ── Logging ────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.log_dir / "app.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("scripthub")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup + shutdown lifecycle."""
    logger.info("Starting ScriptHub backend ...")
    await init_db()
    logger.info("Database initialised.")

    # Seed default categories + admin on first run
    from services.seed_service import seed_defaults
    await seed_defaults()

    # Start the Telegram bot in the background
    from bot import start_bot
    await start_bot()

    yield

    # Shutdown
    from bot import stop_bot
    await stop_bot()
    logger.info("ScriptHub backend stopped.")


app = FastAPI(
    title="ScriptHub API",
    version="1.0.0",
    description="Telegram Marketplace — source-code marketplace backend.",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# ── Middleware ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static file serving (uploads) ───────────────────────────────────
app.mount("/static", StaticFiles(directory=str(settings.storage_dir)), name="static")

# ── Routes ──────────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "scripthub"}
