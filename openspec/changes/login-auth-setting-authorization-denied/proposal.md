## Why

Admin login-auth settings now have strong happy-path coverage, but there is still no explicit denied-path proof that non-admin users receive 403 on the admin GET/PUT endpoints.

## What Changes

- Add denied-path tests for admin login-auth setting GET and PUT
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `system-login-authentication`: verify non-admin actors cannot read or update admin login-auth settings

## Impact

- Extends `apps/system_manage/test_login_auth_setting.py`
- Completes the permission-boundary half of the admin login-auth setting surface
