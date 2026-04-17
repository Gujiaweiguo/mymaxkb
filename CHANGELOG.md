# Changelog

## [e2e-stability] - 2026-04-17

### Fixed
- Stabilized shared admin login flow in E2E tests (networkidle wait, form sync delay, clean re-navigation on retry)
- Auto-recover invalid RSA key state in `get_key_pair_by_sql()` to prevent login page crypto errors

### Added
- Login helper regression coverage (form readiness, token persistence)
- Application detail advisory coverage (overview, setting, access pages)
- Knowledge document management coverage (API-driven list, delete, rename)
- Knowledge document UI coverage (search/filter, table shell, status column header)
- Knowledge paragraph page navigation coverage (document row click → paragraph shell)

### Changed
- `gotoLogin()` now waits for `networkidle` to ensure full SPA hydration before form interaction
- `submitLoginAndWaitForToken()` retries with fresh page navigation on login click failure
- `globalSetup` enabled for all environments (was CI-only)

### Test Coverage
- Advisory E2E suite: 78 passed, 0 failed, 0 flaky, 1 skipped (@deferred chat)
- Login-related flakiness eliminated from 3 flaky → 0 flaky
- Backend regression test added for RSA key recovery
