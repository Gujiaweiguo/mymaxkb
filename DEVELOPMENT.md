# Development Environment

## Architecture

- **PostgreSQL + Redis**: Docker Compose (`docker-compose.dev.yml`)
- **Backend**: Local Python virtual environment (`.venv`)
- **Frontend**: Local Node.js environment (`ui/`)

This is the default development convention for this repo:

1. Start only PostgreSQL and Redis with Docker Compose.
2. Run Django locally from the repo `.venv`.
3. Run Vite locally from `ui/`.
4. Run Playwright against the local frontend and backend.

## Quick Start

### 1. Start Infrastructure (Docker Compose)

```bash
docker compose -f docker-compose.dev.yml up -d
```

### 2. Prepare local app env

```bash
cp .env.local-dev.example .env.local-dev
# Fill in real local secrets for SECRET_KEY / HMAC / RSA values.
```

### 3. Start Backend

```bash
set -a
source .env.local-dev
set +a
. .venv/bin/activate
python main.py dev web
```

The default backend workflow keeps `MAXKB_ENABLE_LOCAL_MODEL=False`, so the normal web/task stack does not auto-start the standalone local-model process.

### 3b. Optional local-model process

Start this only when you are explicitly working on local-model functionality:

```bash
set -a
source .env.local-dev
set +a
. .venv/bin/activate
python main.py dev local_model
```

If you want `python main.py start web` or `python main.py start all` to include the standalone local-model subprocess, set:

```bash
export MAXKB_ENABLE_LOCAL_MODEL=True
```

### 4. Start Frontend

```bash
cd ui
npm run dev
```

### 5. Run E2E Tests

```bash
cd ui
npx playwright test
```

## Quick Self-Check (Port 3080)

Before starting new development work, run this minimal check to confirm local alignment:

```bash
# 1) Backend (expects http://127.0.0.1:3080/)
set -a && source .env.local-dev && set +a
.venv/bin/python main.py dev web

# 2) Frontend quality checks
cd ui
npm run type-check && npm run lint && npm run test

# 3) Manual smoke check
# Open /admin/ and /chat/ in your local browser
```

## Testing Workflow

### Backend tests

Use the repo-root Django command after loading `.env.local-dev`:

```bash
set -a
source .env.local-dev
set +a
.venv/bin/python apps/manage.py test --verbosity=1 --noinput
```

### Runtime safety checks

Use the focused runtime-safety Django test module after loading `.env.local-dev`:

```bash
set -a
source .env.local-dev
set +a
MAXKB_ALLOWED_HOSTS=127.0.0.1,localhost,testserver \
.venv/bin/python apps/manage.py test test_runtime_safety --verbosity=1 --noinput
```

### Frontend unit and component tests

```bash
cd ui
npm run test
npm run type-check
npm run lint
```

### E2E rerun guidance

Playwright starts the two Vite frontends automatically, but it still requires the backend on port `3080` plus PostgreSQL and Redis.

```bash
set -a
source .env.local-dev
set +a
.venv/bin/python main.py dev web
```

Then run:

```bash
cd ui
npx playwright test
```

Note: the remote-backed chat spec depends on `SILICONCLOUD_API_KEY` from `.env.local-dev`. Without it, that chat scenario is skipped while the rest of the suite can still run.

### CI alignment

CI is expected to use the same test layers and command shapes as local verification:

- backend: `python apps/manage.py test --verbosity=1 --noinput`
- runtime safety: `MAXKB_ALLOWED_HOSTS=127.0.0.1,localhost,testserver python apps/manage.py test test_runtime_safety --verbosity=1 --noinput`
- frontend: `npm run test`, `npm run type-check`, `npm run lint`
- advisory E2E: `npx playwright test --grep-invert @deferred`

Use `MAXKB_*` environment variables in CI so the workflow matches the repo's real Django configuration path.

### Required vs advisory CI signals

- **Required baseline**: `Backend Tests`, `Runtime Safety Checks`, and `Frontend Tests`
- **Advisory baseline**: `E2E Tests (Advisory)`
- **Deferred E2E coverage**: Playwright scenarios tagged `@deferred` stay out of the advisory CI run until they are stable and no longer depend on external credentials or non-deterministic setup

### CI gate to local reproduction map

