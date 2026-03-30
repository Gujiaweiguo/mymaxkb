## Context

`LoginAuthSettingView` is guarded by `@has_permissions(PermissionConstants.LOGIN_AUTH_READ, RoleConstants.ADMIN)` for GET and `@has_permissions(PermissionConstants.LOGIN_AUTH_EDIT, RoleConstants.ADMIN)` for PUT. Existing tests already cover serializer logic and admin happy paths, so the missing value is denied-path coverage for regular users.

## Goals / Non-Goals

**Goals:**
- Verify a regular USER receives 403 on admin login-auth GET
- Verify a regular USER receives 403 on admin login-auth PUT

**Non-Goals:**
- No public endpoint assertions (already covered elsewhere)
- No production changes

## Decisions

1. Extend `test_login_auth_setting.py` so happy-path and denied-path coverage stay in one place.
2. Reuse `APIClient` with `get_auth(user)` to match the working admin-side integration style.

## Risks / Trade-offs

- This slice is intentionally tiny, but it closes the missing permission-boundary contract on an admin-only settings endpoint.
