## Why

The repository now has community-edition foundations for WeCom and DingTalk authentication, callback transport, and limited routed side effects, but it still lacks a clear contract for a full external channel message loop. This change is needed to define how supported external channels progress from inbound user message to persisted conversation state and generated application response.

## What Changes

- Define community-edition requirements for receiving supported WeCom channel messages and linking them to application chat state.
- Define community-edition requirements for receiving supported DingTalk channel messages and linking them to application chat state.
- Define the bounded CE behavior for message deduplication, session reuse or creation, answer generation reuse, and outbound response delivery for supported external channel message types.
- Reuse the already-delivered authentication and callback transport contracts instead of reopening provider login, readiness, or callback configuration semantics.

## Capabilities

### New Capabilities
- `wecom-channel-message-loop`: Covers inbound WeCom message handling, session linkage, answer generation reuse, and supported outbound response behavior.
- `dingtalk-channel-message-loop`: Covers inbound DingTalk message handling, session linkage, answer generation reuse, and supported outbound response behavior.

### Modified Capabilities
- `wecom-chat-authentication`: Clarify the handoff boundary between authenticated WeCom integration setup and active message-loop behavior.
- `dingtalk-chat-authentication`: Clarify the handoff boundary between authenticated DingTalk integration setup and active message-loop behavior.

## Impact

- Affects the external-channel runtime code already introduced around `apps/chat/serializers/wecom_callback.py`, `apps/chat/serializers/dingtalk_callback.py`, related callback views, and the existing `ChatSerializers.chat()` answer path.
- Affects application chat persistence behavior in `apps/application/models/application_chat.py` and the surrounding post-response/update flow that currently backs the CE chat experience.
- Affects channel-facing response expectations in the WeCom and DingTalk callback contracts, and may add or tighten tests around callback idempotency, session continuity, and same-record answer updates.
