## 1. Backend Unit Tests

- [x] 1.1 Add unit tests for `users` module (user model, serializers, services)
- [x] 1.2 Add unit tests for `application` module (app model, serializers, services)
- [x] 1.3 Add unit tests for `knowledge` module (document processing, chunking)
- [x] 1.4 Add unit tests for `common` utilities (auth, encryption, validators)
- [x] 1.5 Add unit tests for `system_manage` module (settings, workspaces)
- [x] 1.6 Add unit tests for `chat` module (chat records, messages)

## 2. Backend Integration Tests

- [x] 2.1 Add integration tests for user API endpoints (CRUD, auth)
- [x] 2.2 Add integration tests for application API endpoints
- [x] 2.3 Add integration tests for knowledge API endpoints
- [x] 2.4 Add integration tests for workspace API endpoints
- [x] 2.5 Add integration tests for chat API endpoints
- [x] 2.6 Add integration tests for system settings API endpoints

## 3. Frontend Unit Tests

- [x] 3.1 Add unit tests for composables (useAuth, usePermission, etc.)
- [x] 3.2 Add unit tests for store modules (application store; user store removed - API was never implemented)
- [x] 3.3 Add unit tests for utility functions (formatting, validation)
- [x] 3.4 Add unit tests for API client functions

## 4. Frontend Component Tests

- [x] 4.1 Add component tests for Login/Authentication views (5 tests)
- [x] 4.2 Add component tests for User Management views (5 tests)
- [x] 4.3 Add component tests for Application Management views
- [x] 4.4 Add component tests for Knowledge Base views
- [x] 4.5 Add component tests for Workspace views

## 5. E2E Tests

- [x] 5.1 Write E2E test for login and authentication flow
- [ ] 5.2 Write E2E test for user creation and management [current suite only verifies navigation, table visibility, and create control presence]
- [ ] 5.3 Write E2E test for workspace creation and switching [current suite only verifies navigation and workspace page layout]
- [ ] 5.4 Write E2E test for application creation and configuration [current suite only verifies landing page, search/create controls, and create-menu visibility]
- [ ] 5.5 Write E2E test for knowledge base document upload [current suite only verifies navigation, heading, and create control presence]
- [ ] 5.6 Write E2E test for chat interaction [current suite verifies chat-shell availability for a published remote-backed app, not full message interaction/error paths]

## 6. Testing Infrastructure

- [x] 6.1 Configure test fixtures and factories for backend
- [x] 6.2 Configure test mocks and stubs for frontend
- [x] 6.3 Create E2E test data setup and teardown
- [x] 6.4 Verify CI pipeline runs all test layers
- [x] 6.5 Document testing procedures in README

## 7. Testing (REQUIRED)

- [x] 7.1 Verify frontend unit tests pass locally
  - Result: vitest 30/30 passed (8 test files)
  - Store tests rewritten to match actual store API
  - `window.MaxKB` mock added to vitest.setup.ts
  - Shared real-view mount helpers added under `ui/src/__tests__/helpers/view.ts`
  - Real view suites added for application, knowledge, and workspace management
- [x] 7.2 Verify backend tests pass locally
  - Narrowed suites pass: `users` targeted checks 6/6, `application.test_integration` 8/8, `chat.test_integration` 8/8, `system_manage.test_integration + system_manage.test_integration_settings + users.test_integration + knowledge.test_integration` 39/39
  - Broad repo-root command passes cleanly: `python apps/manage.py test` → 198 tests, OK
  - Fixes applied: repo-root custom Django test runner, explicit root `.env` loading, local DB test bootstrap, duplicate-fixture cleanup, route/auth contract alignment for admin/chat/workspace APIs, utility compatibility helpers, `User.__str__`, `Application.__str__`, `Knowledge.__str__`, `Workspace.__str__`
  - Current backend command convention: `python apps/manage.py test` is valid from repo root; DB connection is fixed with `.env.local-dev` + `set -a`
- [x] 7.3 Verify all E2E tests pass locally
  - Result: Playwright 14/14 passed (1.1m)
  - Added shared E2E resource tracking and cleanup fixtures under `ui/e2e/fixtures/` and `ui/e2e/helpers/`
  - Verified cleanup-dependent chat flow passes on two consecutive reruns
- [x] 7.4 Verify CI runs all test layers successfully
  - Result: GitHub Actions CI run `23628097501` passed on PR #3 (`fix/comprehensive-testing-validation` -> `v2`)
  - Backend Tests: pass (1m39s)
  - Frontend Tests: pass (1m49s)
  - E2E Tests: pass (5m20s)
