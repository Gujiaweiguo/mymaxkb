## Context

The workspace hardening follow-up used real `Auth` objects in integration tests and exposed a concrete CE permission issue that placeholder tokens had hidden. Resource authorization sits behind a more complex permission matrix in `apps/system_manage/views/user_resource_permission.py`, including `ViewPermission`, workspace-manager role checks, and resource-path checks, so the next safe step is to validate denied-path read/list behavior before touching any write flows.

## Goals / Non-Goals

**Goals:**
- Add integration coverage for denied-path GET endpoints on resource-authorization views.
- Use real `get_auth(user)` objects so tests exercise the same permission shape as production requests.
- Keep failures diagnostic: if a test fails, the result should point to a specific permission gate mismatch.

**Non-Goals:**
- Testing PUT/edit endpoints in this slice.
- Refactoring `ResourceUserPermissionSerializer` or `UserResourcePermissionSerializer` behavior.
- Redefining ownership rules, cross-workspace sharing, or role models.

## Decisions

### 1. Start with read/list endpoints only

This slice covers denied-path GET access for:
- `WorkSpaceUserResourcePermissionView.get`
- `WorkSpaceUserResourcePermissionView.Page.get`
- `WorkspaceResourceUserPermissionView.get`
- `WorkspaceResourceUserPermissionView.Page.get`

**Why this decision:** read/list endpoints provide the smallest backend-only surface and avoid the higher risk of mixing policy validation with mutation semantics.

### 2. Use non-ADMIN, non-workspace-manager actors first

The first denied-path tests should authenticate plain CE `USER` actors without additional resource grants or workspace-manager roles.

**Why this decision:** this mirrors the workspace slice and gives the clearest signal on whether view-level permission gates are already too permissive.

### 3. Treat any failure as a focused follow-up fix

If denied-path tests fail, fix only the specific permission gate or constant that allowed the request unexpectedly.

**Why this decision:** it preserves a narrow reviewable slice and avoids speculative authorization redesign.

## Risks / Trade-offs

- **[Risk] Resource authorization views may depend on resource fixtures beyond simple user setup** → **Mitigation:** start with the narrowest supported resource type and build only the minimal fixture data needed for list/read requests.
- **[Risk] Failures may reflect ownership semantics, not just missing permission gates** → **Mitigation:** stop at the first precise mismatch and keep write flows out of scope.
- **[Risk] Existing integration tests may not yet cover these endpoints at all** → **Mitigation:** add new tests alongside current coverage rather than reshaping unrelated tests.

## Migration Plan

1. Add a spec delta for denied-path resource-authorization read/list verification.
2. Add integration tests for non-privileged users hitting resource-authorization GET endpoints.
3. Run the narrowest test target and inspect any authorization mismatch.
4. If needed, apply a minimal permission fix in a single follow-up code edit.

## Open Questions

- Which resource type gives the least setup friction for the first denied-path GET tests: `APPLICATION`, `KNOWLEDGE`, `TOOL`, or `MODEL`?
- Do the current CE defaults already grant any implicit read visibility that should be treated as expected rather than as a bug?
