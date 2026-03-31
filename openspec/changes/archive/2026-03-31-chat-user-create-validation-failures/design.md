## Context

`ChatUserManageSerializer.Create.validate` already enforces three critical constraints before persisting a chat user: username uniqueness, nick name uniqueness, and password complexity. Existing tests only proved the happy path, leaving those validation branches unverified.

## Goals / Non-Goals

**Goals:**
- Verify create rejects a username that already exists
- Verify create rejects a nick name that already exists
- Verify create rejects a password that fails the supported complexity rule

**Non-Goals:**
- No changes to the serializer or view implementation
- No expansion into update, delete, or password-reset validation paths
- No changes to chat-user group validation behavior

## Decisions

1. Extend the existing `ChatUserManagementTests` class so the new failure-path tests live beside the existing create happy-path test.
2. Exercise the serializer through `ChatUserManageView.as_view()` to keep the response contract grounded at the endpoint layer.
3. Keep assertions narrow to the stable business-code failure contract (`code == 500`) already used in nearby negative-path tests.

## Risks / Trade-offs

- This slice intentionally avoids asserting localized error strings to keep the tests stable across translation changes while still pinning the failure contract.
