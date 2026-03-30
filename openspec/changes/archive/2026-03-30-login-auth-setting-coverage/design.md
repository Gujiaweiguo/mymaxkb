## Context

`LoginAuthSettingView` is a narrow admin-only API that delegates all logic to `LoginAuthSettingSerializer`. The serializer contains untested normalization behavior for `max_attempts`, `failed_attempts`, `lock_time`, `default_value`, and `login_methods`. Existing tests in `test_integration_settings.py` only assert status code 200 and do not validate the response payload or persistence behavior.

## Goals / Non-Goals

**Goals:**
- Verify admin GET returns the full normalized default response when no setting exists
- Verify admin GET returns persisted values when a setting exists
- Verify admin PUT creates and updates login-auth settings with normalized output
- Verify serializer normalization behavior for attempt values and login methods

**Non-Goals:**
- No new public login-auth tests (already covered)
- No production serializer/view changes
- No exhaustive permission denied-path tests in this slice

## Decisions

1. Create a dedicated `test_login_auth_setting.py` module instead of extending `test_integration_settings.py`, because this slice combines API and serializer-focused assertions.
2. Use `APIClient` with `get_auth(admin_user)` for admin GET/PUT tests so the auth path matches recent integration work.
3. Keep serializer tests unit-level and direct, since the normalization functions are deterministic and do not need the request stack.

## Risks / Trade-offs

- This slice intentionally focuses on stable normalization and persistence behavior, not every invalid serializer branch.
