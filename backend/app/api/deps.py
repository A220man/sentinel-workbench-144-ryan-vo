"""API dependencies."""
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User, Role
from app.api.routes.auth import get_user_from_token


async def get_current_user(
    user: User = Depends(get_user_from_token),
) -> User:
    """Get current authenticated user."""
    return user


async def require_operator(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require operator or admin role."""
    if current_user.role not in (Role.OPERATOR, Role.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operator role required",
        )
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """Require admin role."""
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required",
        )
    return current_user
