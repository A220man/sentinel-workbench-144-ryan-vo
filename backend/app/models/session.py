"""Session and window models."""
import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum,
    Index,
    Boolean,
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class AgentState(str, enum.Enum):
    """Agent state enumeration."""
    UNKNOWN = "unknown"
    IDLE = "idle"
    WORKING = "working"
    DONE = "done"
    NEEDS_INPUT = "needs_input"
    ERRORED = "errored"


class Session(Base):
    """Session model - a collection of workspaces/windows."""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    space = Column(String(255), nullable=True, index=True, default="")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    windows = relationship("Window", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Session(id={self.id}, name='{self.name}', space='{self.space}')>"


class Window(Base):
    """Window/pane model within a session workspace."""
    __tablename__ = "windows"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    workspace = Column(Integer, nullable=False, default=1)
    index = Column(Integer, nullable=False, default=0)
    title = Column(String(255), nullable=True)
    command = Column(Text, nullable=True)
    cwd = Column(String(512), nullable=True)
    agent_state = Column(Enum(AgentState), default=AgentState.UNKNOWN, nullable=False, index=True)
    completion_seq = Column(Integer, default=0, nullable=False)
    quiet = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    session = relationship("Session", back_populates="windows")
    attention_items = relationship("AttentionItem", back_populates="window", cascade="all, delete-orphan")
    state_history = relationship("AgentStateHistory", back_populates="window", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index("ix_windows_session_workspace_index", "session_id", "workspace", "index"),
    )
    
    def __repr__(self) -> str:
        return f"<Window(id={self.id}, session_id={self.session_id}, workspace={self.workspace}, index={self.index}, agent_state={self.agent_state})>"


class AgentStateHistory(Base):
    """History of agent state transitions for a window."""
    __tablename__ = "agent_state_history"
    
    id = Column(Integer, primary_key=True, index=True)
    window_id = Column(Integer, ForeignKey("windows.id", ondelete="CASCADE"), nullable=False, index=True)
    from_state = Column(Enum(AgentState), nullable=False)
    to_state = Column(Enum(AgentState), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    
    window = relationship("Window", back_populates="state_history")
    
    def __repr__(self) -> str:
        return f"<AgentStateHistory(id={self.id}, window_id={self.window_id}, {self.from_state} -> {self.to_state})>"


class AttentionKind(str, enum.Enum):
    """Attention item kinds."""
    FINISHED = "finished"
    QUESTION = "question"
    ERRORED = "errored"
    APPROVAL = "approval"


class AttentionItem(Base):
    """Inbox attention item for a window."""
    __tablename__ = "attention_items"
    
    id = Column(Integer, primary_key=True, index=True)
    window_id = Column(Integer, ForeignKey("windows.id", ondelete="CASCADE"), nullable=False, index=True)
    kind = Column(Enum(AttentionKind), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=True)
    human_nonce = Column(String(64), nullable=True)
    dismissed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True)
    
    window = relationship("Window", back_populates="attention_items")
    
    def __repr__(self) -> str:
        return f"<AttentionItem(id={self.id}, window_id={self.window_id}, kind={self.kind}, title='{self.title}')>"