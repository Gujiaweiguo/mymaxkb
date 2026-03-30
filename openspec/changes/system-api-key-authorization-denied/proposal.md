## Why

System API key endpoints already have strong happy-path coverage, but they still lack explicit denied-path proof that non-admin users receive 403 across create, page, edit, and delete operations.

## What Changes

- Add denied-path tests for all admin-only system API key endpoints
- Keep scope limited to authorization enforcement; no production code changes

## Capabilities

### Modified Capabilities

- `system-user-management`: verify non-admin actors cannot manage system API keys

## Impact

- Extends `apps/system_manage/test_system_api_key.py`
- Completes permission-boundary coverage for `views/system_api_key.py`
