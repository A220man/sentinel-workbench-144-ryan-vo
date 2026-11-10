"""Privacy mode API routes."""
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from typing import Optional

from app.models.user import User
from app.api.deps import get_current_user, require_operator
from app.services.privacy import get_privacy_service
from app.core.config import get_settings, clear_settings_cache

router = APIRouter(prefix="/privacy", tags=["privacy"])


class PrivacySettingsResponse(BaseModel):
    """Privacy settings response."""
    enabled: bool
    mask_char: str
    rules: list[str]
    allow_hosts: list[str]


class PrivacySettingsUpdate(BaseModel):
    """Privacy settings update request."""
    enabled: Optional[bool] = None
    mask_char: Optional[str] = Field(None, min_length=1, max_length=1)
    rules: Optional[list[str]] = None
    allow_hosts: Optional[list[str]] = None


class MaskTextRequest(BaseModel):
    """Mask text request."""
    text: str = Field(..., min_length=1)


class MaskTextResponse(BaseModel):
    """Mask text response."""
    masked_text: str
    matches_count: int


@router.get("", response_model=PrivacySettingsResponse)
async def get_privacy_settings(
    current_user: User = Depends(get_current_user),
) -> PrivacySettingsResponse:
    """Get current privacy settings."""
    settings = get_settings()
    return PrivacySettingsResponse(
        enabled=settings.privacy_enabled,
        mask_char=settings.privacy_mask_char,
        rules=settings.privacy_rules,
        allow_hosts=settings.privacy_allow_hosts,
    )


@router.patch("", response_model=PrivacySettingsResponse)
async def update_privacy_settings(
    update: PrivacySettingsUpdate,
    current_user: User = Depends(require_operator),
) -> PrivacySettingsResponse:
    """Update privacy settings (operator+ only)."""
    # Note: This is a runtime-only update. For persistence, update .env or config.toml
    settings = get_settings()
    
    if update.enabled is not None:
        settings.privacy_enabled = update.enabled
    if update.mask_char is not None:
        settings.privacy_mask_char = update.mask_char
    if update.rules is not None:
        settings.privacy_rules = update.rules
    if update.allow_hosts is not None:
        settings.privacy_allow_hosts = update.allow_hosts
    
    # Reload privacy service settings to recompile patterns
    from app.services.privacy import get_privacy_service
    privacy_service = get_privacy_service()
    privacy_service.reload_settings()
    clear_settings_cache()
    
    return PrivacySettingsResponse(
        enabled=settings.privacy_enabled,
        mask_char=settings.privacy_mask_char,
        rules=settings.privacy_rules,
        allow_hosts=settings.privacy_allow_hosts,
    )


@router.post("/mask", response_model=MaskTextResponse)
async def mask_text(
    request: MaskTextRequest,
    current_user: User = Depends(get_current_user),
) -> MaskTextResponse:
    """Mask sensitive text using current privacy rules."""
    privacy_service = get_privacy_service()
    matches = privacy_service.find_matches(request.text)
    masked = privacy_service.mask_text(request.text)
    return MaskTextResponse(
        masked_text=masked,
        matches_count=len(matches),
    )


@router.get("/status")
async def privacy_status(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get privacy mode status for dock indicator."""
    privacy_service = get_privacy_service()
    return {
        "enabled": privacy_service.is_enabled(),
        "mask_char": privacy_service.get_mask_char(),
    }

