"""Order model."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Integer, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class OrderStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"
    completed = "completed"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # cents
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.pending)
    promo_code_id: Mapped[str | None] = mapped_column(ForeignKey("promo_codes.id"), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    project: Mapped["Project"] = relationship("Project", back_populates="orders")
    payment: Mapped["Payment | None"] = relationship("Payment", back_populates="order", uselist=False)

    def __repr__(self) -> str:
        return f"<Order {self.id[:8]} status={self.status}>"
