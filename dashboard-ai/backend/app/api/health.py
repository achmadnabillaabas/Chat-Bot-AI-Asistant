"""
Health check endpoint for monitoring.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI Assistant API",
        "version": "1.0.0"
    }


@router.get("/ready")
async def readiness_check():
    """
    Readiness check for deployment orchestration.
    Should check external dependencies (DB, Qdrant, 9Router).
    """
    # TODO: Implement actual checks
    return {
        "ready": True,
        "checks": {
            "database": "ok",
            "qdrant": "ok",
            "9router": "ok"
        }
    }
