# AGENTS.md
This file is for coding agents working in `/opt/code/MaxKB`.
Use verified repo facts over generic assumptions. When evidence is thin, make narrow claims and add caveats.

## Project layout
- Backend: Python 3.11 + Django (`pyproject.toml`, `apps/manage.py`, `main.py`)
- Frontend: Vue 3 + Vite + TypeScript (`ui/package.json`)
- Data layer: PostgreSQL + pgvector
- Cache / queue: Redis

## Checked rule files
- `.cursorrules` — not found
- `.cursor/rules/` — not found
- `.github/copilot-instructions.md` — not found
No repo-local Cursor or Copilot rules were found.

## Setup
Backend (`pyproject.toml`): Python `~=3.11.0`, package manager `uv`.
Verified install pattern from Dockerfiles:
```bash
pip install uv
python -m uv pip install -r pyproject.toml
```
Frontend lives in `ui/` and is set up with:
```bash
cd ui
npm install
```

## Verified backend commands
Supported by `main.py`:
```bash
python main.py dev web
python main.py dev celery
python main.py dev local_model
python main.py start all
python main.py start web
python main.py start task
python main.py upgrade_db
python main.py collect_static
```
Behavior from `main.py`:
- `dev ...` runs `collectstatic`, then `migrate`, then starts the selected dev service
- `start ...` also runs `collectstatic` and `migrate` before starting services
- `upgrade_db` runs migrations only
- `collect_static` collects frontend assets into Django static output
`apps/manage.py` is the standard Django entrypoint and can be used for direct Django commands.

Agent rule: prefer `apps/manage.py` for precise Django operations; use `main.py` only when you intentionally want its startup behavior, including automatic `collectstatic + migrate`.

## Verified frontend commands
Run these from `ui/`:
```bash
npm run dev
npm run chat
npm run build
npm run build-chat
npm run type-check
npm run lint
npm run format
```
From `ui/package.json`:
- `dev`: main Vite dev server
- `chat`: Vite dev server in chat mode
- `build`: type-check + main build
- `build-chat`: type-check + chat build
- `type-check`: `vue-tsc --build`
- `lint`: `eslint . --fix`
- `format`: `prettier --write src/`

## Tests
Backend test modules exist at:
`apps/application/tests.py`, `apps/chat/tests.py`, `apps/knowledge/tests.py`, `apps/local_model/tests.py`, `apps/models_provider/tests.py`, `apps/oss/tests.py`, `apps/system_manage/tests.py`, `apps/tools/tests.py`, `apps/trigger/tests.py`, `apps/users/tests.py`.

These files are currently placeholder `django.test.TestCase` stubs, so coverage is sparse.
Likely Django test commands via `apps/manage.py`:
```bash
python apps/manage.py test
python apps/manage.py test users.tests
python apps/manage.py test knowledge.tests
python apps/manage.py test users.tests.SomeTestCase
python apps/manage.py test users.tests.SomeTestCase.test_method
```
Treat single-test forms as Django-standard and verify exact labels locally before relying on them in automation.

No frontend test runner was found in `ui/package.json`.
No `vitest`, `jest`, or Playwright command is configured.
Do not invent frontend unit-test commands.

## Lint / format / type-check
Verified frontend quality commands:
```bash
cd ui && npm run type-check
cd ui && npm run lint
cd ui && npm run format
```
Backend tooling is much looser:
- `pylint` is present as a dependency in `pyproject.toml`
- no repo-level `pylintrc`, `ruff.toml`, `mypy.ini`, `pyright`, `black`, or `isort` config was found
Do not claim a standardized Python lint, format, or type-check command unless you add and verify it.

## CI signal
`.github/workflows/typos_check.yml` runs `crate-ci/typos` and excludes migrations plus a few generated files.
Use that as a spelling reminder only; do not infer broader CI coverage from it.

## Backend style guidance
Observed in `apps/common/handle/handle_exception.py`, `apps/knowledge/views/document.py`, and related files:
- Imports are grouped with blank lines between stdlib, third-party, and local imports
- Functions and local variables use `snake_case`; classes use `PascalCase`
- DRF views commonly subclass `APIView`
- API endpoints usually return `result.success(...)`, `result.error(...)`, or `result.Result(...)` instead of raw `Response`
- User-facing text commonly uses `gettext_lazy as _`
- Permission and audit decorators are common; preserve them when editing endpoints
- Avoid unrelated reformatting of long import lists and continuations

### Backend typing and errors
- Typing style is mixed: both `List` / `Dict` and newer unions are present
- Follow the style already used in the file you edit
- Do not mass-modernize typing syntax in unrelated code
- Add type hints only when they clarify behavior and keep the diff narrow
- Broad exception handling exists in service code; preserve the repo-specific error/result shape
- Errors are usually logged with `logging` or `maxkb_logger`
- Do not add empty `except` blocks

## Frontend style guidance
From `ui/.prettierrc.json`:
- no semicolons
- single quotes
- `printWidth: 100`
From `ui/eslint.config.ts`:
- lint target: `**/*.{ts,mts,tsx,vue}`
- ignores: `dist`, `dist-ssr`, `coverage`
- `vue/multi-word-component-names`: off
- `@typescript-eslint/no-explicit-any`: off
- `@typescript-eslint/no-unused-vars`: off
Observed in `ui/src/main.ts` and `ui/src/router/index.ts`:
- `@/` path alias is standard
- type-only imports are used and should be preserved
- import order is practical rather than rigidly enforced
- naming is mixed; file-local consistency matters more than normalization
Frontend editing guidance:
- keep semicolon-free formatting and prefer single quotes
- do not globally remove `any`; the repo explicitly allows it
- do not mass-clean import order or naming in untouched files

## Validation expectations
Because automated tests are sparse, validate changes with the nearest real signal:
- backend change: run the narrowest relevant Django test if one exists, otherwise run the relevant startup or management command
- frontend change: run `npm run type-check` and `npm run lint`
- startup-sensitive change: validate the startup path you touched
Default verification rule: frontend edits should normally run `npm run type-check && npm run lint`; backend edits should normally run the narrowest related Django test, or the closest relevant management/startup command when no meaningful test exists.
Do not overstate confidence from placeholder tests.

## Practical do / do-not
Do:
- use Python 3.11 for backend work
- use `uv`-based dependency installation
- use `ui/package.json` scripts for frontend tasks
- preserve Django permission/log/result-wrapper patterns
- keep changes narrowly scoped
Do not:
- invent pytest, vitest, or Playwright commands, or assume default toolchains like ruff, black, or mypy exist unless this repo explicitly adds and verifies them
- invent repo-level Python formatting or typing tools
- rewrite unrelated typing style across older backend files
- replace repo-specific API response helpers with ad hoc response shapes

## Default admin credentials in docs
`README.md` and `README_CN.md` document fresh-install bootstrap credentials:
- username: `admin`
- password: configured through `MAXKB_DEFAULT_PASSWORD`
Treat this as a bootstrap-only credential and rotate it on first login.
