## Why

The users-domain integration tests already covered login, logout, captcha, and code validation, but there was still no endpoint-level proof for the authenticated language-switch contract.

## What Changes

- Add contract coverage for switching to a supported language through `POST /admin/api/user/language`
- Add contract coverage for rejecting unsupported locales through the same endpoint
- Sync the system-login-authentication capability with the supported-language constraint
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `system-login-authentication`: verify authenticated language switching persists supported locales and rejects unsupported ones

## Impact

- Extends `apps/users/test_integration.py`
- Closes the users-domain contract gap for the language-switch endpoint
