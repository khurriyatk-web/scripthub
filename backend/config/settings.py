"""Application configuration loader.

Reads environment variables (from .env or the host environment) and exposes
them as a typed singleton.  Import `settings` anywhere in the codebase.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Telegram
    bot_token: str = ""
    admin_ids: str = ""
    bot_username: str = "ScriptHubBot"

    # Web
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    # Database
    database_url: str = "sqlite+aiosqlite:///./database/scripthub.db"

    # Security
    secret_key: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080  # 7 days

    # Storage
    storage_path: str = "./storage"
    max_upload_mb: int = 200

    # Caddy
    caddy_domain: str = "scripthub.techmentor.uz"
    caddy_port: int = 3443

    # Logging
    log_path: str = "./logs"

    # ── Derived helpers ──────────────────────────────────────────

    @property
    def admin_id_list(self) -> list[int]:
        """Parse the comma-separated ADMIN_IDS env var into integers."""
        return [
            int(x.strip())
            for x in self.admin_ids.split(",")
            if x.strip().isdigit()
        ]

    @property
    def storage_dir(self) -> Path:
        p = Path(self.storage_path).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def log_dir(self) -> Path:
        p = Path(self.log_path).resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def database_dir(self) -> Path:
        p = Path("./database").resolve()
        p.mkdir(parents=True, exist_ok=True)
        return p

    def storage_subdir(self, name: str) -> Path:
        """Return (and create) a subdirectory under storage."""
        p = self.storage_dir / name
        p.mkdir(parents=True, exist_ok=True)
        return p


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
