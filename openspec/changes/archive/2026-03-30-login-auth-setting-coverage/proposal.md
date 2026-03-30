## Why

Login auth setting endpoints currently have only thin smoke coverage. There is no test that proves admin GET returns the full normalized payload, that admin PUT persists normalized values, or that the serializer normalization rules for attempts and login methods behave correctly.

## What Changes

- Add focused tests for admin login-auth setting GET/PUT behavior
- Add serializer-level normalization tests for attempt counts, login methods, and response shaping
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `system-login-authentication`: verify admin login auth settings are normalized, persisted, and readable through the admin API

## Impact

- New test module under `apps/system_manage/`
- Strengthens the admin-side coverage that complements the already-completed public login-auth coverage
