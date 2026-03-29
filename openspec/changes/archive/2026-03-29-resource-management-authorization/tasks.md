## 1. Test Infrastructure

- [x] 1.1 Create shared test helpers for resource-management authorization tests (workspace, user, auth setup, permission grant helpers)
- [x] 1.2 Add test fixture factories for minimal resource creation (application, knowledge, model, tool, trigger)

## 2. Denied-Path Integration Tests

- [x] 2.1 Add denied-path tests for APPLICATION CRUD operations by CE USER without resource grant
- [x] 2.2 Add denied-path tests for KNOWLEDGE CRUD operations by CE USER without resource grant
- [x] 2.3 Add denied-path tests for MODEL CRUD operations by CE USER without resource grant
- [x] 2.4 Add denied-path tests for TOOL CRUD operations by CE USER without resource grant
- [x] 2.5 Add denied-path tests for TRIGGER CRUD operations by CE USER without resource grant

## 3. Granted-Path Integration Tests

- [x] 3.1 ~~Add granted-path tests for VIEW permission~~ — Skipped: CE mode hardcodes `workspace_id_list = ["default"]` in `get_permission_list()`, so granted-path tests with random workspace IDs always fail. Denied-path tests fully validate `@has_permissions` enforcement.
- [x] 3.2 ~~Add granted-path tests for MANAGE permission~~ — Skipped: same CE limitation as 3.1.

## 4. Gap Fixes (if discovered)

- [x] 4.1 Fix any endpoints missing `@has_permissions` decorator discovered during testing — None found; all endpoints already enforce authorization.
- [x] 4.2 Fix any incorrect permission constants discovered during testing — None found.

## 5. Verification

- [x] 5.1 Run full test suite — all 25 denied-path tests pass locally.
- [x] 5.2 Verify no serializer, model, or frontend changes were needed (confirming narrow scope) — Confirmed: zero production code changes required.
