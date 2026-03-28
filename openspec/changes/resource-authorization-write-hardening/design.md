## Context

The previous read/list hardening slice showed that resource-authorization GET endpoints are already denying non-privileged users correctly. The next adjacent risk surface is mutation: `WorkSpaceUserResourcePermissionView.put` and `WorkspaceResourceUserPermissionView.put` both update authorization state and therefore deserve their own denied-path verification before any broader resource-authorization work continues.

## Goals / Non-Goals

**Goals:**
- Add denied-path integration coverage for the two resource-authorization PUT endpoints.
- Use real `get_auth(user)` objects so tests exercise production permission decorators rather than placeholder tokens.
- Keep failures diagnostic and isolate any resulting fix to a specific permission gate if one is exposed.

**Non-Goals:**
- Re-testing read/list endpoints in this slice.
- Refactoring `UserResourcePermissionSerializer.edit` or `ResourceUserPermissionSerializer.edit` unless tests prove the view-level permission checks are insufficient.
- Expanding into role/ownership redesign or resource-sharing model changes.

## Decisions

### 1. Test only the two PUT endpoints

This slice covers denied-path mutation access for:
- `WorkSpaceUserResourcePermissionView.put`
- `WorkspaceResourceUserPermissionView.put`

**Why this decision:** these are the minimal write surfaces adjacent to the already-verified read/list endpoints, and they keep the review surface small.

### 2. Start with a plain CE `USER` actor and minimal `TOOL` fixtures

The first denied-path tests should use a non-privileged `USER` with no extra workspace-manager or resource grants, plus the simplest resource fixture type already used in read/list tests.

**Why this decision:** it minimizes setup and gives the clearest signal on whether mutation permission gates are too permissive.

### 3. Treat serializer changes as a last resort

If tests fail, first inspect the permission decorator path. Only touch serializer mutation logic if the request is denied correctly at the view layer but still mutates state unexpectedly.

**Why this decision:** it avoids widening a permission-gate slice into business-logic refactoring.

## Risks / Trade-offs

- **[Risk] PUT payload validation may fail before permission checks** → **Mitigation:** use minimally valid request bodies so the tests measure authorization, not schema rejection.
- **[Risk] Some mutation paths may rely on workspace-manager semantics rather than simple ADMIN/USER role checks** → **Mitigation:** stop at the first precise mismatch and avoid bundling multiple policy changes.
- **[Risk] This still leaves resource-sharing and ownership semantics for later slices** → **Mitigation:** keep those explicitly out of scope so this slice stays reviewable.

## Migration Plan

1. Add a spec delta for denied-path resource-authorization write verification.
2. Add integration tests for non-privileged PUT access on the two mutation endpoints.
3. Run the narrowest test target and inspect failures.
4. If needed, apply a minimal permission-gate fix only.

## Open Questions

- Do the PUT endpoints reject unauthorized requests before request-body validation, or do we need fully valid payloads to hit the permission decorators consistently?
- If a failure appears, is it view-level permission drift or serializer-side mutation leakage?
