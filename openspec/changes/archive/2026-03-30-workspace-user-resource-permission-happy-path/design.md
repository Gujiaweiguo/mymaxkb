## Context

The codebase already has two permission-management views in `apps/system_manage/views/user_resource_permission.py`, but only the user-axis view is reachable through a confirmed CE happy path today. Existing tests only prove non-privileged users are denied; they do not prove admins can successfully create, read, and page `WorkspaceUserResourcePermission` rows through `WorkSpaceUserResourcePermissionView`.

## Goals / Non-Goals

**Goals:**
- Add focused happy-path integration tests for admin access to user-axis workspace resource permission endpoints
- Verify `VIEW` and `MANAGE` mappings persist correctly in `WorkspaceUserResourcePermission`
- Verify CE role-list exposure via `WorkspaceRoleListView`
- Capture the current CE limitation around resource-axis happy-path access as an explicit non-goal

**Non-Goals:**
- No production serializer or view changes
- No EE-only custom role or workspace-role-mapping behavior
- No resource-axis happy-path implementation for `WorkspaceResourceUserPermissionView`
- No broad RBAC redesign or custom-role CRUD

## Decisions

1. Use a new test module dedicated to happy-path permission coverage so it stays separate from denied-path suites.
2. Use `TOOL` as the representative resource type because it exercises the user-axis permission-management path with the lightest fixture setup.
3. Authenticate with `get_auth(admin_user)` to match the existing permission decorator pipeline and avoid string-token ambiguity.
4. Verify DB state directly through `WorkspaceUserResourcePermission` after PUT operations rather than inferring success only from response payloads.
5. Leave `WorkspaceResourceUserPermissionView` out of this slice because repeated CE-auth fixture attempts still resolve to 403, indicating a current CE access limitation rather than a missing test.

## Risks / Trade-offs

- **Representative resource choice** → Testing only `TOOL` does not exhaustively cover every resource type; mitigation: serializer/view logic is shared and already validated on denied paths for all resource types.
- **Existing auth noise in legacy tests** → Some older tests log string-token permission warnings; mitigation: new tests use `get_auth()` and do not depend on that behavior.
- **Resource-axis gap remains** → CE still lacks a proven happy path for `WorkspaceResourceUserPermissionView`; mitigation: keep this change narrowly truthful and defer that investigation to a dedicated follow-up.
