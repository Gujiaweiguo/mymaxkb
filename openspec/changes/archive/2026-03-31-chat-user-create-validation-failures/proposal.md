## Why

Chat-user creation already had happy-path coverage, but the create validator still lacked explicit proof for its most important failure contracts: duplicate username, duplicate nick name, and weak password rejection.

## What Changes

- Add negative-path coverage for duplicate username on chat-user create
- Add negative-path coverage for duplicate nick name on chat-user create
- Add negative-path coverage for weak password rejection on chat-user create
- Sync the chat-user-management capability with those validation rules
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `chat-user-management`: verify chat-user creation rejects duplicate identity fields and weak passwords

## Impact

- Extends `apps/system_manage/test_chat_user_management.py`
- Strengthens create-time validation coverage in `ChatUserManageSerializer.Create.validate`
