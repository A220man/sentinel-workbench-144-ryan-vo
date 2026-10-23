# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

core-skeleton

## Roadmap

### core-skeleton — FastAPI + React skeleton with SQLite persistence

Status: done

Acceptance:
- FastAPI app runs at /api/health
- React app builds and serves
- SQLite database with models
- Docker compose with backend/frontend/Keycloak
- Basic pytest and vitest passing

Implementation: `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/core/database.py`, `backend/app/models/session.py`, `backend/app/models/user.py`, `backend/app/api/routes/health.py`, `backend/app/api/routes/sessions.py`, `backend/app/api/routes/windows.py`, `backend/app/api/routes/attention.py`, `backend/app/api/routes/auth.py`, `backend/app/api/deps.py`, `backend/app/services/agent.py`, `backend/app/services/privacy.py`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/components/Layout.tsx`, `frontend/src/components/Dashboard.tsx`, `frontend/src/components/Sessions.tsx`, `frontend/src/components/SessionDetail.tsx`, `frontend/src/components/Inbox.tsx`, `frontend/src/components/Settings.tsx`, `frontend/src/components/Login.tsx`, `frontend/src/components/ProtectedRoute.tsx`, `frontend/src/hooks/useAuthStore.ts`, `frontend/src/api/client.ts`, `frontend/src/types/api.ts`

Tests: `backend/tests/conftest.py`, `backend/tests/test_models.py`, `backend/tests/test_api.py`, `frontend/src/test/setup.ts`, `frontend/src/components/Login.test.tsx`, `frontend/src/components/Dashboard.test.tsx`, `frontend/src/components/Sessions.test.tsx`

### auth-oidc — OIDC authentication with Keycloak

Status: planned

Acceptance:
- Login/logout flow works
- Protected API endpoints
- Roles: viewer, operator, admin

### agent-sessions — Agent session management (CRUD + Inbox)

Status: planned

Acceptance:
- Create/list/get/update/delete agent sessions
- Inbox with attention items
- Agent state tracking

### privacy-mode — Privacy mode for masking sensitive text

Status: planned

Acceptance:
- Toggle masks secrets in UI
- Configurable regex rules
- Dock indicator shows privacy status

### spaces — Spaces for grouping sessions

Status: planned

Acceptance:
- Sessions have space label
- Move pane between sessions
- Sidebar groups by space

### quiet-mode — Quiet mode per pane (no Inbox items)

Status: planned

Acceptance:
- Per-pane quiet flag
- Suppresses finished/question/errored items
- CLI verb for runtime toggle

