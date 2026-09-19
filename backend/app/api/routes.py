"""Versioned application API endpoints."""

from fastapi import APIRouter

from backend.app.core.config import settings

router = APIRouter(prefix="/api/v1", tags=["platform"])


@router.get("/info")
def platform_info() -> dict[str, str]:
    """Return non-sensitive metadata about this platform instance."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": settings.app_env,
    }
