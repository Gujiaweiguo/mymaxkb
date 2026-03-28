## Why

The repository already flags bootstrap-password users with `require_password_change`, but the safety contract is only partially enforced and has no focused regression coverage. We should first lock down the existing backend enforcement path before expanding into stronger first-use UX and bootstrap-creation changes.

## What Changes

- define the implementation change for default credential safety around bootstrap admin credentials and first-use password hardening
- add a minimal first slice focused on backend tests for `require_password_change` enforcement, allowed password-change paths, and bootstrap-flag behavior
- sequence follow-up slices for remaining gaps: chat-token bypass, admin-created temporary passwords, and mandatory frontend password-change UX

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `default-credential-safety`: implement and verify predictable-bootstrap-credential protections and enforce first-use password rotation behavior

## Impact

- Backend bootstrap credential configuration and enforcement in `apps/maxkb/conf.py`, `apps/users/migrations/0001_initial.py`, `apps/users/migrations/0002_user_require_password_change.py`, and `apps/common/auth/authenticate.py`
- Backend user/login tests in `apps/users/tests.py` and `apps/users/test_integration.py`
- Frontend first-use password UX in `ui/src/layout/layout-header/avatar/index.vue` and `ui/src/layout/layout-header/avatar/ResetPassword.vue` for follow-up slices
