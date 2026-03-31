## Why

The authenticated `valid/*` endpoint already had a single success-path test, but it still lacked explicit proof for the main CE enforcement branches: rejecting non-matching counts, rejecting requests after the application quota is exhausted, and bypassing CE enforcement when a valid license is present.

## What Changes

- Add CE enforcement coverage for wrong-count and quota-exhausted application validation
- Add licensed-bypass coverage for application validation
- Sync the system-user-management capability with these validation behaviors
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `system-user-management`: verify CE validation enforcement and licensed bypass behavior for the application validation endpoint

## Impact

- Extends `apps/system_manage/test_valid_and_public_auth.py`
- Strengthens coverage for `GET /admin/api/valid/application/<count>` without changing serializer logic
