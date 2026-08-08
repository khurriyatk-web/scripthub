"""File upload route — secure upload with validation and dedup."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from database import get_session
from models.user import Role
from routes.deps import get_current_user
from services.storage_service import save_upload, is_allowed

router = APIRouter()


class UploadResult(BaseModel):
    path: str
    filename: str
    size: int
    sha256: str


PROJECT_EXTENSIONS = {"zip", "rar", "7z", "tar", "gz", "py", "js", "ts", "json", "md", "txt"}
IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


@router.post("/project-file", response_model=UploadResult)
async def upload_project_file(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Upload a main project file (zip/rar/etc). Developer only."""
    if user.role not in (Role.developer, Role.admin, Role.moderator):
        raise HTTPException(status_code=403, detail="Developer account required")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Fayl nomi yoq")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in PROJECT_EXTENSIONS:
        raise HTTPException(status_code=415, detail=f"Fayl turi qollab-quvvatlanmaydi. Mumkin: {', '.join(sorted(PROJECT_EXTENSIONS))}")

    data = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail=f"Fayl {settings.max_upload_mb}MB dan katta")

    rel_path, original_name, size, sha = await save_upload(data, file.filename, "projects")
    return UploadResult(path=rel_path, filename=original_name, size=size, sha256=sha)


@router.post("/image", response_model=UploadResult)
async def upload_image(
    file: UploadFile = File(...),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Upload a demo image / avatar."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Fayl nomi yoq")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in IMAGE_EXTENSIONS:
        raise HTTPException(status_code=415, detail=f"Rasm turi qollab-quvvatlanmaydi. Mumkin: {', '.join(sorted(IMAGE_EXTENSIONS))}")

    data = await file.read()
    max_bytes = 10 * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail="Rasm 10MB dan katta")

    rel_path, original_name, size, sha = await save_upload(data, file.filename, "images")
    return UploadResult(path=rel_path, filename=original_name, size=size, sha256=sha)


@router.post("/payment-screenshot", response_model=UploadResult)
async def upload_payment_screenshot(
    file: UploadFile = File(...),
    order_id: str = Form(...),
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_session),
):
    """Upload a payment screenshot (buyer proof of transfer)."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Fayl nomi yoq")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in IMAGE_EXTENSIONS:
        raise HTTPException(status_code=415, detail="Faqat rasm yuklash mumkin")

    data = await file.read()
    max_bytes = 10 * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail="Rasm 10MB dan katta")

    rel_path, original_name, size, sha = await save_upload(data, file.filename, "payments")
    return UploadResult(path=rel_path, filename=original_name, size=size, sha256=sha)
