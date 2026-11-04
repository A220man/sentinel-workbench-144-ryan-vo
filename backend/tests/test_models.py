"""Tests for database models."""
import pytest
from sqlalchemy import select
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, Role
from app.models.session import (
    Session, Window, AgentState, AgentStateHistory,
    AttentionItem, AttentionKind
)


class TestUserModel:
    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession):
        user = User(email="test@example.com", username="testuser", role=Role.OPERATOR)
        db_session.add(user)
        await db_session.commit()
        
        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.role == Role.OPERATOR
        assert user.is_active is True
        assert user.created_at is not None

    @pytest.mark.asyncio
    async def test_user_unique_email(self, db_session: AsyncSession):
        user1 = User(email="test@example.com", username="user1")
        user2 = User(email="test@example.com", username="user2")
        db_session.add(user1)
        await db_session.commit()
        
        db_session.add(user2)
        with pytest.raises(Exception):
            await db_session.commit()


class TestSessionModel:
    @pytest.mark.asyncio
    async def test_create_session(self, db_session: AsyncSession):
        session = Session(name="Test Session", space="testing")
        db_session.add(session)
        await db_session.commit()
        
        assert session.id is not None
        assert session.name == "Test Session"
        assert session.space == "testing"
        assert session.created_at is not None

    @pytest.mark.asyncio
    async def test_session_space_defaults_to_empty(self, db_session: AsyncSession):
        session = Session(name="No Space")
        db_session.add(session)
        await db_session.commit()
        
        assert session.space == ""


class TestWindowModel:
    @pytest.mark.asyncio
    async def test_create_window(self, db_session: AsyncSession, test_session: Session):
        window = Window(
            session_id=test_session.id,
            workspace=1,
            index=0,
            title="Test Window",
            agent_state=AgentState.WORKING,
        )
        db_session.add(window)
        await db_session.commit()
        
        assert window.id is not None
        assert window.session_id == test_session.id
        assert window.agent_state == AgentState.WORKING
        assert window.completion_seq == 0
        assert window.quiet is False

    @pytest.mark.asyncio
    async def test_window_agent_state_default(self, db_session: AsyncSession, test_session: Session):
        window = Window(session_id=test_session.id)
        db_session.add(window)
        await db_session.commit()
        
        assert window.agent_state == AgentState.UNKNOWN


class TestAgentStateHistory:
    @pytest.mark.asyncio
    async def test_create_history(self, db_session: AsyncSession, test_window: Window):
        history = AgentStateHistory(
            window_id=test_window.id,
            from_state=AgentState.IDLE,
            to_state=AgentState.WORKING,
        )
        db_session.add(history)
        await db_session.commit()
        
        assert history.id is not None
        assert history.from_state == AgentState.IDLE
        assert history.to_state == AgentState.WORKING
        assert history.created_at is not None


class TestAttentionItem:
    @pytest.mark.asyncio
    async def test_create_attention_item(self, db_session: AsyncSession, test_window: Window):
        item = AttentionItem(
            window_id=test_window.id,
            kind=AttentionKind.FINISHED,
            title="Task completed",
            message="Agent finished working",
        )
        db_session.add(item)
        await db_session.commit()
        
        assert item.id is not None
        assert item.kind == AttentionKind.FINISHED
        assert item.dismissed_at is None
        assert item.created_at is not None

    @pytest.mark.asyncio
    async def test_all_attention_kinds(self, db_session: AsyncSession, test_window: Window):
        for kind in AttentionKind:
            item = AttentionItem(
                window_id=test_window.id,
                kind=kind,
                title=f"{kind.value} item",
            )
            db_session.add(item)
        await db_session.commit()
        
        result = await db_session.execute(select(AttentionItem).where(AttentionItem.window_id == test_window.id))
        items = result.scalars().all()
        assert len(items) == len(AttentionKind)
