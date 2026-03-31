## Context

`CaptchaView` and `LoginSerializer` implement a cache-backed captcha flow where captcha image generation depends on the configured threshold, while login-time captcha enforcement additionally depends on the licensed login path. `CheckCode` validates email verification codes directly from the system cache. Existing coverage proved those rules only at the serializer unit level, not at the endpoint contract level.

## Goals / Non-Goals

**Goals:**
- Verify captcha generation returns a base64 payload only when the threshold requires it
- Verify licensed login rejects missing captcha and accepts a correct captcha after the threshold is reached
- Verify `check_code` accepts the matching cached code and rejects wrong or missing codes

**Non-Goals:**
- No send-email or password-reset flow tests in this slice
- No production changes to captcha, login, or code-validation logic
- No chat captcha coverage

## Decisions

1. Add one integration test class in `apps/users/test_integration.py` so the users-domain cache-backed contract stays together.
2. Patch `DatabaseModelManage.get_model` only where needed to model the licensed login path, matching the existing unit-test approach.
3. Phrase the spec carefully around the licensed login flow so the scenarios match the actual `license_is_valid` gate in `LoginSerializer.login()`.

## Risks / Trade-offs

- This slice intentionally verifies the current implementation, which only enforces login captcha in the licensed path, instead of broadening behavior in code.
