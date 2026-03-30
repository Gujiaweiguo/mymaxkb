## Context

`apps/system_manage/views/platform_source.py` exposes two closely related admin-only views backed by the same serializer layer. Existing tests already cover system-level POST/PUT and chat-user-level PUT, but they skip the corresponding GET list endpoints and the chat-user-level POST save endpoint.

## Goals / Non-Goals

**Goals:**
- Verify `PlatformSourceView.get` returns the three normalized platform entries
- Verify `ChatUserPlatformSourceView.get` returns the three normalized chat-user platform entries
- Verify `ChatUserPlatformSourceView.post` persists a chat-user platform source setting

**Non-Goals:**
- No denied-path tests in this slice
- No production changes to platform source serializers or views
- No duplication of already-covered validate/toggle behavior on the system-level endpoint

## Decisions

1. Extend `test_platform_source.py` rather than creating a new file so all platform-source coverage stays together.
2. Keep using `APIRequestFactory` and `force_authenticate` with the existing admin token shape, matching the established local test style in that file.
3. Target both `system-login-authentication` and `chat-user-management` specs because the two views split across those domains.

## Risks / Trade-offs

- This change spans two capabilities, but only because the code already splits platform-source behavior into system-login and chat-user auth settings.
