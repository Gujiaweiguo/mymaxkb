## Context

The current codebase already contains a bootstrap-password hardening mechanism, but it is unevenly enforced. Admin bootstrap creation reads `MAXKB_DEFAULT_PASSWORD` through config loading, migration `0002_user_require_password_change` marks matching accounts with `require_password_change=True`, and token-based auth middleware blocks most requests until the password is changed. However, this flow has no dedicated regression tests, `ChatTokenAuth` currently skips the password-change gate, and frontend UX still allows a forced-change dialog to be dismissed.

The safest first slice is to verify the backend contract that already exists before changing runtime behavior. That gives us a stable baseline for later fixes to the chat-token bypass and the forced frontend password-change UX.

## Goals / Non-Goals

**Goals:**
- Capture `default-credential-safety` as an active implementation change
- Start with backend tests for the current `require_password_change` contract and bootstrap-flag behavior
- Sequence follow-up work for the bypass and UX gaps without mixing everything into the first PR

**Non-Goals:**
- Replacing the password hashing scheme in the first slice
- Redesigning all login or profile UX in the first slice
- Introducing a new bootstrap secret generation system before existing enforcement is covered

## Decisions

### 1. Start with backend enforcement tests before changing runtime behavior

**Why:** the middleware and migration logic already exist, but there is no focused coverage. Tests are the smallest way to stabilize the contract and expose where enforcement is missing.

**Alternative considered:** immediately fix `ChatTokenAuth` and the frontend dialog bypass. Rejected because it changes runtime behavior before the baseline contract is pinned down.

### 2. Treat `ChatTokenAuth` bypass as the second backend slice

**Why:** the code map shows a concrete gap — `TokenAuth` and `AllTokenAuth` call `_require_password_change()`, but `ChatTokenAuth` does not. Once the baseline tests exist, this becomes a small targeted production fix.

**Alternative considered:** include the bypass fix in the first PR. Rejected to keep the first slice test-first and minimize rollback scope.

### 3. Defer mandatory frontend password-change UX until backend enforcement is covered

**Why:** the frontend already receives `is_edit_password`, but the current dialog can be dismissed. That is a real UX gap, but it depends on the backend contract remaining stable. It is safer as a follow-up slice.

**Alternative considered:** start with the frontend dialog because it is user-visible. Rejected because it is a larger cross-component change than the initial backend-only contract tests.

## Risks / Trade-offs

- **[Risk] Existing middleware tests may be awkward to set up** → **Mitigation:** begin with the smallest serializer/authentication tests that assert blocked versus allowed paths
- **[Risk] The first slice might only document, not close, the `ChatTokenAuth` gap** → **Mitigation:** explicitly sequence the gap as the next backend task rather than leaving it implicit
- **[Risk] Bootstrap secret quality remains only partially enforced** → **Mitigation:** keep that as a later hardening task after first-use rotation enforcement is covered

## Migration Plan

1. Add backend regression tests for `require_password_change` and bootstrap-user flagging
2. Run narrow users/auth tests and fix any discovered backend enforcement gaps
3. Add a focused production fix for the `ChatTokenAuth` bypass in the next slice if tests confirm it
4. Add frontend mandatory password-change UX after backend enforcement is stable

## Open Questions

- Should the second slice fix only `ChatTokenAuth`, or also flip admin-created temporary users to `require_password_change=True`?
- Should bootstrap-secret strength validation be enforced at config load time or through a separate initialization flow?
