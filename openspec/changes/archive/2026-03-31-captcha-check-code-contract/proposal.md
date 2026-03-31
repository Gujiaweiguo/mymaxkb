## Why

The users-domain login contract already covered basic login and logout behavior, but there was still no endpoint-level proof for the cache-backed captcha flow or the verification-code checking endpoint.

## What Changes

- Add contract coverage for captcha generation under configured threshold conditions
- Add contract coverage for captcha-enforced login under the licensed login flow
- Add contract coverage for `check_code` success and failure behavior against cached verification codes
- Sync the system-login-authentication capability with these cache-backed verification contracts
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `system-login-authentication`: verify licensed captcha enforcement and verification-code cache validation behavior

## Impact

- Extends `apps/users/test_integration.py`
- Closes the users-domain contract gap for `GET /admin/api/user/captcha`, `POST /admin/api/user/login` captcha gating, and `POST /admin/api/user/check_code`
