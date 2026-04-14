## Why

The advisory E2E job in CI is currently less reliable than the feature coverage it is meant to provide. In the latest merged auth-flow change, the advisory job failed before tests even started because the backend readiness wait step did not consistently prove server availability, and artifact upload also emitted avoidable noise when no Playwright report directory existed.

## What Changes

- Stabilize the advisory E2E backend startup and readiness flow in CI so the job can distinguish server boot failure from test failure.
- Tighten the CI contract around advisory E2E reporting so missing Playwright output is handled intentionally instead of surfacing as secondary noise.
- Align the Playwright/CI startup path, health check target, and report handling so advisory E2E failures are easier to diagnose and less flaky.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `ci-quality-gates`: refine the advisory E2E job requirements around backend readiness checks, failure surfacing, and artifact handling.
- `e2e-testing`: clarify the runtime assumptions for launching the admin app and collecting Playwright artifacts in CI.

## Impact

- `.github/workflows/ci.yml`
- `ui/playwright.config.ts`
- related E2E helper or startup scripts used by the advisory CI path
- CI diagnostics and artifact behavior for advisory Playwright runs
