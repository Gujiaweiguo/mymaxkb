## Context

`ChatUserSyncTypeView` returns `result.success(ChatUserSyncSerializer.get_sync_types())`, and `ChatUserSyncSerializer.get_sync_types()` currently returns `[]` in community edition. Existing tests only cover the POST sync endpoint's unsupported behavior, so the missing value is one precise GET assertion that the CE sync-types list is empty.

## Goals / Non-Goals

**Goals:**
- Verify the sync-types GET endpoint returns a success envelope in CE
- Verify the payload data is exactly an empty list in CE

**Non-Goals:**
- No changes to the view, serializer, or API schema
- No expansion into authorization-denied coverage for this endpoint
- No assertions about enterprise sync-type values

## Decisions

1. Extend `test_chat_user_management.py` so GET and POST CE sync behavior live in the same module.
2. Assert `payload['data'] == []` as the smallest stable CE-value contract.
3. Record the capability change as one chat-user-management scenario focused on the CE empty-list response.

## Risks / Trade-offs

- This slice intentionally checks only the stable CE contract, so it does not attempt to encode any enterprise-only sync-type behavior.
