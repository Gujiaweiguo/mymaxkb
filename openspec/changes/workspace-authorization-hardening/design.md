## Context

The archived workspace-and-resource-ownership change already established that workspace management and membership operations are authority-gated, and the current implementation enforces those gates with `@has_permissions(...)` against `request.auth.role_list` and `request.auth.permission_list`. The remaining gap is validation: the existing integration tests use `force_authenticate(..., token="test-token")`, which bypasses realistic `Auth` construction and does not prove denied-path behavior through the same auth shape used in production.

## Goals / Non-Goals

**Goals:**
- Add integration coverage that uses `get_auth(user)` to build a real `Auth` object.
- Prove that non-ADMIN users receive 403 responses on workspace CRUD and workspace member-management endpoints.
- Keep the slice narrow enough that a failing test would point directly to an authorization gap rather than to broader workspace logic.

**Non-Goals:**
- Changing workspace permission constants or role mappings.
- Enabling `WORKSPACE_MANAGE` for endpoints that are currently ADMIN-only.
- Extending the slice to resource-authorization endpoints in the same pass.
- Refactoring the authentication decorator or token pipeline unless tests prove an actual gap.

## Decisions

### 1. Use real `Auth` objects in integration tests

Denied-path tests will authenticate with `force_authenticate(user=user, token=get_auth(user))` so the request carries the same `Auth` shape (`role_list`, `permission_list`) that production decorators expect.

**Why this decision:** it validates the current permission decorator path instead of testing an artificial shortcut that cannot express role/permission denial correctly.

### 2. Start with workspace CRUD and membership endpoints only

The first follow-up slice covers `/admin/api/workspace*` CRUD, delete-check, member list, add-member, and remove-member endpoints.

**Why this decision:** these endpoints directly implement the `workspace-ownership` spec and already have working allow-path integration tests, so denied-path coverage is the narrowest missing proof.

### 3. Treat authorization failures as test-first findings

If denied-path tests fail, the next slice should harden production authorization based on the specific failure rather than preemptively editing permission logic in this change.

**Why this decision:** it keeps this slice diagnostic and minimal, reducing the risk of speculative auth changes.

## Risks / Trade-offs

- **[Risk] Existing tests may rely on permissive shortcuts** → **Mitigation:** add new denied-path tests alongside existing allow-path tests instead of rewriting the entire suite.
- **[Risk] `get_auth(user)` may depend on setup data not present in tests** → **Mitigation:** keep test fixtures aligned with the current CE user model and only assert current ADMIN-only boundaries.
- **[Risk] This slice does not yet cover resource-authorization denied paths** → **Mitigation:** keep that as the next follow-up once workspace endpoint enforcement is proven.

## Migration Plan

1. Add a narrow spec delta for denied-path workspace authorization verification.
2. Add integration tests for non-ADMIN denial on workspace CRUD and member endpoints.
3. Run the narrowest backend integration test target and inspect failures.
4. Only if tests expose a real gap, follow up with a production authorization hardening slice.

## Open Questions

- Does the current CE `get_auth(user)` path already grant any workspace-scoped roles to non-ADMIN users that need explicit fixture setup in tests?
- After workspace endpoint denial is proven, should the next slice target resource-authorization views or `WORKSPACE_MANAGE` role enablement first?
