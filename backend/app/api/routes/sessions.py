"""Sessions API routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.session import Session, Window, AgentState
from app.models.user import User, Role
from app.api.deps import get_current_user, require_operator

router = APIRouter(prefix="/sessions", tags=["sessions"])


class SessionCreate(BaseModel):
    """Session creation request."""
    name: str = Field(..., min_length=1, max_length=255)
    space: Optional[str] = Field(None, max_length=255)


class SessionUpdate(BaseModel):
    """Session update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    space: Optional[str] = Field(None, max_length=255)


class SessionResponse(BaseModel):
    """Session response."""
    id: int
    name: str
    space: str
    created_at: str
    updated_at: str
    window_count: int = 0
    
    class Config:
        from_attributes = True


class SessionListResponse(BaseModel):
    """Paginated session list response."""
    items: list[SessionResponse]
    total: int
    page: int
    page_size: int


@router.get("", response_model=SessionListResponse)
async def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    space: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionListResponse:
    """List sessions with pagination and optional space filter."""
    stmt = select(Session)
    if space is not None:
        stmt = stmt.where(Session.space == space)
    
    # Count total
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0
    
    # Paginate
    stmt = stmt.order_by(Session.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    
    # Get window counts
    session_ids = [s.id for s in sessions]
    window_counts = {}
    if session_ids:
        wc_stmt = select(Window.session_id, func.count(Window.id)).where(
            Window.session_id.in_(session_ids)
        ).group_by(Window.session_id)
        wc_result = await db.execute(wc_stmt)
        window_counts = dict(wc_result.all())
    
    items = [
        SessionResponse(
            id=s.id,
            name=s.name,
            space=s.space or "",
            created_at=s.created_at.isoformat(),
            updated_at=s.updated_at.isoformat(),
            window_count=window_counts.get(s.id, 0),
        )
        for s in sessions
    ]
    
    return SessionListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_in: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
) -> SessionResponse:
    """Create a new session."""
    session = Session(name=session_in.name, space=session_in.space or "")
    db.add(session)
    await db.commit()
    await db.refresh(session)
    
    return SessionResponse(
        id=session.id,
        name=session.name,
        space=session.space or "",
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        window_count=0,
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionResponse:
    """Get a session by ID."""
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Count windows
    wc_stmt = select(func.count(Window.id)).where(Window.session_id == session_id)
    window_count = await db.scalar(wc_stmt) or 0
    
    return SessionResponse(
        id=session.id,
        name=session.name,
        space=session.space or "",
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        window_count=window_count,
    )


@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    session_in: SessionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
) -> SessionResponse:
    """Update a session."""
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    update_data = session_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(session, field, value)
    
    await db.commit()
    await db.refresh(session)
    
    wc_stmt = select(func.count(Window.id)).where(Window.session_id == session_id)
    window_count = await db.scalar(wc_stmt) or 0
    
    return SessionResponse(
        id=session.id,
        name=session.name,
        space=session.space or "",
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
        window_count=window_count,
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
) -> None:
    """Delete a session."""
    session = await db.get(Session, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await db.delete(session)
    await db.commit()


@router.get("/spaces/list")
async def list_spaces(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[str]:
    """List all unique space names."""
    stmt = select(Session.space).where(Session.space != "").distinct()
    result = await db.execute(stmt)
    spaces = [row[0] for row in result.all() if row[0]]
    return sorted(spaces)
