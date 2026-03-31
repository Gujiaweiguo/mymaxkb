## Why

The users-domain integration tests already covered login, logout, captcha, check-code, and language switching, but there was still no endpoint-level proof for the authenticated current-user password reset contract.

## What Changes

- Add contract coverage for successful current-user password reset
- Add contract coverage for mismatched confirmation and weak-password rejection on the current-user reset endpoint
- Sync the system-login-authentication capability with the current-user password reset behavior
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `system-login-authentication`: verify authenticated actors can reset their current password with supported input and receive validation errors for invalid input

## Impact

- Extends `apps/users/test_integration.py`
- Closes the users-domain contract gap for `POST /admin/api/user/current/reset_password`
