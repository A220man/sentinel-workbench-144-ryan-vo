"""Authentication API routes."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
import secrets

from app.core.config import get_settings
from app.core.database import get_db
from app.models.user import User, Role
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)

settings = get_settings()


class TokenResponse(BaseModel):
    """Token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response."""
    id: int
    email: str
    username: Optional[str]
    full_name: Optional[str]
    role: Role
    is_active: bool


class LoginRequest(BaseModel):
    """Login request for demo mode."""
    email: str
    password: str


def create_access_token(user: User) -> str:
    """Create JWT access token."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def verify_token(token: str) -> dict:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
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


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Demo login endpoint (only works when OIDC disabled)."""
    if settings.oidc_enabled:
        raise HTTPException(status_code=400, detail="OIDC enabled - use /auth/oidc/login")
    
    # Demo mode: find or create user
    stmt = select(User).where(User.email == request.email)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(email=request.email, username=request.email.split("@")[0], role=Role.OPERATOR)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    user.last_login_at = datetime.now(timezone.utc)
    await db.commit()
    
    token = create_access_token(user)
    
    # Set HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # True in production with HTTPS
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )
    
    return TokenResponse(
        access_token=token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/logout")
async def logout(response: Response) -> dict:
    """Logout endpoint."""
    response.delete_cookie("access_token")
    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current user info."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
    )


@router.get("/oidc/login")
async def oidc_login(request: Request) -> dict:
    """Initiate OIDC login flow."""
    if not settings.oidc_enabled:
        raise HTTPException(status_code=400, detail="OIDC not enabled")
    
    # Generate state and nonce for PKCE
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    
    # Store in session (in production, use proper session store)
    request.session["oidc_state"] = state
    request.session["oidc_nonce"] = nonce
    
    # Build authorization URL
    auth_url = (
        f"{settings.oidc_issuer_url}/protocol/openid-connect/auth"
        f"?client_id={settings.oidc_client_id}"
        f"&redirect_uri={settings.oidc_redirect_uri}"
        f"&response_type=code"
        f"&scope={settings.oidc_scopes}"
        f"&state={state}"
        f"&nonce={nonce}"
    )
    
    return {"authorization_url": auth_url, "state": state}


@router.get("/oidc/callback")
async def oidc_callback(
    request: Request,
    code: str,
    state: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Handle OIDC callback."""
    if not settings.oidc_enabled:
        raise HTTPException(status_code=400, detail="OIDC not enabled")
    
    # Verify state
    stored_state = request.session.get("oidc_state")
    if not stored_state or stored_state != state:
        raise HTTPException(status_code=400, detail="Invalid state")
    
    # Exchange code for tokens (simplified - in production use httpx to call token endpoint)
    # This is a placeholder - real implementation would call Keycloak token endpoint
    # and validate ID token with JWKS
    
    # For demo, create/find user
    stmt = select(User).where(User.email == "oidc-user@example.com")
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            email="oidc-user@example.com",
            username="oidc-user",
            role=Role.OPERATOR,
            oidc_sub="oidc-sub-123",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    token = create_access_token(user)
    
    response = Response(content="Login successful", media_type="text/html")
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.access_token_expire_minutes * 60,
    )
    return response


@router.get("/oidc/logout")
async def oidc_logout(request: Request) -> dict:
    """OIDC logout."""
    request.session.clear()
    return {"logout_url": f"{settings.oidc_issuer_url}/protocol/openid-connect/logout"}
