## Why

The archived workspace-and-resource-ownership and authorization-hardening changes established workspace CRUD denied-path coverage and narrowed `WORKSPACE_READ` to ADMIN-only. However, resource-management endpoints (application, knowledge, model, tool, trigger) under workspace-scoped URLs have not been systematically verified for denied-path authorization. This change closes that gap by adding integration tests that prove a CE USER actor without explicit resource grants is denied resource-management actions, while a user with grants succeeds — all through the real `@has_permissions` decorator path, not mocked auth.

## What Changes

- Add denied-path integration tests for workspace-scoped resource CRUD endpoints (application, knowledge, model, tool, trigger) proving non-privileged actors receive 403.
- Add granted-path integration tests proving actors with `WorkspaceUserResourcePermission` grants can perform permitted resource operations within their scope.
- Verify the existing `@has_permissions` decorator enforcement is correct for each resource type's read and write operations.
- If gaps are found (endpoints missing `@has_permissions` or using wrong permission constants), fix them minimally.
- Keep the slice backend-first and test-focused; do not widen scope into serializer changes, new permission models, role redesign, or cross-workspace sharing.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `resource-management-authorization`: tighten the executable contract so denied-path and granted-path authorization for workspace-scoped resource management operations (application, knowledge, model, tool, trigger) is explicitly verified through integration coverage.

## Impact

- New backend integration tests in `apps/application/tests.py`, `apps/knowledge/tests.py`, `apps/models_provider/tests.py`, `apps/tools/tests.py`, `apps/trigger/tests.py`.
- Potentially minimal fixes to `@has_permissions` decorators in view files under `apps/*/views/*.py` if coverage reveals gaps.
- No database schema, serializer, API shape, or frontend changes are intended in this slice.
