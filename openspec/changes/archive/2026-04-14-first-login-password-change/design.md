## Context

The backend already carries most of the password-change-required state needed for this change. `apps/users/models/user.py` stores `require_password_change`, `apps/users/serializers/user.py` exposes that state to the admin profile contract as `is_edit_password` for local users, and `apps/common/auth/authenticate.py` blocks flagged users from calling most authenticated APIs except a small whitelist (`/user/profile`, `/user/current/reset_password`, `/user/logout`, `/user/language`). Administrator-driven password reset already sets the flag in `UserManageSerializer.Operate.re_password`, and both self-service password reset flows clear the flag in `ResetCurrentUserPassword.reset_password` and `RePasswordSerializer.reset_password`.

The missing piece is the admin frontend enforcement flow. After login, `ui/src/stores/modules/login.ts` fetches `user.profile()`, and `ui/src/router/index.ts` only checks for token presence and profile loading before allowing normal navigation. The UI does have a forced password dialog in `ui/src/layout/layout-header/avatar/ResetPassword.vue`, and `ui/src/layout/layout-header/avatar/index.vue` auto-opens it when `user.userInfo?.is_edit_password` is true, but that behavior only runs after the normal application shell has mounted. That leaves a gap where the user is routed to `home` first and only later sees the forced dialog, which is weaker than a dedicated first-login gate and is fragile if layout timing changes.

This change spans backend auth state, frontend routing, and test coverage, but it does not require a new authentication model or a new password API. The design should reuse the existing backend contract and password update endpoint while making the frontend enforcement explicit and unavoidable.

## Goals / Non-Goals

**Goals:**
- Enforce a mandatory password change flow for authenticated local admin users whose profile reports `is_edit_password=true`.
- Prevent flagged users from reaching normal admin pages until `/user/current/reset_password` succeeds.
- Reuse existing backend password reset semantics, including token invalidation after successful password change.
- Keep administrator-driven password reset behavior aligned with the forced next-login experience.
- Add regression coverage for backend gate behavior, profile signaling, frontend route enforcement, and the forced password change user journey.

**Non-Goals:**
- Redesign the general forgot-password or email-code reset flow.
- Extend forced password change behavior to non-local auth sources such as LDAP, CAS, OIDC, or QR-login providers.
- Change password policy, token format, or the underlying authentication scheme.
- Refactor the entire avatar/profile UX beyond what is necessary to support the forced flow.

## Decisions

### 1. Use a dedicated authenticated route for mandatory password change

The forced flow should move from an avatar-mounted dialog side effect to an explicit route, such as a dedicated authenticated page under the admin app. The router already has unauthenticated password-recovery routes (`/forgot_password`, `/reset_password/:code/:email`), so adding a separate authenticated route keeps the concern clear: this is not account recovery, it is post-login security enforcement.

**Why this approach:** a route-level gate runs before the user enters normal navigation, survives refreshes, is easier to verify in tests, and avoids depending on the header avatar component being mounted.

**Alternatives considered:**
- **Keep the existing avatar dialog only.** Rejected because it is mounted too late in the flow and is tied to a particular layout component.
- **Show a full-screen modal from the login page after successful login.** Rejected because it complicates refresh handling and does not create a stable deep-link target for route guards.

### 2. Enforce the flow in the global router guard using the existing `user.profile()` contract

`ui/src/router/index.ts` should become the single routing authority for forced password change. After token validation and profile loading, the guard should check `user.userInfo?.is_edit_password`. If the flag is true, any route other than the dedicated forced-password-change route should redirect to that route. If the flag is false and the user manually navigates to the forced-password-change route, the guard should redirect them to the normal post-login destination.

This keeps the frontend aligned with the backend API gate in `authenticate.py`: the router blocks normal page access in the UI, while the backend remains the final server-side enforcement layer for protected APIs.

**Alternatives considered:**
- **Perform the redirect only in `views/login/index.vue` after `asyncLogin`.** Rejected because it would not cover refreshes, direct URLs, or third-party login callbacks that also hydrate the profile.
- **Rely entirely on backend 1002 errors and handle them in a generic interceptor.** Rejected because it produces a poorer UX and makes the intended flow less explicit.

### 3. Reuse the existing reset-current-password API and preserve logout-after-success behavior

The current endpoint `/user/current/reset_password` already clears `require_password_change` and invalidates the current token in `ResetCurrentUserPasswordView`. The frontend forced flow should keep using `UserApi.resetCurrentPassword()` and continue the current post-success behavior: close/reset UI state, log the user out, and send them back to the login page so they reauthenticate with the new credential.

**Why this approach:** it avoids introducing token-refresh edge cases or a second “password changed but still logged in” mode. It also matches the backend contract that deletes the current token after password change.

