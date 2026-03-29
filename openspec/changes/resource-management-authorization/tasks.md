## 1. Test Infrastructure

- [ ] 1.1 Create shared test helpers for resource-management authorization tests (workspace, user, auth setup, permission grant helpers)
- [ ] 1.2 Add test fixture factories for minimal resource creation (application, knowledge, model, tool, trigger)

## 2. Denied-Path Integration Tests

- [ ] 2.1 Add denied-path tests for APPLICATION CRUD operations by CE USER without resource grant
- [ ] 2.2 Add denied-path tests for KNOWLEDGE CRUD operations by CE USER without resource grant
- [ ] 2.3 Add denied-path tests for MODEL CRUD operations by CE USER without resource grant
- [ ] 2.4 Add denied-path tests for TOOL CRUD operations by CE USER without resource grant
- [ ] 2.5 Add denied-path tests for TRIGGER CRUD operations by CE USER without resource grant

## 3. Granted-Path Integration Tests

- [ ] 3.1 Add granted-path tests for VIEW permission — list/read succeeds, write operations denied
- [ ] 3.2 Add granted-path tests for MANAGE permission — all CRUD operations succeed

## 4. Gap Fixes (if discovered)

- [ ] 4.1 Fix any endpoints missing `@has_permissions` decorator discovered during testing
- [ ] 4.2 Fix any incorrect permission constants discovered during testing

## 5. Verification

- [ ] 5.1 Run full test suite — all new and existing tests pass
- [ ] 5.2 Verify no serializer, model, or frontend changes were needed (confirming narrow scope)
