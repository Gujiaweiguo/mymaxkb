## Context

`apps/users/views/user.py` applies `@has_permissions(..., RoleConstants.ADMIN)` to the mutation endpoints on `UserManage`: create, update, delete, batch delete, and password reset. Existing integration tests covered the admin happy path but did not verify that a regular authenticated user receives HTTP 403 for those same mutations.

## Goals / Non-Goals

**Goals:**
- Verify a `USER` role receives 403 on create, update, delete, batch-delete, and password-reset mutations under `user_manage`
- Sync the main system-user-management spec with that denied mutation contract

**Non-Goals:**
- No production permission changes
- No assertions about `user_manage` read/detail/page behavior, which is intentionally out of scope for this slice
- No expansion into login/profile/language/logout endpoints

## Decisions

1. Add one denied test class in `apps/users/test_integration.py` using `get_auth(self.regular_user)` so the real permission decorator path is exercised.
2. Cover the five actually forbidden mutation endpoints in a single subtest-driven test method.
3. Phrase the spec as “cannot mutate” rather than “cannot access” so it matches the live behavior proven by the test.

## Risks / Trade-offs

- This slice intentionally leaves read/page semantics alone because the current implementation allows them for non-admin authenticated users.
