## 1. Backend login contract exploration

- [x] 1.1 Review the current LOCAL admin login flow in `apps/users/serializers/login.py` and `apps/users/views/login.py`
- [x] 1.2 Identify existing backend login tests and the smallest missing contract cases in `apps/users/tests.py` and `apps/users/test_integration.py`

## 2. Minimal backend LOCAL login slice

- [x] 2.1 Add focused backend tests for successful LOCAL admin login, invalid password denial, and disabled-user denial
- [x] 2.2 Run the narrow users test modules and fix any contract gaps discovered

## 3. Follow-up backend hardening slice

- [x] 3.1 Add tests for login lockout and captcha behavior driven by login auth settings
- [x] 3.2 Run the relevant backend tests and fix any discovered issues

## 4. Frontend login visibility slice

- [x] 4.1 Replace placeholder login view tests with real component-level coverage for enabled and disabled sign-in methods
- [x] 4.2 Verify frontend type-check and lint after login view test updates

## 5. Packaging and verification

- [ ] 5.1 Run full Django login-related tests
- [ ] 5.2 Run frontend type-check and lint
- [ ] 5.3 Package the change into atomic commits and create a PR
