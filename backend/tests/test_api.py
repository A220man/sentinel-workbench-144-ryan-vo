"""Tests for API routes."""
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.user import User, Role
from app.models.session import Session, Window, AgentState, AttentionItem, AttentionKind


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "environment" in data


class TestAuthEndpoints:
    @pytest.mark.asyncio
    async def test_login_demo_mode(self, client: AsyncClient, db_session):
        response = await client.post("/api/auth/login", json={
            "email": "newuser@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        
        # Verify user was created
        result = await db_session.execute(select(User).where(User.email == "newuser@example.com"))
        user = result.scalar_one_or_none()
        assert user is not None
        assert user.role == Role.OPERATOR

    @pytest.mark.asyncio
    async def test_get_me(self, client: AsyncClient, test_user: User):
        # Login first
        login_resp = await client.post("/api/auth/login", json={
            "email": test_user.email,
            "password": "password"
        })
        token = login_resp.json()["access_token"]
        
        # Get user info
        response = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["role"] == test_user.role.value

    @pytest.mark.asyncio
    async def test_unauthorized_without_token(self, client: AsyncClient):
        response = await client.get("/api/auth/me")
        assert response.status_code == 401


class TestSessionsEndpoints:
    @pytest.mark.asyncio
    async def test_list_sessions_empty(self, client: AsyncClient, test_user: User):
        login_resp = await client.post("/api/auth/login", json={"email": test_user.email, "password": "password"})
        token = login_resp.json()["access_token"]
        
        response = await client.get("/api/sessions", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_create_session(self, client: AsyncClient, test_user: User):
        login_resp = await client.post("/api/auth/login", json={"email": test_user.email, "password": "password"})
        token = login_resp.json()["access_token"]
        
        response = await client.post("/api/sessions", headers={"Authorization": f"Bearer {token}"}, json={
            "name": "New Session",
            "space": "testing"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Session"
        assert data["space"] == "testing"
        assert data["window_count"] == 0

    @pytest.mark.asyncio
    async def test_get_session(self, client: AsyncClient, test_user: User, test_session: Session):
        login_resp = await client.post("/api/auth/login", json={"email": test_user.email, "password": "password"})
        token = login_resp.json()["access_token"]
        
        response = await client.get(f"/api/sessions/{test_session.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_session.id
        assert data["name"] == test_session.name

    @pytest.mark.asyncio
    async def test_update_session(self, client: AsyncClient, test_user: User, test_session: Session):
        login_resp = await client.post("/api/auth/login", json={"email": test_user.email, "password": "password"})
        token = login_resp.json()["access_token"]
        
        response = await client.patch(f"/api/sessions/{test_session.id}", headers={"Authorization": f"Bearer {token}"}, json={
            "name": "Updated Session"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Session"

    @pytest.mark.asyncio
    async def test_delete_session(self, client: AsyncClient, test_user: User, test_session: Session):
        login_resp = await client.post("/api/auth/login", json={"email": test_user.email, "password": "password"})
        token = login_resp.json()["access_token"]
        
        response = await client.delete(f"/api/sessions/{test_session.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 204
        
        # Verify deleted
        get_resp = await client.get(f"/api/sessions/{test_session.id}", headers={"Authorization": f"Bearer {token}"})
        assert get_resp.status_code == 404

    @pytest.mark.asyncio
    async def test_list_spaces(self, client: AsyncClient, test_user: User, test_session: Session):
        login_resp = await client.post("/api/auth/login", json={"email": test_user.email, "password": "password"})
        token = login_resp.json()["access_token"]
        
        response = await client.get("/api/sessions/spaces/list", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert "testing" in data


class TestWindowsEndpoints:
    @pytest.mark.asyncio
    async def test_list_windows(self, client: AsyncClient, test_user: User, test_window: Window):
        login_resp = await client.post("/api/auth/login", json={"email": test_user.email, "password": "password"})
        token = login_resp.json()["access_token"]
        
        response = await client.get("/api/windows", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert data["items"][0]["id"] == test_window.id

    @pytest.mark.asyncio
    async def test_create_window(self, client: AsyncClient, test_user: User, test_session: Session):
        login_resp = await client.post("/api/auth/login", json={"email": test_user.email, "password": "password"})
        token = login_resp.json()["access_token"]
        
        response = await client.post("/api/windows", headers={"Authorization": f"Bearer {token}"}, json={
            "session_id": test_session.id,
            "workspace": 2,
            "index": 1,
            "title": "New Window"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["session_id"] == test_session.id
        assert data["workspace"] == 2
        assert data["title"] == "New Window"

    @pytest.mark.asyncio
    async def test_update_window_agent_state(self, client: AsyncClient, test_user: User, test_window: Window):
        login_resp = await client.post("/api/auth/login", json={"email": test_user.email, "password": "password"})
        token = login_resp.json()["access_token"]
        
        response = await client.patch(f"/api/windows/{test_window.id}", headers={"Authorization": f"Bearer {token}"}, json={
            "agent_state": "working"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["agent_state"] == "working"

    @pytest.mark.asyncio
    async def test_set_window_quiet(self, client: AsyncClient, test_user: User, test_window: Window):
        login_resp = await client.post("/api/auth/login", json={"email": test_user.email, "password": "password"})
        token = login_resp.json()["access_token"]
        
        response = await client.post(f"/api/windows/{test_window.id}/quiet", headers={"Authorization": f"Bearer {token}"}, params={"quiet": "true"})
        assert response.status_code == 200
        data = response.json()
        assert data["quiet"] is True

    @pytest.mark.asyncio
    async def test_move_window(self, client: AsyncClient, test_user: User, test_window: Window, test_session: Session):
        # Create another session
        from app.core.database import get_db
        from app.models.session import Session as SessionModel
        import asyncio
        
        login_resp = await client.post("/api/auth/login", json={"email": test_user.email, "password": "password"})
        token = login_resp.json()["access_token"]
        
        # Create target session
        create_resp = await client.post("/api/sessions", headers={"Authorization": f"Bearer {token}"}, json={
            "name": "Target Session"
        })
        target_session_id = create_resp.json()["id"]
        
        response = await client.post(
            f"/api/windows/{test_window.id}/move",
            headers={"Authorization": f"Bearer {token}"},
            params={"to_session_id": target_session_id, "to_workspace": 1, "to_index": 0}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == target_session_id


class TestAttentionEndpoints:
    @pytest.mark.asyncio
    async def test_list_attention_empty(self, client: AsyncClient, test_user: User):
        login_resp = await client.post("/api/auth/login", json={"email": test_user.email, "password": "password"})
        token = login_resp.json()["access_token"]
        
        response = await client.get("/api/attention", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_attention_summary(self, client: AsyncClient, test_user: User, test_window: Window):
        login_resp = await client.post("/api/auth/login", json={"email": test_user.email, "password": "password"})
        token = login_resp.json()["access_token"]
        
        # Create attention item
        from app.core.database import get_db
        from app.models.session import AttentionItem, AttentionKind
        from app.api.deps import get_current_user
        
        # Use db_session fixture
        from app.core.database import async_session_maker
        async with async_session_maker() as db:
            item = AttentionItem(
                window_id=test_window.id,
                kind=AttentionKind.FINISHED,
                title="Task done",
                human_nonce="test-nonce-123",
            )
            db.add(item)
            await db.commit()
        
        response = await client.get("/api/attention/stats/summary", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert "finished" in data["by_kind"]

    @pytest.mark.asyncio
    async def test_dismiss_attention(self, client: AsyncClient, test_user: User, test_window: Window):
        login_resp = await client.post("/api/auth/login", json={"email": test_user.email, "password": "password"})
        token = login_resp.json()["access_token"]
        
        # Create attention item with nonce
        from app.core.database import async_session_maker
        from app.models.session import AttentionItem, AttentionKind
        async with async_session_maker() as db:
            item = AttentionItem(
                window_id=test_window.id,
                kind=AttentionKind.FINISHED,
                title="Task done",
                human_nonce="test-nonce-123",
            )
            db.add(item)
            await db.commit()
            await db.refresh(item)
            item_id = item.id
        
        response = await client.post(
            f"/api/attention/{item_id}/dismiss",
            headers={"Authorization": f"Bearer {token}"},
            json={"human_nonce": "test-nonce-123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["dismissed_at"] is not None

    @pytest.mark.asyncio
    async def test_dismiss_wrong_nonce(self, client: AsyncClient, test_user: User, test_window: Window):
        login_resp = await client.post("/api/auth/login", json={"email": test_user.email, "password": "password"})
        token = login_resp.json()["access_token"]
        
        from app.core.database import async_session_maker
        from app.models.session import AttentionItem, AttentionKind
        async with async_session_maker() as db:
            item = AttentionItem(
                window_id=test_window.id,
                kind=AttentionKind.FINISHED,
                title="Task done",
                human_nonce="correct-nonce",
            )
            db.add(item)
            await db.commit()
            await db.refresh(item)
            item_id = item.id
        
        response = await client.post(
            f"/api/attention/{item_id}/dismiss",
            headers={"Authorization": f"Bearer {token}"},
            json={"human_nonce": "wrong-nonce"}
        )
        assert response.status_code == 403
