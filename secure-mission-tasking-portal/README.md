# Secure Mission Tasking Portal (Portfolio Replica)

> **Portfolio note (DoD-style, sanitized):** This project is intentionally designed to resemble patterns used in classified tasking / mission support systems (RBAC, audit, immutable logging, hardened headers, rate limiting, config controls). It is **not** a copy of any classified system and contains **no** classified logic, data, endpoints, or workflows. It exists solely to demonstrate end‑to‑end engineering practices in a security‑sensitive environment.

## What this app is
A small Flask-based tasking portal API that supports:
- **Role-based access control (RBAC)**: `admin`, `operator`, `auditor`
- **JWT authentication** with token refresh support
- **Task CRUD** (create/update/assign/close) with role restrictions
- **Audit logging** for security-relevant actions (who/what/when/request-id)
- **Security hardening**: security headers, strict config, rate limiting
- **Operational hygiene**: structured logs, health endpoint, database migrations style layout

## Tech stack
- Python 3.11+
- Flask (application factory + blueprints)
- SQLAlchemy + SQLite (local dev)
- Flask-JWT-Extended (auth)
- Flask-Limiter (rate limiting)
- Flask-Talisman (security headers)
- Marshmallow (request validation / serialization)
- Pytest (unit tests)

## Quick start
```bash
cd secure-mission-tasking-portal
python -m venv .venv
source .venv/bin/activate   # (Windows: .venv\Scripts\activate)
pip install -r requirements.txt

# Create .env from template
cp .env.example .env

# Initialize DB + seed users
flask --app wsgi.py init-db
flask --app wsgi.py seed-users

# Run
flask --app wsgi.py run
```

The API will be at `http://127.0.0.1:5000`.

## Default users (seeded)
- admin: `admin` / `Admin!234`
- operator: `operator` / `Operator!234`
- auditor: `auditor` / `Auditor!234`

> Change these immediately if you deploy anywhere besides local dev.

## Try it (curl)
### 1) Login
```bash
curl -s -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin!234"}' | python -m json.tool
```

Copy the `access_token` and use it below:

### 2) Create a task (admin only)
```bash
TOKEN="PASTE_ACCESS_TOKEN"
curl -s -X POST http://127.0.0.1:5000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Rotate service credentials","priority":"high","assigned_to":"operator"}' | python -m json.tool
```

### 3) List tasks (admin/operator/auditor)
```bash
curl -s http://127.0.0.1:5000/api/tasks \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

### 4) Audit events (auditor/admin)
```bash
curl -s http://127.0.0.1:5000/api/audit \
  -H "Authorization: Bearer $TOKEN" | python -m json.tool
```

## Security model (high-level)
- Auth uses **short-lived access tokens** and optional refresh tokens.
- RBAC enforced by decorators at the route layer.
- Request correlation uses `X-Request-Id` (or auto-generated).
- Audit entries are created for login, task mutations, and privileged reads.

## Project layout
```
secure-mission-tasking-portal/
  app/
    __init__.py
    config.py
    extensions.py
    models.py
    schemas.py
    security.py
    audit.py
    blueprints/
      auth.py
      tasks.py
      audit_api.py
      health.py
  tests/
  migrations/        # placeholder for real-world Alembic usage
  wsgi.py
  requirements.txt
  .env.example
  .gitignore
  .github/workflows/ci.yml
```

## Running tests
```bash
pytest -q
```

## Notes for GitHub
This repo is meant to show:
- secure-by-default API patterns
- clear code comments and documentation
- practical testing and CI scaffolding

If you’d like, you can extend this with:
- Alembic migrations
- OpenAPI / Swagger documentation
- Containerization (Dockerfile) and IaC (Terraform) for a full portfolio story
