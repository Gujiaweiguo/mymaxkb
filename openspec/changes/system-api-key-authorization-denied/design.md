## Context

`SystemApiKeyView`, `SystemApiKeyView.Page`, and `SystemApiKeyView.Operate` are all guarded by `@has_permissions(PermissionConstants.SYSTEM_API_KEY_EDIT, RoleConstants.ADMIN)`. Existing tests already cover create/page/edit/delete behavior for admin actors, so the missing value is denied-path coverage for regular users.

## Goals / Non-Goals

**Goals:**
- Verify a regular USER receives 403 on create, page, edit, and delete system API key operations

**Non-Goals:**
- No new happy-path CRUD assertions
- No production changes

## Decisions

1. Extend `test_system_api_key.py` so happy-path and denied-path coverage stay in one place.
2. Reuse the existing `APIRequestFactory` + `force_authenticate` style already used in that file.

## Risks / Trade-offs

- This slice is intentionally small, but it closes the missing half of the permission contract on a sensitive admin-only surface.
