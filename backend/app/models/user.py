"""User and role models."""
import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, Index
from sqlalchemy.orm import relationship
from app.core.database import Base


class Role(str, enum.Enum):
    """User role enumeration."""
    VIEWER = "viewer"
    OPERATOR = "operator"
    ADMIN = "admin"


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=True, index=True)
    full_name = Column(String(255), nullable=True)
    role = Column(Enum(Role), default=Role.VIEWER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    oidc_sub = Column(String(255), unique=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role={self.role})>"