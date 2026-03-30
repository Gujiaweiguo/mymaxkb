## Context

`Valid` and `PublicLoginAuthSettingView` are both narrow GET-only endpoints. `Valid` requires `TokenAuth` but no additional permission decorator, and `PublicLoginAuthSettingView` is entirely unauthenticated. Their serializers return deterministic values driven by model counts and `SystemSetting`, so this slice can be implemented with small direct tests and no mocks.

## Goals / Non-Goals

**Goals:**
- Verify authenticated success for `valid/application/5`
- Verify unauthenticated access to `valid/*` is rejected
- Verify public login-auth endpoint returns default values when no setting exists
- Verify public login-auth endpoint reflects persisted configuration

**Non-Goals:**
- No write-path coverage for admin login-auth settings in this slice
- No invalid-payload or exception-path testing for `ValidSerializer`
- No production changes

## Decisions

1. Create a dedicated small test module instead of expanding `test_integration_settings.py`, because this slice mixes one authenticated utility endpoint with one public settings endpoint.
2. Use `APIClient` rather than `APIRequestFactory` so `TokenAuth` is exercised for the `valid/*` route.
3. Use the `application` count path for `Valid` because it avoids interference from the number of test users created in setup.

## Risks / Trade-offs

- The `Valid` success path depends on current model counts staying below the CE limit; choosing `application/5` keeps this stable in tests.
