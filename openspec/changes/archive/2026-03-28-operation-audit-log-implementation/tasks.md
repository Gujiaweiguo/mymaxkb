## 1. Operation-log lifecycle exploration

- [x] 1.1 Review the existing log model, clean-time setting flow, and scheduler patterns used by other cleanup jobs
- [x] 1.2 Identify the smallest missing backend seam needed to enforce operation-log retention cleanup

## 2. Minimal retention cleanup slice

- [x] 2.1 Implement a scheduled cleanup job for expired operation logs using the existing `clean_time` setting
- [x] 2.2 Register the cleanup job in the shared scheduler bootstrap
- [x] 2.3 Add backend tests proving expired logs are removed and newer logs are retained
- [x] 2.4 Run narrow log-management backend tests and fix any cleanup gaps discovered

## 3. Follow-up audit coverage slice

- [x] 3.1 Add focused regression coverage for the `@log()` decorator write path
- [x] 3.2 Evaluate whether any important administrative operations still bypass audit logging and decide if they belong in this change

## 4. Packaging and verification

- [x] 4.1 Run full audit-log-related backend tests
- [x] 4.2 Package the change into atomic commits and create a PR
