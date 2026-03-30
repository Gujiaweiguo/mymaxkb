## Why

User group management endpoints in `system_manage/views/user_group.py` are guarded by admin-only permission decorators, but there is currently no denied-path integration coverage proving that a non-admin user receives 403 for those endpoints.

## What Changes

- Add denied-path integration tests for all admin-only user group management endpoints
- Reuse the existing integration-test style in `apps/system_manage/test_integration.py`
- Keep the slice test-only; no production code changes

## Capabilities

### Modified Capabilities

- `role-and-permission-management`: verify admin-only user group management endpoints reject non-admin callers

## Impact

- Extends `apps/system_manage/test_integration.py`
- Adds concrete permission enforcement evidence for `system/group/*` endpoints
