## Context

`SystemProfile.get` is a public GET-only endpoint that returns `SystemProfileSerializer.profile()`. The serializer output is deterministic in shape: `version`, `edition`, `license_is_valid`, and `ras`. No auth is required, and there are no model writes or side effects.

## Goals / Non-Goals

**Goals:**
- Verify unauthenticated callers can read `/profile`
- Verify the response payload contains the stable keys and values returned by the serializer

**Non-Goals:**
- No API-key variant coverage in this slice (`/system/profile` is already covered elsewhere)
- No production changes

## Decisions

1. Create a dedicated `test_system_profile.py` module because this slice is tiny and independent.
2. Compare the API response to `SystemProfileSerializer.profile()` directly so the test stays aligned with the serializer contract without over-hardcoding volatile values.

## Risks / Trade-offs

- `ras` comes from runtime key material, so exact value assertions should be equality against the serializer output rather than string literals.
