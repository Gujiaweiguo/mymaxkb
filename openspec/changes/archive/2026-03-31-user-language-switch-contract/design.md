## Context

`SwitchUserLanguageView` injects `request.user.id` into `SwitchLanguageSerializer`, which validates the locale against a fixed allowlist (`zh-CN`, `zh-Hant`, `en-US`) and persists the new value with a direct DB update. Existing integration tests only exercised unrelated profile/login endpoints, leaving the language-switch contract unverified.

## Goals / Non-Goals

**Goals:**
- Verify an authenticated actor can switch to a supported locale
- Verify an unsupported locale is rejected with the serializer’s allowlist error
- Verify the user row is updated only on the supported path

**Non-Goals:**
- No production changes to locale handling
- No expansion into profile response shape or workspace-specific language behavior
- No frontend locale tests

## Decisions

1. Add a dedicated `SwitchLanguageContractIntegrationTests` class in `apps/users/test_integration.py` so the users-domain endpoint contract remains isolated and deterministic.
2. Use real token authentication via `get_auth(user)` to exercise the same permission path as production.
3. Keep the success assertion aligned with the actual view behavior: `result.success(...)` wraps the serializer’s `None` return value as `data: null`.

## Risks / Trade-offs

- This slice intentionally verifies the current direct-update behavior and does not attempt to broaden locale support or refactor the serializer return shape.