**Alternatives considered:**
- **Keep the session alive after password change by refetching profile.** Rejected because the backend explicitly invalidates the current token, so the frontend would need a broader auth contract change.

### 4. Extract or wrap the existing forced dialog into a route-friendly component instead of duplicating form logic

`ui/src/layout/layout-header/avatar/ResetPassword.vue` already contains the validation rules, forced-mode behavior, and success handling for current-user password reset. The implementation should reuse that form logic by either:
- moving the form body into a shared component that can be used by both the avatar dialog and the dedicated route, or
- wrapping the existing forced dialog in a route component with minimal adaptation.

The design preference is to extract the password form into a shared component and keep the avatar menu entry as a non-forced entry point to the same underlying form. That avoids drift between “voluntary change password” and “mandatory change password” behavior.

**Alternatives considered:**
- **Create a second independent page implementation.** Rejected because duplicated validation and success flow would drift quickly.

### 5. Enable first-login enforcement for newly created local users by setting the backend flag at creation time

`UserManageSerializer.save()` currently creates local users with `require_password_change=False` and contains a TODO explicitly calling out the missing frontend flow. Once the forced frontend flow exists, newly created local users should be created with `require_password_change=True` so “first-login password change” is real for administrator-created accounts, not only for bootstrap or manually reset accounts.

This change should remain scoped to local users created through administrative user management and should not alter non-local identities.

**Alternatives considered:**
- **Leave creation behavior unchanged and only support admin-reset users.** Rejected because it would not satisfy the stated first-login goal and would leave the existing TODO unresolved.

### 6. Keep backend enforcement narrow and additive rather than redesigning the auth gate

The backend gate in `apps/common/auth/authenticate.py` already protects server-side access. The design should preserve that structure and only update it if the forced frontend flow needs an additional allowed API path. The current design does not require new allowed API paths because the dedicated page can operate using `/user/profile`, `/user/current/reset_password`, `/user/logout`, and `/user/language`, which are already allowed.

**Alternatives considered:**
- **Broaden the whitelist for extra UI helper APIs.** Rejected unless implementation proves it necessary, because every extra path weakens the server-side gate.

## Risks / Trade-offs

- **[Risk] Existing layout-based forced dialog logic may conflict with the new route guard and create double-open behavior.** → Mitigation: move the “auto-open when `is_edit_password`” behavior out of the avatar container or scope it so it does not fire on the dedicated forced route.
- **[Risk] Third-party login callbacks (`dingCallback`, `wecomCallback`, `larkCallback`) also hydrate profile and could be accidentally redirected despite not using local passwords.** → Mitigation: keep frontend enforcement keyed strictly to the backend-provided `is_edit_password` flag, which is already false for non-local users.
- **[Risk] Redirect loops if the guard runs before profile is available or if the forced route itself triggers profile fetches incorrectly.** → Mitigation: centralize the check after `await user.profile()` and explicitly exempt the dedicated forced route from the redirect-to-self path.
- **[Risk] Changing newly created local users to `require_password_change=True` could surprise existing admin workflows.** → Mitigation: cover the behavior with user-management tests and document that admin-created temporary passwords are now one-time credentials.
- **[Risk] Logout-after-password-change adds one extra sign-in step for the user.** → Mitigation: keep the UX explicit and predictable, and rely on the existing backend token invalidation behavior rather than introducing a more complex session transition.

## Migration Plan

1. Update the OpenSpec specs for login authentication, user management, and default credential safety to reflect enforced behavior.
2. Implement the frontend dedicated forced-password-change route and router guard enforcement.
3. Refactor the existing current-password-reset UI so the avatar menu and forced route share the same form behavior.
4. Enable `require_password_change=True` for newly created local administrative users.
5. Add and run regression coverage for backend contracts, frontend route behavior, and the forced password change journey.

**Deployment / rollout:** No data migration is required for the core route-enforcement work because the flag and endpoints already exist. Existing flagged users will start seeing the enforced flow immediately after deployment. New local users created after deployment will enter the first-login path automatically if creation behavior is updated as designed.

**Rollback:** Revert the frontend route guard and dedicated route changes first to restore current behavior, then revert the user-creation flag default if needed. Backend password reset and profile signaling can remain because they are already compatible with the pre-change UI.

## Open Questions

- Should the forced route be a standalone page under the login-style shell or a minimal authenticated page inside the admin app shell? The preferred direction is a login-style shell with authenticated API access so the user is not exposed to normal navigation while blocked.
- Should administrator-created users always be flagged for first-login password change, or only users created with generated temporary passwords? The design assumes all local admin-created credentials should be treated as temporary unless product requirements say otherwise.
- Do we want an explicit backend login response hint in addition to the existing profile flag, or is the current `user.profile()` fetch sufficient? The current design assumes the existing profile fetch is sufficient and avoids expanding the login contract unless implementation friction appears.
