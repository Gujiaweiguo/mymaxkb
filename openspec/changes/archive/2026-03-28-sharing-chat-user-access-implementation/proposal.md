## Why

The authorization hardening layer (PR #9) is complete. The next OpenSpec slice implements sharing, chat-user management, and chat-user resource access — features that answer the question: who may access a resource when they are not simply the owning admin actor inside the owning workspace?

The planning change `sharing-and-chat-user-access` (archived 2026-03-25) defined the requirements. This change implements them.

## What Changes

- Implement chat-user and chat-user-group management lifecycle
- Implement shared-resource cross-workspace behavior
- Implement chat-user access control for applications and datasets
- Add denied-path integration tests for all new authorization surfaces
- Fix any authorization gaps discovered by tests (following the same pattern as authorization hardening)

## Capabilities

### New Capabilities
- `chat-user-management`: Chat user and group lifecycle, source tracking, and group assignment
- `chat-user-resource-access`: Chat-user and chat-user-group access control for applications and datasets, including access restriction behavior
- `shared-resources`: Cross-workspace shared resource exposure and consumption

### Modified Capabilities
- None (all specs are new requirements)

## Impact

- Backend chat-user and group models in `apps/system_manage/models/chat_user.py`
- Shared-resource and mapping behavior through `apps/system_manage/models/resource_mapping.py` and `apps/common/utils/shared_resource_auth.py`
- Application and chat authorization paths in `apps/chat/**/*`, `apps/application/**/*`
- Frontend admin surfaces in `ui/src/views/system-chat-user/**/*`, `ui/src/views/system-shared/**/*`
- Application access restriction surfaces in `ui/src/views/application/ApplicationAccess.vue` and `ui/src/views/application/component/AccessSettingDrawer.vue`
