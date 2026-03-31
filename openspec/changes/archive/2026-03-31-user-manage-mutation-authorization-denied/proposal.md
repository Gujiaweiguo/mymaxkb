## Why

Administrative user-management CRUD coverage existed for admins, but there was still no explicit proof that a regular authenticated user is forbidden from mutating the user-management surface.

## What Changes

- Add denied-path coverage for non-admin create, update, delete, batch-delete, and password-reset operations on `user_manage`
- Sync the system-user-management capability with the non-admin mutation-denied scenario
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `system-user-management`: verify non-admin actors cannot mutate the administrative user-management surface

## Impact

- Extends `apps/users/test_integration.py`
- Documents the actual permission boundary already enforced by the user-management mutation endpoints
