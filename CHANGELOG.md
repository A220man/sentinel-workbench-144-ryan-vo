# Changelog

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-10-23

### Added
- Initial release of Sentinel Workbench
- FastAPI backend with SQLite persistence (SQLAlchemy + async)
- React + TypeScript + Vite frontend with responsive UI
- Session management: create, list, update, delete sessions
- Space grouping for sessions
- Window/pane management with 9 workspaces per session
- Cross-session window move with crash-safe ordering
- Agent state tracking: unknown, idle, working, done, needs_input, errored
- Agent state history with timestamps
- Inbox (attention system) with kinds: finished, question, errored, approval
- Human nonce required for dismissal
- Quiet mode per window to suppress Inbox noise
- Privacy mode with built-in detectors (secret, email, phone, card, iban, ip)
- Custom regex patterns for privacy mode
- Allow-list for public hosts
- OIDC authentication via Keycloak (authorization code + PKCE)
- Demo mode for local development
- Role-based access: viewer, operator, admin
- JWT tokens with HttpOnly SameSite cookies
- Docker Compose with backend, frontend, Keycloak
- Health checks for all services
- 14 backend tests (models, API endpoints, auth)
- 3 frontend tests (Login, Dashboard, Sessions)
- Comprehensive README with architecture diagram
- API documentation
- MIT License
