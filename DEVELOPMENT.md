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

## Testing Workflow

### Backend tests

Use the repo-root Django command after loading `.env.local-dev`:

```bash
set -a
source .env.local-dev
set +a
.venv/bin/python apps/manage.py test --verbosity=1 --noinput
```

### Frontend unit and component tests

```bash
cd ui
npm run test
npm run type-check
npm run lint
```

### E2E rerun guidance

Playwright starts the two Vite frontends automatically, but it still requires the backend on port `8080` plus PostgreSQL and Redis.

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
- frontend: `npm run test`, `npm run type-check`, `npm run lint`
- E2E: `npx playwright test`

Use `MAXKB_*` environment variables in CI so the workflow matches the repo's real Django configuration path.

## Services

| Service | Port | Credentials |
|---------|------|-------------|
| PostgreSQL | 5432 | User: `maxkb`, Password: `maxkb123`, DB: `maxkb` |
| Redis | 6379 | Password: `maxkb123` |
| Backend | 8080 | - |
| Frontend | 5173 | - |

## Environment Variables

Use `.env.local-dev` for the local-backend workflow. The committed `.env` remains for full Docker Compose startup.

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
