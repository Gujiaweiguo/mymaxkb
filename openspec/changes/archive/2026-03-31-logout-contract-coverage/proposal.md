## Why

The login contract already had endpoint-level coverage, but the paired logout endpoint still had no proof that it invalidates the current bearer token and rejects unauthenticated access.

## What Changes

- Add endpoint-level coverage for successful logout with token invalidation
- Add unauthenticated logout coverage
- Sync the system-user-management capability with the logout contract
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `system-user-management`: verify logout succeeds for authenticated actors and invalidates the current token

## Impact

- Extends `apps/users/test_integration.py`
- Closes the users-domain contract gap for `POST /admin/api/user/logout`
