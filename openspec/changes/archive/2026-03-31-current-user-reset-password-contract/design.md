## Context

`ResetCurrentUserPasswordView` accepts authenticated requests, validates the new password through `ResetCurrentUserPassword`, updates the stored password, clears `require_password_change`, deletes the current token cache entry, and returns `result.success(True)`. Existing coverage stopped at login/logout and public password-reset helpers, leaving this authenticated self-service endpoint unverified.

## Goals / Non-Goals

**Goals:**
- Verify a current user can reset their password successfully
- Verify mismatched confirmation is rejected with the app-level password mismatch error
- Verify unsupported password format is rejected with the serializer validation error
- Verify the current token cache entry is invalidated after success

**Non-Goals:**
- No production changes to password-reset logic
- No expansion into email-code reset flows or send-email endpoints
- No frontend password-reset tests

## Decisions

1. Add a dedicated `ResetCurrentPasswordContractIntegrationTests` class to the existing users integration file so the users-domain credential contract stays together.
2. Use a real auth token from `get_auth(user)` and seed the token cache entry explicitly so the invalidation side effect is observable.
3. Assert the actual endpoint contract, including the localized message variants currently emitted by the serializer and DRF validation wrapper.

## Risks / Trade-offs

- The weak-password assertion is intentionally tied to the current localized field-prefix message (`密码:`) because that is the real endpoint contract today.
