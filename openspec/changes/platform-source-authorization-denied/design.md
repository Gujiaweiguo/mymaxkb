## Context

`PlatformSourceView` and `ChatUserPlatformSourceView` are both guarded by `@has_permissions(..., RoleConstants.ADMIN)`, but current tests only prove admin happy paths. Denied-path coverage is the missing half of the permission contract and fits naturally beside the existing unit-style tests in `test_platform_source.py`.

## Goals / Non-Goals

**Goals:**
- Verify a regular USER receives 403 on system platform source GET/POST/PUT
- Verify a regular USER receives 403 on chat-user platform source GET/POST/PUT

**Non-Goals:**
- No production permission changes
- No additional validation-path or persistence-path assertions beyond the 403 contract

## Decisions

1. Extend `test_platform_source.py` so happy-path and denied-path stay co-located.
2. Reuse the existing `APIRequestFactory` style and add a non-admin user token mirroring patterns from `test_appearance_setting.py`.

## Risks / Trade-offs

- This slice is intentionally narrow and repetitive, but it closes an otherwise obvious auth gap on admin-only configuration endpoints.
