"""Attention/Inbox API routes."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.models.session import AttentionItem, AttentionKind, Window
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter(prefix="/attention", tags=["attention"])


class AttentionItemResponse(BaseModel):
    """Attention item response."""
    id: int
    window_id: int
    window_title: Optional[str]
    session_name: str
    kind: AttentionKind
    title: str
    message: Optional[str]
    human_nonce: Optional[str]
    dismissed_at: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


class AttentionListResponse(BaseModel):
    """Paginated attention list response."""
    items: list[AttentionItemResponse]
    total: int
    page: int
    page_size: int


class DismissRequest(BaseModel):
    """Dismiss attention item request."""
    human_nonce: str = Field(..., min_length=1)


@router.get("", response_model=AttentionListResponse)
async def list_attention(
    kind: Optional[AttentionKind] = Query(None),
    dismissed: Optional[bool] = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AttentionListResponse:
    """List attention items (Inbox)."""
    stmt = (
        select(AttentionItem, Window.title, Window.session_id, Session.name)
        .join(Window, AttentionItem.window_id == Window.id)
        .join(Session, Window.session_id == Session.id)
    )
    
    if kind is not None:
        stmt = stmt.where(AttentionItem.kind == kind)
    if not dismissed:
        stmt = stmt.where(AttentionItem.dismissed_at.is_(None))
    
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await db.scalar(count_stmt) or 0
    
    stmt = stmt.order_by(AttentionItem.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(stmt)
    rows = result.all()
    
    items = [
        AttentionItemResponse(
            id=item.id,
            window_id=item.window_id,
            window_title=window_title,
            session_name=session_name,
            kind=item.kind,
            title=item.title,
            message=item.message,
            human_nonce=item.human_nonce,
            dismissed_at=item.dismissed_at.isoformat() if item.dismissed_at else None,
            created_at=item.created_at.isoformat(),
        )
        for item, window_title, _, session_name in rows
    ]
    
    return AttentionListResponse(items=items, total=total, page=page, page_size=page_size)


@router.post("/{item_id}/dismiss", response_model=AttentionItemResponse)
async def dismiss_attention(
    item_id: int,
    request: DismissRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AttentionItemResponse:
    """Dismiss an attention item with human nonce."""
    item = await db.get(AttentionItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Attention item not found")
    
    if item.human_nonce and item.human_nonce != request.human_nonce:
        raise HTTPException(status_code=403, detail="Invalid human nonce")
    
    if not item.human_nonce:
        raise HTTPException(status_code=403, detail="Item requires human nonce")
    
    from datetime import datetime, timezone
    item.dismissed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(item)
    
    # Get related info
    window = await db.get(Window, item.window_id)
    session = await db.get(Session, window.session_id) if window else None
    
    return AttentionItemResponse(
        id=item.id,
        window_id=item.window_id,
        window_title=window.title if window else None,
        session_name=session.name if session else "",
        kind=item.kind,
        title=item.title,
        message=item.message,
        human_nonce=item.human_nonce,
        dismissed_at=item.dismissed_at.isoformat(),
        created_at=item.created_at.isoformat(),
    )


@router.get("/stats/summary")
async def attention_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get attention summary counts by kind."""
    stmt = select(AttentionItem.kind, func.count(AttentionItem.id)).where(
        AttentionItem.dismissed_at.is_(None)
    ).group_by(AttentionItem.kind)
    result = await db.execute(stmt)
    counts = {row[0].value: row[1] for row in result.all()}
    
    return {
        "total": sum(counts.values()),
        "by_kind": counts,
    }
