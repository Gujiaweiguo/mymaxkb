## Why

The platform-source settings views already have partial unit coverage, but three narrow admin happy-path gaps remain: listing system platform sources, listing chat-user platform sources, and saving chat-user platform source configuration. These are read/write endpoints adjacent to already-tested validate/save flows and are good candidates for another small zero-production-change slice.

## What Changes

- Add happy-path coverage for `GET /platform/source`
- Add happy-path coverage for `GET /chat_user/auth/platform/source`
- Add happy-path coverage for `POST /chat_user/auth/platform/source`
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `system-login-authentication`: verify platform source configuration can be listed for admin login integrations
- `chat-user-management`: verify chat-user platform source configuration can be listed and saved

## Impact

- Extends `apps/system_manage/test_platform_source.py`
- Closes the remaining happy-path coverage holes in `views/platform_source.py`
