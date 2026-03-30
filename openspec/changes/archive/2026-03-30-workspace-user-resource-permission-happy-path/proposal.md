## Why

The CE RBAC surface already exposes workspace user-resource permission APIs and a workspace role list endpoint, but current tests only cover denied-path behavior. We need positive-path integration tests that prove administrators can grant, read, and page resource permissions successfully.

## What Changes

- Add happy-path integration tests for `WorkSpaceUserResourcePermissionView` list, page, and edit flows
- Add integration coverage for `WorkspaceRoleListView` in CE
- Document the discovered CE limitation that `WorkspaceResourceUserPermissionView` remains unreachable through a happy path under the current CE permission model
- Keep scope to existing CE endpoints and serializers; no production code changes

## Capabilities

### New Capabilities
- `workspace-user-resource-permission`: CE workspace user-resource permission grant and query behavior

### Modified Capabilities

## Impact

- New OpenSpec capability for workspace user-resource permissions
- New integration test module under `apps/system_manage/`
- Validation against existing serializer/view code in `system_manage/serializers/user_resource_permission.py` and `system_manage/views/user_resource_permission.py`
