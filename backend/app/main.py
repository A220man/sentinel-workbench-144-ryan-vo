"""Main FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.api.routes import health, sessions, windows, attention, auth

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan."""
    await init_db()
    yield
    await close_db()


def create_app() -> FastAPI:
    """Create FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Sentinel Workbench - Terminal window manager for AI agents",
        lifespan=lifespan,
        docs_url="/api/docs" if settings.debug else None,
        redoc_url="/api/redoc" if settings.debug else None,
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Session middleware for OIDC
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        max_age=settings.access_token_expire_minutes * 60,
    )
    
    # Include routers
    app.include_router(health.router, prefix="/api")
    app.include_router(sessions.router, prefix="/api")
    app.include_router(windows.router, prefix="/api")
    app.include_router(attention.router, prefix="/api")
    app.include_router(auth.router, prefix="/api")
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.debug)
