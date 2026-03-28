## 1. Backend default-credential enforcement exploration

- [x] 1.1 Review bootstrap credential creation and flagging paths in config loading and user migrations
- [x] 1.2 Review current runtime enforcement in authentication middleware and identify uncovered backend seams

## 2. Minimal backend enforcement slice

- [x] 2.1 Add backend tests for `require_password_change` blocking on non-whitelisted paths
- [x] 2.2 Add backend tests for allowed password-change/session-management paths and profile `is_edit_password` signaling
- [x] 2.3 Add backend coverage for bootstrap-password flagging behavior in the existing migration/runtime contract
- [x] 2.4 Run narrow backend tests and fix any discovered enforcement gaps

## 3. Backend gap hardening slice

- [x] 3.1 Add tests covering `ChatTokenAuth` or equivalent bypass paths for flagged users
- [x] 3.2 Fix the bypass if tests expose a real enforcement gap and rerun the relevant backend tests
- [x] 3.3 Evaluate admin-created temporary password flows and decide whether `require_password_change=True` belongs in this change or a follow-up

## 4. Frontend first-use hardening slice

- [x] 4.1 Add or update frontend coverage for mandatory password-change UX driven by `is_edit_password`
- [x] 4.2 Implement the minimal frontend behavior needed to prevent dismissing first-use password hardening if required by the spec
- [x] 4.3 Run frontend tests, type-check, and lint

## 5. Packaging and verification

- [x] 5.1 Run full login/user-related backend tests
- [x] 5.2 Run frontend type-check and lint
- [x] 5.3 Package the change into atomic commits and create a PR
