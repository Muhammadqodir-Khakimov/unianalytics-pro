"""Cache boshqaruv endpointlari (admin uchun)."""
from fastapi import APIRouter, Depends

from app.core.cache import cache
from app.core.dependencies import require_admin

router = APIRouter(prefix="/cache", tags=["Cache"], dependencies=[Depends(require_admin)])


@router.get("/stats")
def cache_stats():
    return cache.stats()


@router.delete("/clear")
def clear_cache(prefix: str = ""):
    count = cache.invalidate(prefix)
    return {"invalidated": count}
