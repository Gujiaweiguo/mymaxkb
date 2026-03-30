## Context

The workspace ownership spec (`openspec/specs/workspace-ownership/spec.md`) defines three scenarios: workspace creation by authorized administrators, deletion blocked while constrained resources remain, and workspace authority enforced on membership actions. Existing integration tests in `test_integration.py` cover basic CRUD and ADMIN-only denial, but the deletion constraint matrix (10 resource types) and default workspace member immutability are not integration-tested.

## Goals / Non-Goals

**Goals:**
- Integration-test all 10 workspace deletion constraint types independently (each resource type blocks deletion)
- Integration-test default workspace member management rejection (add, page, remove)
- Integration-test workspace name uniqueness on create and update
- Integration-test workspace update via POST with `id` field

**Non-Goals:**
- No production code changes
- No granted-path testing for workspace member operations (already covered in `WorkspaceMemberIntegrationTests`)
- No cross-workspace isolation tests (workspace model has no per-user ownership in CE)
- No changes to the `WorkspaceManageOperateView` (no PUT handler — update is via POST)

## Decisions

1. **Single test file**: All workspace ownership tests in `apps/system_manage/test_workspace_ownership.py` — one TestCase class per scenario group (deletion constraints, member immutability, name uniqueness, update path).

2. **Admin token via simple string**: Workspace CRUD views use `@has_permissions(PermissionConstants.WORKSPACE_*, RoleConstants.ADMIN)`. Admin users can use simple `token="test-token"` for `force_authenticate` since the permission check resolves ADMIN role from the user object. No need for `get_auth()`.

3. **Constraint tests use `delete_check` endpoint**: Rather than calling DELETE and checking for failure, use GET `/workspace/{id}/check` which returns `{can_delete: bool, message: str}`. This is safer and more precise — verifies the constraint check logic without actually deleting.

4. **Resource factories inline**: Each constraint test creates the minimal resource needed for that constraint. No shared factory mixin needed since we're testing a different domain (workspace lifecycle) than the resource auth tests.

## Risks / Trade-offs

- **Default workspace ID**: Tests rely on `"default"` being the sentinel ID. If this changes, tests break. Low risk — it's hardcoded in production code.
- **ForeignKey cascade**: Some resources have FK dependencies (e.g., Tool requires ToolFolder). Tests must create parent resources first. Straightforward but verbose.
