## 1. Backend password-change state enforcement

- [x] 1.1 Update local user creation in `apps/users/serializers/user.py` so administrator-created local users are marked with `require_password_change=True`.
- [x] 1.2 Confirm the authenticated password-change gate in `apps/common/auth/authenticate.py` supports the forced flow without broadening the whitelist unnecessarily.
- [x] 1.3 Keep the current-profile and current-password-reset serializers/views aligned so `is_edit_password` is exposed for local flagged users and cleared after successful current-password reset.

## 2. Frontend forced password-change flow

- [x] 2.1 Add a dedicated authenticated forced-password-change route in `ui/src/router/routes.ts` for users blocked by `is_edit_password`.
- [x] 2.2 Update the global guard in `ui/src/router/index.ts` to redirect flagged users into the forced-password-change route and redirect unflagged users away from it.
- [x] 2.3 Refactor the current-password-reset UI so the avatar entry point and the forced route share the same password form and success handling.
- [x] 2.4 Remove or scope the existing avatar auto-open behavior so the new forced route does not double-trigger the reset-password UI.
- [x] 2.5 Update login success handling and related authenticated entry paths to rely on the router-guard enforcement rather than post-home dialog behavior.

## 3. Regression coverage and verification

- [x] 3.1 Extend backend user/auth tests to cover local user creation requiring password change, profile signaling, and successful current-password reset clearing the flag.
- [x] 3.2 Extend frontend unit tests for router/login/avatar reset-password behavior so forced users are routed correctly and cannot dismiss the flow before success.
- [x] 3.3 Add or update an end-to-end login scenario that verifies a flagged local user is forced through password change before reaching normal admin pages.
- [ ] 3.4 Run the relevant backend tests, frontend `type-check`, `lint`, `test`, and the targeted Playwright verification for the forced password-change flow.
