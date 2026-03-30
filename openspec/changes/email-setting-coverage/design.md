## Context

`SystemSetting.Email` in `views/email_setting.py` is a narrow admin-only API with three methods: GET, PUT, and POST. Persistence is handled through `EmailSettingSerializer.Create.update_or_save()`, and SMTP validation is delegated to `EmailBackend.open()` inside `EmailSettingSerializer.Create.is_valid()`.

## Goals / Non-Goals

**Goals:**
- Verify GET returns `{}` when no email setting exists
- Verify PUT creates and then updates persisted email settings
- Verify POST succeeds when SMTP validation succeeds
- Verify non-admin actors receive 403 for email-setting management endpoints

**Non-Goals:**
- No real SMTP/network calls in tests
- No production serializer or view changes
- No exhaustive serializer invalid-input matrix in this slice

## Decisions

1. Create a dedicated `test_email_setting.py` module instead of extending `test_integration_settings.py`, because this slice needs mocking and more specific persistence assertions than the existing smoke tests.
2. Use `APIClient` with `get_auth(admin_user)` / `get_auth(user)` so the auth path matches recent integration work.
3. Mock `EmailBackend.open()` for PUT/POST happy-path tests to avoid external side effects while still exercising the API layer.

## Risks / Trade-offs

- This slice does not assert the exact error body for SMTP failure; it focuses on the stable happy-path and denied-path behavior.
