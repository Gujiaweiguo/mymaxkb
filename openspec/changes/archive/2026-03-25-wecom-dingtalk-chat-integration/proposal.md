## Why

The repository already exposes WeCom and DingTalk configuration, QR login, and application access surfaces, but the delivered contract so far stops at readiness and saved configuration. This change is needed to define the missing CE behavior for real WeCom and DingTalk chat integration so the existing UI and callback metadata can be backed by bounded, testable backend flows.

## What Changes

- Define community-edition requirements for WeCom chat authentication and application callback integration.
- Define community-edition requirements for DingTalk chat authentication and application callback integration.
- Define the shared design boundaries for provider clients, auth-code exchange, callback or webhook handling, and how these flows attach to existing admin login, chat-user login, and application access surfaces.
- Reuse the existing third-party channel readiness contract instead of reopening provider configuration semantics already delivered in the archived `external-integrations` change.

## Capabilities

### New Capabilities
- `wecom-chat-authentication`: Define how a configured WeCom integration participates in login and application callback flows in community edition.
- `dingtalk-chat-authentication`: Define how a configured DingTalk integration participates in login and application callback flows in community edition.

### Modified Capabilities
- `third-party-channel-integration`: Clarify that ready WeCom and DingTalk integrations expose executable auth and callback behavior rather than configuration-only readiness.

## Impact

- Affects existing login and QR-code surfaces already present in `ui/src/views/login/scanCompinents/`, `ui/src/views/chat/user-login/scanCompinents/`, `ui/src/stores/modules/login.ts`, and `ui/src/stores/modules/chat-user.ts`.
- Affects existing provider and application access surfaces already present in `apps/system_manage/views/platform_source.py`, `apps/application/views/application_platform.py`, `ui/src/views/system-setting/authentication/`, and `ui/src/views/application/`.
- Likely introduces dedicated WeCom and DingTalk backend client and callback handling modules in the chat or shared integration layer.
