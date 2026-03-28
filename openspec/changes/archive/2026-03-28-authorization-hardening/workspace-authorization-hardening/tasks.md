## 1. Denied-path workspace authorization contract

- [x] 1.1 Add a spec delta for denied-path workspace authorization verification under `workspace-ownership`
- [x] 1.2 Add backend integration tests that authenticate non-ADMIN users with real `Auth` objects and assert 403 on workspace CRUD endpoints
- [x] 1.3 Add backend integration tests that authenticate non-ADMIN users with real `Auth` objects and assert 403 on workspace member-management endpoints
- [x] 1.4 Validate the slice with the narrowest relevant Django integration test command

## 2. Follow-up decision gate

- [x] 2.1 Record whether the denied-path tests pass unchanged or reveal a production authorization gap that needs a separate hardening slice
  - Denied-path tests revealed a CE authorization gap: `PermissionConstants.WORKSPACE_READ` still granted `RoleConstants.USER`, which allowed non-admin workspace list and member-list access.
  - The slice fixed that gap by narrowing `WORKSPACE_READ` to `RoleConstants.ADMIN` and re-validating the affected integration tests.
