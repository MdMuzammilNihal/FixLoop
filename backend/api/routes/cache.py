from fastapi import APIRouter
from backend.api.services.cache_services import cache_manager

router = APIRouter()

@router.get("/api/cache/stats")
async def cache_stats():
    return cache_manager.get_cache_stats()

@router.post("/api/cache/save")
async def save_cache():
    success = cache_manager.save_cache_to_disk()
    return {"success": success, "message": "Cache saved to disk" if success else "Failed to save cache"}

@router.post("/api/cache/clear")
async def clear_cache():
    return cache_manager.clear_cache() 