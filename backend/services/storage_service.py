"""File storage service.

Handles upload, dedup (sha256), and safe retrieval of project files.
All files live under storage/ subdirectories and are addressed by UUID.
"""
from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

import aiofiles

from config.settings import settings

# Allowed upload extensions
ALLOWED_EXTENSIONS = {
    "zip", "rar", "7z", "pdf", "png", "jpg", "jpeg", "gif",
    "mp4", "apk", "exe", "docx", "pptx", "txt", "py", "js",
    "ts", "json", "md",
}

CHUNK_SIZE = 1024 * 1024  # 1 MB


def _ext(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def is_allowed(filename: str) -> bool:
    return _ext(filename) in ALLOWED_EXTENSIONS


async def save_upload(data: bytes, filename: str, subdir: str = "projects") -> tuple[str, str, int, str]:
    """Persist *data* to storage/<subdir>/<uuid>.<ext>.

    Returns ``(relative_path, original_filename, size_bytes, sha256)``.
    """
    ext = _ext(filename)
    file_uuid = str(uuid.uuid4())
    safe_name = f"{file_uuid}.{ext}" if ext else file_uuid

    target_dir = settings.storage_subdir(subdir)
    target_path = target_dir / safe_name

    async with aiofiles.open(target_path, "wb") as f:
        await f.write(data)

    sha = hashlib.sha256(data).hexdigest()
    rel_path = f"{subdir}/{safe_name}"
    return rel_path, filename, len(data), sha


async def stream_to_file(src, target: Path) -> int:
    """Stream an async generator / file-like object to *target*. Returns bytes written."""
    written = 0
    async with aiofiles.open(target, "wb") as f:
        async for chunk in src:
            await f.write(chunk)
            written += len(chunk)
    return written


def file_abspath(rel_path: str) -> Path:
    """Resolve a storage-relative path to an absolute filesystem path."""
    return settings.storage_dir / rel_path
