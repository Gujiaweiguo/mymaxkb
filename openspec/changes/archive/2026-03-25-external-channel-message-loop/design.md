## Context

The repository already contains community-edition foundations for external channel integration, but the two supported channels are at different runtime depths. WeCom now has a working inbound message loop in `apps/chat/serializers/wecom_callback.py`: callback verification, session creation or reuse, `ChatRecord` persistence, answer generation reuse through `ChatSerializers.chat()`, and message-level idempotency using `source.msg_id`. DingTalk currently reaches only transport and routed org-event behavior in `apps/chat/serializers/dingtalk_callback.py`: callback verification, encrypted response handling, `user_add_org` chat-shell creation, and event-level deduplication using `source.event_id`.

The new change exists to define how these channel-specific implementations should become a coherent external-channel message loop without reopening the already-archived authentication, callback transport, or readiness semantics from the earlier integration changes.

## Goals / Non-Goals

**Goals:**
- Define the CE message-loop contract for WeCom from inbound callback to persisted conversation state and generated answer.
- Define the CE message-loop contract for DingTalk based on confirmed runtime capabilities, while being explicit about where parity is incomplete.
- Reuse the existing `Chat`, `ChatRecord`, `ChatSerializers.chat()`, and callback code paths instead of inventing a parallel channel conversation system.
- Formalize idempotency, session reuse, and answer-persistence expectations for supported external channel message types.

**Non-Goals:**
- Reopening WeCom or DingTalk login/authentication requirements already covered by `wecom-chat-authentication` and `dingtalk-chat-authentication`.
- Redesigning channel readiness, callback credential storage, or admin setup flows already shipped in earlier changes.
- Defining unsupported message types, rich-media handling, or full outbound bot capability where current repo evidence is absent.
- Inventing a DingTalk text-message loop before a confirmed inbound message payload and request shape are established.

## Decisions

### 1. Treat WeCom as the reference loop and DingTalk as capability-gated parity

**Decision:** Use the existing WeCom implementation as the architectural reference for the message loop, but do not claim equivalent DingTalk runtime behavior until its inbound message payload is concretely supported.

**Why:** The codebase already proves WeCom can execute the full CE loop: callback verification, `Chat` reuse, `ChatRecord` creation, answer generation reuse, and `msg_id` deduplication. DingTalk, by contrast, only proves transport and routed `user_add_org` handling. Designing both channels as though they already have equivalent message payloads would overstate the real implementation.

**Alternatives considered:**
- **Force strict WeCom/DingTalk parity in the design now** — rejected because current DingTalk code and evidence do not justify it.
- **Split WeCom and DingTalk into unrelated changes** — rejected because the product intent is one external-channel message loop, and the shared boundaries are still valuable.

### 2. Reuse the existing chat persistence and answer-generation pipeline

**Decision:** The message loop should continue to reuse `Chat`, `ChatRecord`, and `ChatSerializers.chat()` rather than creating channel-specific message persistence or answer-generation code paths.

**Why:** The repository already demonstrates that the existing CE chat path can be driven from non-UI channel callbacks. This keeps behavior consistent with the current application conversation model and minimizes duplicate logic across channels.

**Alternatives considered:**
- **Create channel-specific response-generation services** — rejected because the repo already has a working generic answer path.
- **Persist only shell events and defer answer generation to later** — rejected for WeCom because the repo already proves deeper reuse is viable.

### 3. Separate transport idempotency from message idempotency

**Decision:** Channel callback handling should distinguish between event-level deduplication and message-level deduplication.

**Why:** DingTalk currently dedupes routed org events by `eventId`, while WeCom dedupes text messages by `msg_id` on `ChatRecord.source`. These are different layers of idempotency and need to stay explicit in the design so retries do not create duplicate chats or duplicate answers.

**Alternatives considered:**
- **One universal dedupe key for all channels and payload types** — rejected because repo evidence already shows different identifiers at different layers.

### 4. Keep outbound response delivery as an explicit design boundary

**Decision:** The design should treat outbound channel response delivery as part of the message-loop capability boundary, but acknowledge that current repo behavior is still incomplete there.

**Why:** The proposal explicitly includes outbound response behavior, but the current implementation primarily proves inbound persistence and answer generation. Naming outbound delivery as a design boundary prevents the change from silently collapsing into an inbound-only loop.

**Alternatives considered:**
- **Exclude outbound delivery entirely from this change** — rejected because it would understate the intended “message loop” behavior.
- **Specify a full outbound bot implementation now** — rejected because the repo evidence is not yet deep enough for that level of detail.

### 5. Use supported payload sets as the unit of scope control

**Decision:** The change should specify supported inbound payload classes per channel instead of treating “all channel messages” as a single scope bucket.

**Why:** WeCom already has a supported set (`text`, `event/enter_agent`) with distinct behavior. DingTalk currently has a narrower supported set (`check_url`, `user_add_org`). Scoping by payload class allows the specs and tasks to grow honestly from actual repo behavior.

**Alternatives considered:**
- **Define generic “message support” without payload-level boundaries** — rejected because it would hide important asymmetry and implementation risk.

## Risks / Trade-offs

- **[Risk] DingTalk message parity may still be blocked by missing confirmed inbound message payloads** → **Mitigation:** keep DingTalk specs capability-gated and avoid promising text-message answer bridging until payload evidence exists.
- **[Risk] Channel retries can still create duplicate work if idempotency keys are not aligned with actual payload semantics** → **Mitigation:** explicitly separate event-level and message-level dedupe in the design and preserve source identifiers through persistence and answer generation.
- **[Risk] Reusing the synchronous answer path may not fit callback timeout windows for all external channels** → **Mitigation:** make synchronous reuse an explicit current-state decision and leave async delivery as a bounded follow-up decision rather than an implicit assumption.
- **[Risk] Outbound delivery behavior may diverge from inbound persistence progress, leaving channels asymmetrically complete** → **Mitigation:** treat outbound response handling as a first-class design boundary and tie tasks to the exact supported payload set for each channel.
