## Context

`WorkspaceRoleListView` in `apps/system_manage/views/workspace.py` is guarded by `@has_permissions(PermissionConstants.WORKSPACE_READ, RoleConstants.ADMIN)`. Existing tests already cover the administrator happy path in `test_permission_happy_path.py`, so the missing value is a single denied-path assertion for a CE `USER` actor.

## Goals / Non-Goals

**Goals:**
- Verify a regular USER receives 403 on the workspace role-list endpoint
- Sync the main role-and-permission spec with that denied-path contract

**Non-Goals:**
- No view or serializer changes
- No expansion into workspace member or role-mutation endpoints
- No response-body assertions beyond the stable forbidden contract

## Decisions

1. Extend `test_permission_happy_path.py` so the denied-path test lives beside the existing role-list happy path.
2. Reuse `PermissionHappyPathMixin.create_ce_user()` and `setup_authenticated_client()` to keep auth setup identical to the rest of the file.
3. Record the capability change as one denied scenario in `role-and-permission-management`.

## Risks / Trade-offs

- This slice is intentionally tiny, so it improves contract coverage without expanding into adjacent workspace authorization surfaces.
