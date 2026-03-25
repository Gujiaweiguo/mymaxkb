## 1. WeCom message-loop completion

- [x] 1.1 Confirm the supported WeCom payload set (`text`, `enter_agent`, and explicit unsupported classes) against the current callback implementation and update any missing runtime guards
- [x] 1.2 Ensure WeCom channel session reuse and `ChatRecord` persistence consistently attach inbound text to the correct chat session
- [x] 1.3 Preserve WeCom message identifiers and related channel metadata through answer generation so same-record updates remain traceable and idempotent
- [x] 1.4 Define and implement the bounded CE outbound WeCom response behavior for supported answered messages

## 2. DingTalk message-loop advancement

- [x] 2.1 Keep DingTalk transport and routed `user_add_org` behavior aligned with the current supported callback/event set
- [x] 2.2 Confirm whether a supported inbound DingTalk message payload exists for CE conversation input and document the decision in code/tests
- [x] 2.3 If a supported DingTalk message payload is confirmed, implement the first session/persistence/answer bridge step using the existing CE chat path
- [x] 2.4 If no supported DingTalk message payload is confirmed, keep DingTalk capability-gated and ensure unsupported payloads remain explicit no-op acknowledgements

## 3. Shared idempotency and delivery boundaries

- [x] 3.1 Separate event-level and message-level deduplication rules in the callback handlers and tests for each supported channel payload class
- [x] 3.2 Define the synchronous callback-versus-async delivery boundary for outbound responses and answer generation reuse in the CE message loop
- [x] 3.3 Add or tighten traceable source metadata on persisted channel conversations so retries, regenerated answers, and outbound responses can be correlated

## 4. Verification and closeout

- [x] 4.1 Add targeted Django tests covering supported WeCom loop behavior, duplicate delivery behavior, and outbound response handling
- [x] 4.2 Add targeted Django tests covering the bounded DingTalk message-loop behavior that is actually supported in CE
- [x] 4.3 Run the narrowest backend verification set plus `apps/manage.py check`, then review the change for any remaining auth/callback boundary mismatches before implementation continues
