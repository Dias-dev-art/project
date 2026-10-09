# PR Security Scanner — Complete Setup Guide

## Phase 1: Prerequisites (One-time)

### 1.1 Verify Prerequisites
```bash
# Python 3.11+
python --version

# Node.js 20+
node --version
npm --version

# Docker & Docker Compose
docker --version
docker compose --version
```

### 1.2 GitHub App & Credentials
1. Go to **GitHub Settings** → **Developer settings** → **GitHub Apps**
2. Create a new GitHub App with:
   - **Webhook URL:** `https://your-domain.com/api/v1/webhooks/github`
   - **Webhook Secret:** Generate a secure string (use `openssl rand -hex 32`)
   - **Permissions:** 
     - `pull_requests` (read)
     - `contents` (read)
   - **Events:** `pull_request`
3. Copy:
   - **App ID** → `GITHUB_APP_ID`
   - **Private Key** → `GITHUB_APP_PRIVATE_KEY` (save as `.pem`)
   - **Webhook Secret** → `GITHUB_WEBHOOK_SECRET`

### 1.3 Claude API Key
1. Get your API key from [console.anthropic.com](https://console.anthropic.com)
2. Copy it → `ANTHROPIC_API_KEY`

---

## Phase 2: Local Environment Setup

### 2.1 Clone/Enter Project
```bash
cd /path/to/pr-security-scanner
```

### 2.2 Configure Environment
```bash
# Copy template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

Fill in:
```env
GITHUB_APP_ID=123456
GITHUB_APP_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n..."
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
ANTHROPIC_API_KEY=sk-ant-...
```

### 2.3 Start Docker Containers
```bash
# Build and start (first time takes 2-3 minutes)
docker compose up --build

# View logs from all services:
docker compose logs -f

# In new terminal, verify services are healthy
```

### 2.4 Verify Services
Open these in your browser or terminal:
- **API Docs:** http://localhost:8000/docs
- **API Health:** http://localhost:8000/api/v1/health
- **Frontend:** http://localhost:5173
- **PostgreSQL:** localhost:5432 (user: `scanner`, password: `scanner`)

---

## Phase 3: Database Setup

### 3.1 Create First Migration
```bash
# While Docker is running, in a new terminal:
docker compose exec backend alembic revision --autogenerate -m "init"

# Output: Generating migration /app/migrations/versions/<timestamp>_init.py
```

### 3.2 Apply Migration
```bash
docker compose exec backend alembic upgrade head

# Expected: INFO [alembic.runtime.migration] Running upgrade -> <revision>, done
```

### 3.3 Verify Database
```bash
docker compose exec db psql -U scanner -d scanner -c "\dt"

# Should show:
#  public | findings | table | app
#  public | scans    | table | app
```

---

## Phase 4: Frontend Setup

### 4.1 Install Dependencies (first time only)
```bash
cd frontend
npm install

# Generates package-lock.json (commit this!)
git add package-lock.json
git commit -m "chore: add npm lockfile"

cd ..
```

### 4.2 Verify Frontend Build
```bash
docker compose exec frontend npm run build

# Should complete with: ✓ built in 1.2s
```

### 4.3 Run Frontend Tests
```bash
docker compose exec frontend npm test

# Should pass the placeholder test
```

---

## Phase 5: Backend Testing & Development

### 5.1 Run Backend Tests
```bash
docker compose exec backend pytest -v

# Expected: 2 passed in 0.12s
```

### 5.2 Check Linting
```bash
docker compose exec backend ruff check .

# Should have no errors
```

### 5.3 View API Logs
```bash
# Attach to backend logs (Ctrl+C to detach):
docker compose logs -f backend

# Or one-shot:
docker compose logs backend
```

---

## Phase 6: Development Workflow

### 6.1 Backend Development
The backend container runs with `--reload`, so changes are reflected instantly.

```bash
# Example: Add new endpoint to backend/app/api/v1/example.py
# Save file → API reloads automatically → test at http://localhost:8000/docs
```

**Useful commands:**
```bash
# Run tests on watch mode:
docker compose exec backend pytest -v --tb=short -k test_

# Interactive Python shell:
docker compose exec backend python

# Database shell:
docker compose exec db psql -U scanner -d scanner

# Run specific test:
docker compose exec backend pytest tests/unit/test_security.py -v
```

### 6.2 Frontend Development
The frontend runs Vite dev server with hot module replacement.

```bash
# Changes to frontend/src/** auto-reload in browser
# Open http://localhost:5173 and start editing
```

**Useful commands:**
```bash
# Watch mode tests:
docker compose exec frontend npm test -- --watch

# Build for production:
docker compose exec frontend npm run build

# Type check:
docker compose exec frontend npm run typecheck

# View logs:
docker compose logs -f frontend
```

### 6.3 Database Migrations
After modifying models in `backend/app/models/`:

```bash
# Auto-generate migration:
docker compose exec backend alembic revision --autogenerate -m "add user_accounts"

# Review the generated file in backend/migrations/versions/
# Edit if needed (e.g., remove irrelevant changes)

# Apply:
docker compose exec backend alembic upgrade head

# Rollback (if needed):
docker compose exec backend alembic downgrade -1
```

---

## Phase 7: Connecting GitHub Webhook

### 7.1 Local Tunnel Setup
GitHub webhooks require a public URL. Use **ngrok** for local testing:

```bash
# Install: https://ngrok.com/download
# Start tunnel:
ngrok http 8000

# Copy the public URL (e.g., https://1234-5678-9012.ngrok.io)
```

### 7.2 Update GitHub App
1. Go to your GitHub App settings
2. Update **Webhook URL:** `https://your-ngrok-url.ngrok.io/api/v1/webhooks/github`
3. Install the app on a test repository
4. Create a test PR

### 7.3 Check Webhook Logs
```bash
docker compose logs -f backend | grep webhook

# You should see the webhook request logged
```

---

## Phase 8: CI/CD Pipeline

### 8.1 GitHub Actions (Automatic)
On every push to `main` or PR, `.github/workflows/ci.yml` runs:
- ✅ Backend: ruff lint + pytest
- ✅ Frontend: eslint + typecheck + tests + build

### 8.2 Manual Pre-Commit Check
```bash
# Run before committing:

# Backend:
docker compose exec backend ruff check .
docker compose exec backend pytest

# Frontend:
docker compose exec frontend npm run lint
docker compose exec frontend npm run typecheck
docker compose exec frontend npm test
docker compose exec frontend npm run build
```

### 8.3 Deploy on Release
```bash
# Create a version tag:
git tag -a v0.1.0 -m "Initial release"

# Push:
git push origin v0.1.0

# GitHub Actions automatically:
# 1. Builds Docker images (backend + frontend)
# 2. Pushes to ghcr.io
# 3. Awaits your custom deploy job
```

---

## Phase 9: Implementing Security Scanning

### 9.1 Add Scanner Rules
Edit `backend/app/services/scanner.py`:

```python
import re

def scan_diff(diff: str) -> list[dict]:
    findings = []
    
    # Rule 1: Hardcoded passwords
    if re.search(r'(password|secret|api[_-]?key)\s*=\s*["\']?\w{8,}', diff, re.I):
        findings.append({
            "rule_id": "hardcoded-secret",
            "severity": "critical",
            "message": "Potential hardcoded secret detected",
            "file_path": "multiple",
            "line": None,
        })
    
    # Rule 2: SQL injection patterns
    if re.search(r'execute\s*\(\s*["\'].*%s', diff, re.I):
        findings.append({
            "rule_id": "sql-injection",
            "severity": "high",
            "message": "Potential SQL injection vulnerability",
            "file_path": "unknown",
            "line": None,
        })
    
    return findings
```

### 9.2 Add Background Job
Edit `backend/app/api/v1/webhooks.py`:

```python
@router.post("/github", status_code=202)
async def github_webhook(
    request: Request,
    background: BackgroundTasks,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    body = await request.body()
    if not verify_github_signature(settings.github_webhook_secret, body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="invalid signature")
    
    if x_github_event == "pull_request":
        payload = (await request.json())
        background.add_task(run_scan, db, payload)
    
    return {"accepted": True}

async def run_scan(db: AsyncSession, payload: dict):
    from app.models.scan import Scan, Finding
    from app.services.scanner import scan_diff
    from app.services.github import fetch_pr_diff
    from app.services.claude import explain_finding
    
    repo = payload["repository"]["full_name"]
    pr_num = payload["pull_request"]["number"]
    head_sha = payload["pull_request"]["head"]["sha"]
    
    # Create scan record
    scan = Scan(repo_full_name=repo, pr_number=pr_num, head_sha=head_sha, status="running")
    db.add(scan)
    await db.commit()
    
    try:
        # Fetch PR diff
        diff = await fetch_pr_diff("token", repo, pr_num)  # TODO: get actual token
        
        # Scan the diff
        findings_data = scan_diff(diff)
        
        # Get explanations from Claude
        for finding in findings_data:
            explanation = await explain_finding(
                finding["rule_id"], finding["message"], diff[:500]
            )
            f = Finding(
                scan_id=scan.id,
                rule_id=finding["rule_id"],
                severity=finding["severity"],
                file_path=finding.get("file_path", "unknown"),
                line=finding.get("line"),
                message=finding["message"],
                explanation=explanation,
            )
            db.add(f)
        
        scan.status = "completed"
        await db.commit()
    except Exception as e:
        scan.status = "failed"
        await db.commit()
        raise
```

---

## Phase 10: Production Deployment

### 10.1 Deploy with docker-compose.prod.yml
```bash
# On production server:
scp .env user@server:/app/.env.prod
scp docker-compose.prod.yml user@server:/app/

ssh user@server
cd /app

# Load production env and start:
export $(cat .env.prod | xargs)
docker compose -f docker-compose.prod.yml up -d --build

# Verify:
curl http://localhost:8000/api/v1/health
```

### 10.2 Production Environment
```env
ENVIRONMENT=production
SECRET_KEY=<generate-with-: python -c "import secrets; print(secrets.token_urlsafe(32))">
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db-host:5432/scanner
CORS_ORIGINS=https://yourdomain.com
VITE_API_URL=https://api.yourdomain.com
```

### 10.3 Reverse Proxy (nginx)
```nginx
upstream api {
  server backend:8000;
}

server {
  listen 443 ssl http2;
  server_name api.yourdomain.com;
  ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
  ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
  
  location / {
    proxy_pass http://api;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto https;
  }
}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Port 5173 in use** | `lsof -i :5173` → `kill -9 <PID>` |
| **Port 8000 in use** | `docker compose down` → `docker compose up` |
| **DB connection refused** | Wait 10 seconds, check: `docker compose logs db` |
| **Alembic fails** | Delete migration files (keep `__init__.py`), regenerate |
| **npm install fails** | Run in `frontend/` directory locally first |
| **GitHub webhook 401** | Verify `GITHUB_WEBHOOK_SECRET` in `.env` matches GitHub App |
| **Frontend shows blank page** | Check `docker compose logs frontend` and browser console |
| **API 500 errors** | Check `docker compose logs backend` for stack trace |

---

## Checklist: First Run

- [ ] Run `cp .env.example .env` and fill credentials
- [ ] Run `docker compose up --build` (wait for healthy status)
- [ ] Visit http://localhost:8000/docs and http://localhost:5173
- [ ] Run `docker compose exec backend alembic revision --autogenerate -m "init"`
- [ ] Run `docker compose exec backend alembic upgrade head`
- [ ] Run `docker compose exec backend pytest` (2 passed)
- [ ] Run `cd frontend && npm install && cd ..`
- [ ] Run `docker compose exec frontend npm test` (1 passed)
- [ ] Commit `frontend/package-lock.json`
- [ ] Set up ngrok and test webhook
- [ ] Add scanner rules to `backend/app/services/scanner.py`
- [ ] Implement background job in `backend/app/api/v1/webhooks.py`
- [ ] Build frontend UI for dashboard
- [ ] Deploy to production environment

---

## Next: Build the Core Features

1. **Scanner Rules** — Add security checks (secrets, SQL injection, etc.)
2. **Claude Integration** — Explain findings with explanations
3. **Background Jobs** — Process webhooks asynchronously
4. **Dashboard UI** — Show scan results in React
5. **PR Comments** — Post findings back to GitHub

Good luck! 🚀
