## Why

Administrative sign-in already exists in the product, but the OpenSpec mainline does not yet capture or verify the community-edition login contract as a completed implementation slice. We should lock down the existing LOCAL admin login behavior first, then expand into lockout, captcha, and frontend method visibility with a test-first plan.

## What Changes

- define the implementation change for system login authentication around the current community-edition admin sign-in contract
- add a minimal first slice focused on backend LOCAL login success and denial behavior in the existing serializer and API flow
- sequence follow-up slices for lockout/captcha enforcement and frontend visibility of enabled versus disabled sign-in methods

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `system-login-authentication`: implement and verify configured administrative sign-in behavior, starting with the existing LOCAL admin login path in community edition

## Impact

- Backend login flow in `apps/users/serializers/login.py`, `apps/users/views/login.py`, and related user tests
- Login auth settings in `apps/system_manage/views/login_auth_setting.py` and `apps/system_manage/serializers/login_auth_setting.py`
- Frontend admin login page and auth-setting rendering in `ui/src/views/login/index.vue` and `ui/src/views/system-setting/authentication/component/Setting.vue`
- Existing test suites in `apps/users/tests.py`, `apps/users/test_integration.py`, and `ui/src/__tests__/views/login.test.ts`
