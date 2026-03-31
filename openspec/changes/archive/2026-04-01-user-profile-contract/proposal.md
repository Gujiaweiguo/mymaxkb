## Why

The users-domain integration suite already covered login, logout, captcha, language switching, and password reset, but the authenticated current-profile endpoint still only had a smoke test and no response-contract verification.

## What Changes

- Add endpoint-level contract coverage for the current-profile endpoint
- Verify core identity fields, role information, permissions, workspace membership, and the password-change flag behavior
- Sync the system-login-authentication capability with the current-profile contract
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `system-login-authentication`: verify authenticated actors can read their current profile contract and that local password-change state is surfaced when required

## Impact

- Extends `apps/users/test_integration.py`
- Closes the users-domain contract gap for `GET /admin/api/user/profile`
