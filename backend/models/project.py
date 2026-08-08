"""Project model — a developer's sellable source-code listing."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, Integer, Text, Enum, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class ProjectStatus(str, enum.Enum):
    draft = "draft"
    pending = "pending"      # awaiting admin verification
    published = "published"
    rejected = "rejected"
    archived = "archived"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    developer_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    category_id: Mapped[str | None] = mapped_column(ForeignKey("categories.id"), nullable=True, index=True)

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    short_description: Mapped[str] = mapped_column(String(255), nullable=False)
    full_description: Mapped[str] = mapped_column(Text, nullable=False)
    technologies: Mapped[str] = mapped_column(String(512), nullable=False, default="")  # comma-separated
    tags: Mapped[str] = mapped_column(String(512), nullable=False, default="")  # comma-separated

    price: Mapped[int] = mapped_column(Integer, nullable=False, default=0)  # cents
    discount_percent: Mapped[int] = mapped_column(Integer, default=0)
    discounted_price: Mapped[int] = mapped_column(Integer, default=0)  # cached

    version: Mapped[str] = mapped_column(String(32), default="1.0.0")
    requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    license: Mapped[str] = mapped_column(String(64), default="MIT")
    documentation: Mapped[str | None] = mapped_column(Text, nullable=True)
    github_link: Mapped[str | None] = mapped_column(String(255), nullable=True)
    demo_video: Mapped[str | None] = mapped_column(String(255), nullable=True)
    demo_images: Mapped[str] = mapped_column(Text, default="")  # JSON array of paths

    file_path: Mapped[str | None] = mapped_column(String(512), nullable=True)  # main downloadable file
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    file_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)  # sha256

    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.draft)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    views: Mapped[int] = mapped_column(Integer, default=0)
    sales_count: Mapped[int] = mapped_column(Integer, default=0)
    rating_avg: Mapped[float] = mapped_column(Float, default=0.0)
    rating_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    developer: Mapped["User"] = relationship("User", back_populates="projects")
    category: Mapped["Category | None"] = relationship("Category", back_populates="projects")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="project")
    orders: Mapped[list["Order"]] = relationship("Order", back_populates="project")

    def __repr__(self) -> str:
        return f"<Project {self.name} status={self.status}>"
