"""Store settings model — merchant card info for manual payments."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, Text, Integer
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class StoreSettings(Base):
    __tablename__ = "store_settings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Merchant card info shown to buyers during checkout
    merchant_card_number: Mapped[str] = mapped_column(String(32), default="", nullable=False)
    merchant_card_holder: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    merchant_bank: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    merchant_phone: Mapped[str] = mapped_column(String(32), default="", nullable=False)
    # Store info
    store_name: Mapped[str] = mapped_column(String(128), default="ScriptHub", nullable=False)
    store_description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    # Currency: UZS (so'm) — prices stored in tiyin (1 so'm = 100 tiyin)
    currency: Mapped[str] = mapped_column(String(8), default="UZS", nullable=False)
    # Support contact
    support_username: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
