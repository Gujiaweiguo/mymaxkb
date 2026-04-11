## Why

The repository already has meaningful backend tests, frontend type-check/lint commands, Vitest coverage, and Playwright scaffolding, but these signals are not enforced as a repeatable merge gate. This change is needed now to turn the existing validation surface into a reliable CI quality barrier and to close a small number of high-risk coverage gaps on core user flows.

## What Changes

- Add a CI validation pipeline that runs the repository's existing backend and frontend verification commands on every relevant change.
- Define the minimum required quality gates for backend Django tests, frontend type-check, frontend lint, and frontend unit/component tests.
- Establish a phased policy for E2E coverage so critical Playwright scenarios can be added or promoted without blocking the initial CI rollout.
- Add a small, targeted set of high-value test coverage improvements for core product paths that are currently under-verified.
- Document how local validation maps to CI so contributors can reproduce failures before opening or updating a pull request.

## Capabilities

### New Capabilities
- `ci-quality-gates`: Define the repository's required continuous-integration validation pipeline, mandatory checks, and contributor-facing expectations for merge readiness.

### Modified Capabilities
- `backend-unit-testing`: Require the supported backend test suite to run as part of CI instead of existing only as a local development convention.
- `e2e-testing`: Clarify which end-to-end scenarios are required immediately, which are phased in later, and how critical flows are promoted into CI enforcement.
- `frontend-typecheck-stability`: Extend frontend static validation expectations from local cleanup work to ongoing CI enforcement for touched changes.

## Impact

- GitHub Actions workflows under `.github/workflows/`
- Backend validation commands and test execution via `apps/manage.py test`
- Frontend validation commands in `ui/package.json`, including `npm run type-check`, `npm run lint`, and `npm run test`
- Playwright execution policy in `ui/e2e/` and `ui/playwright.config.ts`
- Developer documentation describing local-first validation and CI expectations
