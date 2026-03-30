## Why

The platform-source admin endpoints now have happy-path coverage, but there is still no denied-path proof that non-admin users are rejected from system login platform configuration and chat-user platform configuration.

## What Changes

- Add denied-path tests for `PlatformSourceView` GET/POST/PUT
- Add denied-path tests for `ChatUserPlatformSourceView` GET/POST/PUT
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `system-login-authentication`: verify non-admin actors cannot manage platform login sources
- `chat-user-management`: verify non-admin actors cannot manage chat-user platform sources

## Impact

- Extends `apps/system_manage/test_platform_source.py`
- Completes permission enforcement coverage for `views/platform_source.py`
