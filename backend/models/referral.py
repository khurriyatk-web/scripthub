"""Referral model — tracks who referred whom."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Referral(Base):
    __tablename__ = "referrals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    referrer_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    referred_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    reward_amount: Mapped[int] = mapped_column(Integer, default=0)  # cents
    is_paid: Mapped[bool] = mapped_column(Integer, default=0)  # 0/1 for sqlite bool
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<Referral {self.referrer_id[:8]}->{self.referred_id[:8]}>"