| CI gate | Local command | Prerequisites |
|---------|---------------|---------------|
| Backend Tests | `.venv/bin/python apps/manage.py test --verbosity=1 --noinput` | Load `.env.local-dev`, start PostgreSQL and Redis |
| Runtime Safety Checks | `MAXKB_ALLOWED_HOSTS=127.0.0.1,localhost,testserver .venv/bin/python apps/manage.py test test_runtime_safety --verbosity=1 --noinput` | Load `.env.local-dev`, start PostgreSQL and Redis |
| Frontend Tests | `cd ui && npm run type-check && npm run lint && npm run test` | Install frontend dependencies |
| E2E Tests (Advisory) | `cd ui && npx playwright test --grep-invert @deferred` | Backend running locally, PostgreSQL, Redis, frontend dependencies |

Initial Playwright classification:

- `@advisory`: login, entry routing, workspace, user management, application, and knowledge flows
- `@deferred`: remote-backed chat flow requiring `SILICONCLOUD_API_KEY`

Promotion criteria for moving an E2E scenario into the required baseline:

1. The scenario passes consistently in CI without external manual setup.
2. The scenario does not require third-party credentials that are intentionally absent from the default CI contract.
3. The scenario protects a critical user journey that is not already covered well enough by backend or frontend required gates.
4. The scenario has run stably as advisory before being promoted to a required status check.

Note: local development commonly uses a Redis password from `.env.local-dev`, while the GitHub Actions Redis service runs without auth. CI keeps `MAXKB_REDIS_PASSWORD=''` intentionally so the workflow matches the unauthenticated service container it starts.

## Services

| Service | Port | Credentials |
|---------|------|-------------|
| PostgreSQL | 5432 | User: `maxkb`, Password: `maxkb123`, DB: `maxkb` |
| Redis | 6379 | Password: `maxkb123` |
| Backend | 3080 | - |
| Frontend | 5173 | - |

## Environment Variables

Use `.env.local-dev` for the local-backend workflow. The committed `.env` remains for full Docker Compose startup.

Local development keeps `MAXKB_DEBUG=True` and can use the local `MAXKB_ALLOWED_HOSTS` example value from `.env.local-dev.example`. Deployable environments should set `MAXKB_ALLOWED_HOSTS` explicitly to the real hostnames or IPs they serve.

`MAXKB_ENABLE_LOCAL_MODEL` is an explicit opt-in switch. Keep it `False` for the default web/task workflow, and turn it on only when you want the local-model subprocess to be part of startup.

Packaging is unchanged in this batch: heavyweight local-model dependencies still live in the shared Python environment. This change isolates the runtime contract, while dependency-profile isolation is deferred.

If your local setup previously used backend `8080`, update `.env.local-dev` to `MAXKB_DEV_PORT=3080` so frontend proxy and backend defaults stay aligned.

```env
MAXKB_CONFIG_TYPE=ENV
MAXKB_DB_HOST=127.0.0.1
MAXKB_DB_PORT=5432
MAXKB_DB_USER=maxkb
MAXKB_DB_PASSWORD=maxkb123
MAXKB_REDIS_HOST=127.0.0.1
MAXKB_REDIS_PORT=6379
MAXKB_REDIS_PASSWORD=maxkb123
MAXKB_DEFAULT_PASSWORD=TestPassword123!
MAXKB_DEV_HOST=127.0.0.1
MAXKB_DEV_PORT=3080
```

## Stopping Services

```bash
docker compose -f docker-compose.dev.yml down
```

## Cleaning Up

```bash
docker compose -f docker-compose.dev.yml down -v
```

## Troubleshooting

### PostgreSQL Connection Issues

1. Check if PostgreSQL is running: `docker ps | grep postgres`
2. Check logs: `docker logs maxkb-postgres`
3. Verify connection: `psql -h localhost -U maxkb -d maxkb`

### Redis Connection Issues

1. Check if Redis is running: `docker ps | grep redis`
2. Check logs: `docker logs maxkb-redis`
3. Test connection: `redis-cli -a maxkb123 ping`

### Backend Won't Start

1. Ensure `.env.local-dev` is loaded before starting Django
2. Ensure `/opt/maxkb/logs` and `/opt/code/mymaxkb/data/celery_task` are writable
3. Ensure Docker Compose PostgreSQL and Redis are healthy
4. Run migrations: `python main.py upgrade_db`

### Frontend Won't Start

1. Install dependencies: `cd ui && npm install`
2. Check Node.js version: `node --version` (should be 20+)
3. Clear cache: `npm cache clean --force`
