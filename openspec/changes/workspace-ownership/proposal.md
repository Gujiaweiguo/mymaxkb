## Why

The workspace-ownership spec defines workspace lifecycle, membership, ownership, and administrative authority, but integration tests only cover basic CRUD, default workspace deletion protection, and ADMIN-only authorization denial. Deletion constraint enforcement (workspace cannot be deleted while resources exist) is untested for each of the 10 constraint types, and default workspace member-management immutability is not verified at the integration level.

## What Changes

- Add integration tests for workspace deletion constraints: verify each of the 10 constrained resource types (application, application_folder, knowledge, knowledge_folder, knowledge_workflow, tool, tool_folder, model, trigger, resource_permission) independently blocks workspace deletion
- Add integration test verifying default workspace rejects member management (add, list, remove)
- Add integration test verifying workspace name uniqueness enforcement on create and update
- Add integration test verifying workspace update via POST with `id` field (the only supported update path)
- No production code changes

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `workspace-ownership`: Add integration-tested scenarios for deletion constraints, default workspace member immutability, name uniqueness, and update path

## Impact

- New test file: `apps/system_manage/test_workspace_ownership.py`
- No production code changes
- Builds on existing test patterns from `test_integration.py` and `test_resource_auth.py`
