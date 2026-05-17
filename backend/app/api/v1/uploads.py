"""Fayl yuklash endpointlari — avatar, hujjatlar, kitob muqovasi va h.k."""
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.dependencies import get_current_user, require_any
from app.models.oltp.user import User

router = APIRouter(prefix="/uploads", tags=["Uploads"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_IMAGE_TYPES = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_DOC_TYPES = {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".txt", ".jpg", ".png"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _save_upload(file: UploadFile, subdir: str, allowed_exts: set) -> str:
    """Faylni saqlash va URL qaytarish."""
    ext = Path(file.filename or "").suffix.lower()
    if ext not in allowed_exts:
        raise HTTPException(400, f"Yaroqsiz fayl turi. Ruxsat: {', '.join(allowed_exts)}")

    folder = UPLOAD_DIR / subdir
    folder.mkdir(parents=True, exist_ok=True)

    filename = f"{uuid.uuid4().hex}{ext}"
    path = folder / filename

    content = file.file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, f"Fayl juda katta (max {MAX_FILE_SIZE // 1024 // 1024} MB)")

    with open(path, "wb") as f:
        f.write(content)

    return f"/api/v1/uploads/files/{subdir}/{filename}"


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """Foydalanuvchi avatar rasmi."""
    url = _save_upload(file, f"avatars/user_{user.id}", ALLOWED_IMAGE_TYPES)
    return {"url": url, "filename": file.filename}


@router.post("/document")
async def upload_document(
    file: UploadFile = File(...),
    category: str = "general",
    user: User = Depends(get_current_user),
):
    """Hujjat fayli (pasport, attestat va h.k.)."""
    url = _save_upload(file, f"documents/user_{user.id}/{category}", ALLOWED_DOC_TYPES)
    return {"url": url, "filename": file.filename, "category": category}


@router.post("/announcement")
async def upload_announcement_image(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """E'lon uchun rasm."""
    url = _save_upload(file, "announcements", ALLOWED_IMAGE_TYPES)
    return {"url": url}


@router.post("/book-cover")
async def upload_book_cover(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """Kitob muqovasi."""
    url = _save_upload(file, "books", ALLOWED_IMAGE_TYPES)
    return {"url": url}


@router.get("/files/{subdir:path}/{filename}", dependencies=[Depends(require_any)])
def get_file(subdir: str, filename: str):
    """Yuklangan faylni qaytarish."""
    path = UPLOAD_DIR / subdir / filename
    if not path.exists():
        raise HTTPException(404, "Fayl topilmadi")
    return FileResponse(path)
