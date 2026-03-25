## 1. Scope and prerequisite reuse

- [x] 1.1 Confirm which readiness and provider-validation behaviors are reused from `external-integrations` and should not be redefined here
- [x] 1.2 Map the concrete backend gaps for WeCom and DingTalk runtime behavior, including provider clients, auth-code exchange, and callback handlers
- [x] 1.3 Map the concrete frontend gaps for admin login, chat-user login, and application callback flows that currently reference WeCom or DingTalk

## 2. WeCom capability planning

- [x] 2.1 Define WeCom administrator login behavior using the existing QR login and provider-readiness surfaces
- [x] 2.2 Define WeCom chat-user login behavior using the dedicated chat-user provider setting path
- [x] 2.3 Define WeCom application callback behavior and the minimum active-use contract implied by existing callback metadata
- [x] 2.4 Add the first WeCom application callback side effect by persisting an application chat on `enter_agent`
- [x] 2.5 Add the first WeCom text callback side effect by persisting a chat record onto a WeCom chat session
- [x] 2.6 Link the first WeCom text callback into the existing answer-generation path and persist the generated answer on the same chat record
- [x] 2.7 Preserve `msg_id` through WeCom text answer generation and dedupe duplicate callback deliveries
- [x] 2.8 Validate the real non-stream WeCom text callback path updates the original chat record and preserves `msg_id`

## 3. DingTalk capability planning

- [x] 3.1 Define DingTalk administrator login behavior using the existing QR login and provider-readiness surfaces
- [x] 3.2 Define DingTalk chat-user login behavior using the dedicated chat-user provider setting path
- [x] 3.3 Define DingTalk application callback behavior and the minimum active-use contract implied by existing callback metadata
- [x] 3.4 Add the first DingTalk callback side effect by routing `user_add_org` into a persisted chat shell
- [x] 3.5 Make DingTalk `user_add_org` retry-safe by deduping `eventId` and handling all `userId` entries

## 4. Shared design decisions

- [x] 4.1 Define shared backend execution boundaries for provider-specific clients, code exchange, and callback handling without collapsing WeCom and DingTalk into one schema
- [x] 4.2 Define how login-store flows, chat-user flows, and application callback flows attach to the new backend contracts
- [x] 4.3 Record explicit non-goals so this change does not reopen Lark knowledge import, audit governance, or already-delivered readiness work

## 5. Verification and execution slicing

- [x] 5.1 Break backend implementation into provider runtime, login callback, and application callback slices with targeted Django verification per slice
- [x] 5.2 Break frontend implementation into admin login, chat-user login, and application-access wiring slices with `npm run type-check` and `npm run lint` as default signals
- [x] 5.3 Record any known repo-state constraints, including draft or unreliable existing integration tests that should not be treated as acceptance evidence

## 6. Closeout readiness

- [x] 6.1 Review the proposal, design, specs, and task breakdown for overlap with active changes and tighten scope if needed before implementation starts
