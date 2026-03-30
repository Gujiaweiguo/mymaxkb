## Why

Operation-log happy-path and retention behavior are already covered, but there is still no explicit proof that non-admin actors receive 403 across the admin-only operation-log management surface.

## What Changes

- Add denied-path coverage for all admin operation-log endpoints
- Sync the operation-audit-log capability with the denied-access scenario
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `operation-audit-log`: verify non-admin actors cannot access operation-log management endpoints

## Impact

- Extends `apps/system_manage/test_log_management.py`
- Completes the permission-boundary contract for operation-log management in CE
