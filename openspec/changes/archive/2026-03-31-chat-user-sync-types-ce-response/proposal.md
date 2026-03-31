## Why

Community-edition chat-user sync behavior already has a POST failure test, but there is still no explicit proof that the sync-types GET endpoint returns the CE contract of an empty list.

## What Changes

- Add exact-value coverage for the chat-user sync-types GET endpoint in CE
- Sync the chat-user-management capability with the CE empty-list scenario
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `chat-user-management`: verify community edition exposes no available chat-user sync types

## Impact

- Extends `apps/system_manage/test_chat_user_management.py`
- Closes the CE response-contract gap for `GET /admin/api/system/chat_user/sync_types`
