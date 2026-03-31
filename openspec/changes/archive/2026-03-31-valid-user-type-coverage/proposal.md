## Why

The `valid` endpoint now has solid application-path CE enforcement coverage, but it still lacked the same contract checks for the remaining supported `user` valid type.

## What Changes

- Add CE allowance, wrong-count, quota-exhausted, and licensed-bypass coverage for `GET /admin/api/valid/user/<count>`
- Sync the system-user-management capability so the CE validation scenarios cover the implemented user path as well as the application path
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `system-user-management`: verify CE validation behavior for the supported user-count path on the `valid` endpoint

## Impact

- Extends `apps/system_manage/test_valid_and_public_auth.py`
- Completes the shipped CE `user` branch of `ValidSerializer.valid()` without touching the unresolved dataset/knowledge mismatch
