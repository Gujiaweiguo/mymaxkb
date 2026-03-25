## Why

The repository already contains workspace management, resource authorization, and workspace-aware permission utilities, but the X-Pack parity goal needs an explicit community-edition contract for workspace ownership and resource scoping. This change isolates those rules so later sharing, chat-user access, and system API work do not redefine resource authority inconsistently.

## What Changes

- Define community-edition workspace lifecycle, membership, and administrative ownership behavior.
- Define resource ownership and resource-authorization behavior for workspace-scoped resources.
- Define how workspace-level authority and resource-level grants relate for supported resource types.
- Establish the ownership assumptions that later sharing and external-control changes must consume.

## Capabilities

### New Capabilities
- `workspace-ownership`: Define workspace creation, membership, ownership, deletion constraints, and administration behavior in community edition.
- `resource-management-authorization`: Define resource scoping, resource-management visibility, and resource-level authorization rules within workspace-aware boundaries.

### Modified Capabilities
- None.

## Impact

- Affected workspace and authorization models including `apps/system_manage/models/workspace_user_permission.py` and related system-management views and serializers.
- Affected shared authorization utilities such as `apps/common/utils/shared_resource_auth.py`.
- Affected administrative frontend surfaces in `ui/src/views/system/workspace/**/*`, `ui/src/views/system/resource-authorization/**/*`, and `ui/src/views/system-resource-management/**/*`.
- Affected workspace and resource-management API clients including `ui/src/api/workspace/workspace.ts`, `ui/src/api/workspace/resource-authorization.ts`, and `ui/src/api/system-resource-management/*`.
