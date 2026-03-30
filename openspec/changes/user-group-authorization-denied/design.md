## Context

The `system/group` endpoints already support admin happy-path operations in `test_chat_user_management.py`, but denied-path coverage is missing. Existing integration suites already verify the same pattern for workspace management, chat-user management, shared-resource authorization, and resource permission endpoints.

## Goals / Non-Goals

**Goals:**
- Add 403-denied integration tests for non-admin access to user group list, create, delete, add-member, remove-member, and member-page endpoints
- Match the existing denied-test style in `apps/system_manage/test_integration.py`

**Non-Goals:**
- No user group happy-path expansion
- No production permission changes
- No user-group validation edge-case testing in this slice

## Decisions

1. Extend `apps/system_manage/test_integration.py` instead of creating a new file so all admin-denied integration coverage stays together.
2. Use a normal `USER` actor authenticated with `get_auth()` to mirror the existing denied-path suites.
3. Create a real `UserGroup` and `ChatUser` relation fixture so delete/remove/page paths hit realistic objects rather than fake IDs.

## Risks / Trade-offs

- This slice proves denial only, not happy-path semantics, but that is the highest-value adjacent gap because those happy paths are already covered elsewhere.
