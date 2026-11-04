"""API dependencies."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError

from app.core.config import get_settings
from app.core.database import get_db
from app.models.user import User, Role

security = HTTPBearer(auto_error=False)


def verify_token(token: str) -> dict:
    """Verify and decode JWT token."""
    s = get_settings()
    try:
        payload = jwt.decode(token, s.secret_key, algorithms=[s.algorithm])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current user from JWT token."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = verify_token(credentials.credentials)
    user_id = int(payload.get("sub", 0))
    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


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
