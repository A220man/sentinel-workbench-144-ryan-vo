"""Health check endpoint."""
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import get_settings

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str
    environment: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
    )
