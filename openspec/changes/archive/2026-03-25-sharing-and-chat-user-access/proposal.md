## Why

The X-Pack feature set treats shared resources, chat users, user groups, and per-resource access controls as closely related capabilities, and this repository already has concrete chat-user, group, shared-resource, and permission surfaces. They should be planned together so community edition can define one coherent model for external-facing resource access instead of scattering the rules across applications, datasets, and shared workspace flows.

## What Changes

- Define community-edition shared-resource behavior across workspaces for supported resource types.
- Define chat user and chat user group lifecycle behavior, including membership and source synchronization boundaries.
- Define application- and dataset-facing chat-user authorization behavior, including allow/deny rules and assignment semantics.
- Define how application access restriction depends on password-based or authenticated chat-user access paths.

## Capabilities

### New Capabilities
- `shared-resources`: Define how supported resources are exposed across workspaces and how authorized workspaces consume them.
- `chat-user-management`: Define chat user and chat user group management behavior, including source tracking and group assignment.
- `chat-user-resource-access`: Define chat-user and chat-user-group access control for applications and datasets, including access restriction behavior.

### Modified Capabilities
- None.

## Impact

- Affected backend chat-user and group models in `apps/system_manage/models/chat_user.py` and related chat-user authorization paths used by application and chat flows.
- Affected shared-resource and mapping behavior through `apps/system_manage/models/resource_mapping.py`, `apps/system_manage/views/resource_mapping.py`, and `apps/common/utils/shared_resource_auth.py`.
- Affected application and chat authorization paths that already reference chat-user identity in `apps/chat/**/*`, `apps/application/**/*`, and knowledge-search authorization flows.
- Affected frontend administrative surfaces in `ui/src/views/system-chat-user/**/*`, `ui/src/views/system-shared/**/*`, and application access surfaces such as `ui/src/views/application/ApplicationAccess.vue` and `ui/src/views/application/component/AccessSettingDrawer.vue`.
