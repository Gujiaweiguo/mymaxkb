## Why

The users-domain integration tests already covered user-manage CRUD and non-admin mutation denial, but the admin batch-delete endpoint still lacked any happy-path or validation-contract coverage.

## What Changes

- Add admin happy-path coverage for `POST /admin/api/user_manage/batch_delete`
- Add empty-user-ID validation coverage for the same endpoint
- Sync the system-user-management capability with the batch-delete success and validation contracts
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `system-user-management`: verify administrators can batch delete system users and cannot submit an empty delete set

## Impact

- Extends `apps/users/test_integration.py`
- Closes the users-domain contract gap for the admin batch-delete endpoint
