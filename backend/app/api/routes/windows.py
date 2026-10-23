"""Windows API routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.session import Window, Session, AgentState
from app.models.user import User
from app.api.deps import get_current_user, require_operator

router = APIRouter(prefix="/windows", tags=["windows"])


class WindowCreate(BaseModel):
    """Window creation request."""
    session_id: int
    workspace: int = Field(default=1, ge=1, le=9)
    index: int = Field(default=0, ge=0)
    title: Optional[str] = Field(None, max_length=255)
    command: Optional[str] = None
    cwd: Optional[str] = Field(None, max_length=512)


class WindowUpdate(BaseModel):
    """Window update request."""
    title: Optional[str] = Field(None, max_length=255)
    command: Optional[str] = None
    cwd: Optional[str] = Field(None, max_length=512)
    agent_state: Optional[AgentState] = None
    quiet: Optional[bool] = None


class WindowResponse(BaseModel):
    """Window response."""
    id: int
    session_id: int
    workspace: int
    index: int
    title: Optional[str]
    command: Optional[str]
    cwd: Optional[str]
    agent_state: AgentState
    completion_seq: int
    quiet: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class WindowListResponse(BaseModel):
    """Paginated window list response."""
    items: list[WindowResponse]
    total: int
    page: int
    page_size: int


@router.get("", response_model=WindowListResponse)
async def list_windows(
    session_id: Optional[int] = Query(None),
    workspace: Optional[int] = Query(None, ge=1, le=9),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WindowListResponse:
    """List windows with optional filters."""
    stmt = select(Window)
    if session_id is not None:
        stmt = stmt.where(Window.session_id == session_id)
    if workspace is not None:
        stmt = stmt.where(Window.workspace == workspace)
    
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0
    
    stmt = stmt.order_by(Window.session_id, Window.workspace, Window.index).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    windows = result.scalars().all()
    
    items = [
        WindowResponse(
            id=w.id,
            session_id=w.session_id,
            workspace=w.workspace,
            index=w.index,
            title=w.title,
            command=w.command,
            cwd=w.cwd,
            agent_state=w.agent_state,
            completion_seq=w.completion_seq,
            quiet=w.quiet,
            created_at=w.created_at.isoformat(),
            updated_at=w.updated_at.isoformat(),
        )
        for w in windows
    ]
    
    return WindowListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("", response_model=WindowResponse, status_code=status.HTTP_201_CREATED)
async def create_window(
    window_in: WindowCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
) -> WindowResponse:
    """Create a new window."""
    # Verify session exists
    session = await db.get(Session, window_in.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    window = Window(**window_in.model_dump())
    db.add(window)
    await db.commit()
    await db.refresh(window)
    
    return WindowResponse(
        id=window.id,
        session_id=window.session_id,
        workspace=window.workspace,
        index=window.index,
        title=window.title,
        command=window.command,
        cwd=window.cwd,
        agent_state=window.agent_state,
        completion_seq=window.completion_seq,
        quiet=window.quiet,
        created_at=window.created_at.isoformat(),
        updated_at=window.updated_at.isoformat(),
    )


@router.get("/{window_id}", response_model=WindowResponse)
async def get_window(
    window_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WindowResponse:
    """Get a window by ID."""
    window = await db.get(Window, window_id)
    if not window:
        raise HTTPException(status_code=404, detail="Window not found")
    
    return WindowResponse(
        id=window.id,
        session_id=window.session_id,
        workspace=window.workspace,
        index=window.index,
        title=window.title,
        command=window.command,
        cwd=window.cwd,
        agent_state=window.agent_state,
        completion_seq=window.completion_seq,
        quiet=window.quiet,
        created_at=window.created_at.isoformat(),
        updated_at=window.updated_at.isoformat(),
    )


@router.patch("/{window_id}", response_model=WindowResponse)
async def update_window(
    window_id: int,
    window_in: WindowUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
) -> WindowResponse:
    """Update a window."""
    window = await db.get(Window, window_id)
    if not window:
        raise HTTPException(status_code=404, detail="Window not found")
    
    update_data = window_in.model_dump(exclude_unset=True)
    
    # Handle agent state change - create history entry
    if "agent_state" in update_data and update_data["agent_state"] != window.agent_state:
        from app.models.session import AgentStateHistory
        history = AgentStateHistory(
            window_id=window.id,
            from_state=window.agent_state,
            to_state=update_data["agent_state"],
        )
        db.add(history)
    
    for field, value in update_data.items():
        setattr(window, field, value)
    
    await db.commit()
    await db.refresh(window)
    
    return WindowResponse(
        id=window.id,
        session_id=window.session_id,
        workspace=window.workspace,
        index=window.index,
        title=window.title,
        command=window.command,
        cwd=window.cwd,
        agent_state=window.agent_state,
        completion_seq=window.completion_seq,
        quiet=window.quiet,
        created_at=window.created_at.isoformat(),
        updated_at=window.updated_at.isoformat(),
    )


@router.delete("/{window_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_window(
    window_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
) -> None:
    """Delete a window."""
    window = await db.get(Window, window_id)
    if not window:
        raise HTTPException(status_code=404, detail="Window not found")
    
    await db.delete(window)
    await db.commit()


@router.post("/{window_id}/move", response_model=WindowResponse)
async def move_window(
    window_id: int,
    to_session_id: int = Query(...),
    to_workspace: int = Query(1, ge=1, le=9),
    to_index: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
) -> WindowResponse:
    """Move a window to another session/workspace."""
    window = await db.get(Window, window_id)
    if not window:
        raise HTTPException(status_code=404, detail="Window not found")
    
    # Verify target session exists
    target_session = await db.get(Session, to_session_id)
    if not target_session:
        raise HTTPException(status_code=404, detail="Target session not found")
    
    # Lock sessions in consistent order to prevent deadlock
    session_ids = sorted([window.session_id, to_session_id])
    for sid in session_ids:
        await db.execute(select(Session).where(Session.id == sid).with_for_update())
    
    window.session_id = to_session_id
    window.workspace = to_workspace
    window.index = to_index
    
    await db.commit()
    await db.refresh(window)
    
    return WindowResponse(
        id=window.id,
        session_id=window.session_id,
        workspace=window.workspace,
        index=window.index,
        title=window.title,
        command=window.command,
        cwd=window.cwd,
        agent_state=window.agent_state,
        completion_seq=window.completion_seq,
        quiet=window.quiet,
        created_at=window.created_at.isoformat(),
        updated_at=window.updated_at.isoformat(),
    )


@router.post("/{window_id}/quiet", response_model=WindowResponse)
async def set_window_quiet(
    window_id: int,
    quiet: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_operator),
) -> WindowResponse:
    """Set window quiet mode (suppresses Inbox items)."""
    window = await db.get(Window, window_id)
    if not window:
        raise HTTPException(status_code=404, detail="Window not found")
    
    window.quiet = quiet
    
    # If becoming quiet, close existing attention items for this window
    if quiet:
        from app.models.session import AttentionItem, AttentionKind
        from sqlalchemy import update
        stmt = update(AttentionItem).where(
            AttentionItem.window_id == window_id,
            AttentionItem.dismissed_at.is_(None),
            AttentionItem.kind.in_([AttentionKind.FINISHED, AttentionKind.QUESTION, AttentionKind.ERRORED])
        ).values(dismissed_at=func.now())
        await db.execute(stmt)
    
    await db.commit()
    await db.refresh(window)
    
    return WindowResponse(
        id=window.id,
        session_id=window.session_id,
        workspace=window.workspace,
        index=window.index,
        title=window.title,
        command=window.command,
        cwd=window.cwd,
        agent_state=window.agent_state,
        completion_seq=window.completion_seq,
        quiet=window.quiet,
        created_at=window.created_at.isoformat(),
        updated_at=window.updated_at.isoformat(),
    )
