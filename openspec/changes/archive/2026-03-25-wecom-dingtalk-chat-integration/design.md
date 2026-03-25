## Context

The archived `external-integrations` change already established provider readiness for WeCom, DingTalk, and Lark, and the synced `third-party-channel-integration` spec now covers configurable third-party channels. The repository also already contains WeCom and DingTalk QR login components, login store actions, application access configuration drawers, and backend callback URL generation, but there is no verified contract yet for the runtime auth and callback flows that those surfaces imply.

## Goals

- Define the first bounded CE contract for WeCom login and application callback behavior.
- Define the first bounded CE contract for DingTalk login and application callback behavior.
- Reuse existing readiness and saved-configuration behavior without redefining provider lifecycle semantics.
- Keep the planning narrow enough that implementation can proceed in provider-specific slices.

## Non-Goals

- Reworking the previously delivered readiness model or provider validation APIs.
- Extending Lark or Feishu knowledge behavior.
- Expanding into audit logging, broader system API governance, or ownership model changes.
- Defining second-wave channels such as Slack or WeChat public account.

## Existing Evidence

- System and chat-user provider configuration already exist in `apps/system_manage/serializers/platform_source.py` and `apps/system_manage/views/platform_source.py`.
- Application platform configuration and readiness gating already exist in `apps/application/serializers/application_platform.py` and `apps/application/views/application_platform.py`.
- Admin login and chat-user login already expose WeCom and DingTalk QR flows in `ui/src/views/login/scanCompinents/`, `ui/src/views/chat/user-login/scanCompinents/`, `ui/src/stores/modules/login.ts`, `ui/src/stores/modules/chat-user.ts`, `ui/src/api/user/login.ts`, and `ui/src/api/chat/chat.ts`.
- Application access UI already exposes callback metadata and provider-specific form fields in `ui/src/views/application/ApplicationAccess.vue` and `ui/src/views/application/component/AccessSettingDrawer.vue`.
- Backend planning evidence indicates generated callback URLs exist, but corresponding runtime handlers are not yet represented as concrete verified routes or provider clients.

## Key Decisions

### 1. Reuse readiness as a prerequisite, not a deliverable

This change treats the archived readiness contract as settled. The new work starts only after a provider is configured and ready, so the change can focus on actual auth and callback execution paths.

### 2. Keep WeCom and DingTalk as separate capabilities under one shared design

WeCom and DingTalk reuse the same repo surfaces and planning concerns, but their provider fields and callback mechanics are already different in current code. Separate capabilities keep requirements truthful while one design document captures the shared execution shape.

### 3. Plan three attachment points together

The codebase already spans the same two providers across:
- admin login
- chat-user login
- application platform access

The design keeps all three attachment points in scope so provider clients and callback endpoints are planned once instead of being split into incompatible follow-up contracts.

### 4. Make provider clients and callback handlers explicit artifacts of implementation

The current codebase shows configuration and UI expectations but not dedicated WeCom or DingTalk runtime clients. The implementation plan should therefore assume explicit provider-specific backend modules for auth-code exchange, signature validation where needed, and callback payload handling.

### 5. Use TDD-shaped execution slices

Because the repo already has targeted tests around provider readiness, the next change should continue with narrow backend tests per flow, followed by frontend wiring verification with `npm run type-check` and `npm run lint`.

## Proposed Execution Slices

1. **Provider runtime contract slice**
   - Define backend client boundaries for WeCom and DingTalk.
   - Define code-exchange and callback endpoint contracts.

2. **Admin and chat-user login slice**
   - Connect existing QR login flows to real backend auth completion endpoints.
   - Define success, failure, and disabled-provider behavior.

3. **Application callback slice**
   - Define provider callback behavior for configured applications.
   - Preserve existing callback metadata exposure in application settings.

## Risks and Constraints

- Existing UI surfaces may imply behavior that backend code does not yet implement; the specs must stay grounded in verified code entry points.
- WeCom and DingTalk use different field names across auth and application configuration, so implementation slices must avoid over-normalizing the saved schema.
- Existing draft integration tests are not yet a reliable source of truth, so new targeted tests should anchor the implementation plan.

## Verification Strategy

- Add narrow Django tests for provider runtime behaviors before each backend slice.
- Reuse targeted readiness tests as regression coverage instead of replacing them.
- Run frontend `npm run type-check` and `npm run lint` for any UI or store wiring changes.
- Keep provider-specific flows independently verifiable so each slice can be reviewed in isolation.
