## Why

MaxKB already exposes password-change-required state in the authenticated profile contract and marks administrator-reset users as requiring a password change, but the frontend does not yet enforce that state as a mandatory first-login flow. This leaves a gap between the documented credential-hardening intent and the actual administrative sign-in experience.

## What Changes

- Enforce a mandatory password change flow when a locally authenticated administrative user is marked as requiring password edit.
- Update the admin login and post-login experience so users who require a password change are routed into a dedicated password-update path before normal system use.
- Preserve the existing password reset behavior for authenticated actors, including token invalidation after a successful password update.
- Extend automated coverage for login, current-profile, password-reset, and forced-password-change frontend behavior.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `system-login-authentication`: require the admin experience to enforce the password-change-required profile state before normal navigation continues.
- `system-user-management`: clarify that administrator-driven password resets transition managed users into a mandatory next-login password-change flow.
- `default-credential-safety`: strengthen first-use credential hardening so the required password rotation is enforced in the real sign-in flow rather than documented intent alone.

## Impact

- Backend auth/profile and password update flow under `apps/users/`
- Frontend login, routing, user state, and password update UI under `ui/src/views/login/`, `ui/src/router/`, `ui/src/api/user/`, and related stores
- User/auth regression coverage in Django tests, frontend unit tests, and targeted Playwright login flow coverage
