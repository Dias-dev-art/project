# PR Security Scanner

SaaS app that scans GitHub pull requests for security issues and uses Claude to explain findings and suggest fixes.

## Stack
- **Backend:** FastAPI (Python 3.11+), SQLAlchemy + Alembic
- **Frontend:** React 18 + TypeScript (Vite)
- **Database:** PostgreSQL 16
- **Integrations:** GitHub API (webhooks + App), Claude API

## Structure
```
backend/    FastAPI app, migrations, tests
frontend/   React app
.github/    CI/CD workflows
```

## Quick start (local dev)
```bash
cp .env.example .env      # fill in GitHub + Anthropic credentials
docker compose up --build
```
- API: http://localhost:8000 (docs at `/docs`)
- Web: http://localhost:5173

## Migrations
```bash
docker compose exec backend alembic revision --autogenerate -m "message"
docker compose exec backend alembic upgrade head
```

## Tests
```bash
docker compose exec backend pytest
docker compose exec frontend npm test
```

## Production
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

## How it works
1. GitHub sends a `pull_request` webhook to `/api/v1/webhooks/github`.
2. Backend fetches the PR diff and runs security checks.
3. Findings are explained by Claude and stored in PostgreSQL.
4. Results are shown in the dashboard and optionally posted as a PR comment.
