## Context

The mymaxkb platform uses a decorator-based authorization system where all workspace-scoped endpoints are protected by `@has_permissions` decorators. The permission model operates at three layers:

1. **System layer**: Role-based (ADMIN, WORKSPACE_MANAGE, USER) with hardcoded permission mappings in `permission_constants.py`
2. **Workspace layer**: Permissions scoped to `/WORKSPACE/{id}` resource paths, checked by `get_workspace_permission()` lambdas in the decorator
3. **Resource layer**: Per-user, per-resource grants via `WorkspaceUserResourcePermission` model with `AuthTargetType` (APPLICATION, KNOWLEDGE, TOOL, MODEL)

Previous changes (PRs #9, #13, #15) hardened `WORKSPACE_READ`, ChatTokenAuth bypass, and cross-domain middleware. PR #9 added denied-path tests for workspace CRUD operations. This change extends that pattern to workspace-scoped resource management endpoints.

The five resource types to verify are: APPLICATION, KNOWLEDGE, MODEL, TOOL, TRIGGER. Each has workspace-scoped URL patterns like `workspace/<str:workspace_id>/...` and uses `@has_permissions` with resource-type-specific PermissionConstants.

## Goals / Non-Goals

**Goals:**
- Verify denied-path authorization for each resource type's management endpoints (list, create, read, update, delete) against a CE USER actor without explicit resource grants
- Verify granted-path authorization where a USER actor with `WorkspaceUserResourcePermission` VIEW/MANAGE grants can access permitted resources
- Fix any discovered gaps minimally (missing decorators, wrong permission constants)

**Non-Goals:**
- Serializer changes or API shape changes
- New permission models or role redesign
- Cross-workspace resource sharing or ownership changes
- Frontend changes
- Write-endpoint expansion beyond existing CRUD

## Decisions

### Decision 1: Test-first approach (verify before fix)
**Choice**: Write integration tests first, then fix any gaps discovered.
**Rationale**: The existing `@has_permissions` infrastructure is mature and covers 39 view files. Most endpoints should already be correctly protected. Writing tests first avoids speculative fixes and ensures we only change what's actually broken.
**Alternative**: Audit all decorators manually and fix proactively. Rejected because manual auditing is error-prone and doesn't produce regression protection.

### Decision 2: Test against real Auth objects, not mocked permissions
**Choice**: Use the same `Auth` object construction pattern from PR #9's denied-path tests (`user_token.py` `get_auth()` flow).
**Rationale**: Mocked auth skips the real permission resolution chain (system → workspace → resource layers). Real Auth objects catch bugs in the actual resolution logic.
**Alternative**: Mock `request.auth.permission_list`. Rejected because it wouldn't catch resolution bugs.

### Decision 3: Focus on CE USER actor with minimal fixtures
**Choice**: Test with a single CE USER actor, a workspace, and the resource under test. No role/permission model mocks needed since CE uses in-memory defaults.
**Rationale**: Matches the production CE configuration where roles are hardcoded. Minimizes fixture complexity.
**Alternative**: Test multiple role combinations. Rejected as out of scope — role coverage was done in prior changes.

### Decision 4: Test each resource type independently
**Choice**: Separate test methods or test classes per resource type (application, knowledge, model, tool, trigger).
**Rationale**: Resource types have different permission groups and operations. Isolating them makes failures easy to diagnose and avoids cascade failures.
**Alternative**: Combined test class. Rejected because one broken resource type would obscure others.

## Risks / Trade-offs

- **[Risk] Some endpoints may lack `@has_permissions` entirely** → Mitigation: The test will produce 200 instead of 403, clearly identifying the gap. Fix is adding the decorator.
- **[Risk] Test DB setup complexity for some resource types (e.g., MODEL needs provider)** → Mitigation: Use minimal fixtures — only create what the view's serializer requires for the permission check, not full resource creation.
- **[Risk] Test running time increases with 5 resource types × multiple operations** → Mitigation: Each test class runs independently; Django test runner handles parallelism within the class.
- **[Trade-off] Not testing all 39 view files** → Accepted. We test the five primary resource types' core CRUD operations. Sub-operations (stats, version, chat-record) can be added incrementally.
