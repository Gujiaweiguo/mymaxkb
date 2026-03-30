## Why

Workspace role-list happy-path coverage already proves that administrators can read the role options, but there is still no explicit denied-path proof that non-admin actors receive 403 on the same endpoint.

## What Changes

- Add denied-path coverage for the workspace role-list endpoint
- Sync the role-and-permission-management capability with the denied-access scenario
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `role-and-permission-management`: verify non-admin actors cannot list workspace roles

## Impact

- Extends `apps/system_manage/test_permission_happy_path.py`
- Closes the permission-boundary gap for `GET /admin/api/role_list/current_user`
