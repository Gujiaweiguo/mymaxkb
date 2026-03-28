## 1. Denied-path resource-authorization contract

- [x] 1.1 Add a spec delta for denied-path resource-authorization read/list verification under `resource-management-authorization`
- [x] 1.2 Add backend integration tests that authenticate non-privileged users with real `Auth` objects and assert 403 on user-resource authorization read/list endpoints
- [x] 1.3 Add backend integration tests that authenticate non-privileged users with real `Auth` objects and assert 403 on resource-user authorization read/list endpoints
- [x] 1.4 Validate the slice with the narrowest relevant Django integration test command

## 2. Follow-up decision gate

- [x] 2.1 Record whether denied-path read/list tests pass unchanged or expose a narrower permission-gate mismatch that needs a focused production fix
  - Denied-path read/list tests passed unchanged for the targeted `TOOL` resource authorization endpoints.
  - No additional production permission fix was required in this slice.
