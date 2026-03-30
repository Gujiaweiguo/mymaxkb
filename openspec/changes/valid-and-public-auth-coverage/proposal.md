## Why

Two small but real API surfaces in `system_manage` still have zero automated coverage: the authenticated `valid/{type}/{count}` endpoint and the public `login/auth/setting` endpoint. Both are stable, read-only endpoints with deterministic response shapes, making them ideal for another narrow zero-production-change slice.

## What Changes

- Add tests for `Valid.get` success and authentication requirement
- Add tests for `PublicLoginAuthSettingView.get` default response and persisted-setting response
- Keep scope limited to tests and OpenSpec artifacts; no production code changes

## Capabilities

### Modified Capabilities

- `system-user-management`: verify CE user-count/application-count validation endpoint behavior
- `role-and-permission-management`: verify public login-auth settings are exposed consistently

## Impact

- New lightweight test module under `apps/system_manage/`
- Closes two previously untested API endpoints
