## Context

`views/log_management.py` exposes five admin-only operation-log endpoints: log page, menu options, export, clean-time read, and clean-time save. Existing tests in `test_log_management.py` already cover admin happy paths and retention behavior, so the missing value is explicit denied-path coverage for regular users.

## Goals / Non-Goals

**Goals:**
- Verify a regular USER receives 403 on the operation-log page endpoint
- Verify a regular USER receives 403 on menu-option and export endpoints
- Verify a regular USER receives 403 on clean-time read and save endpoints

**Non-Goals:**
- No production view or serializer changes
- No response-body assertions beyond the stable forbidden contract
- No expansion into unrelated audit-log filtering or export semantics

## Decisions

1. Extend `test_log_management.py` so denied-path checks live beside the existing operation-log coverage.
2. Use `APIClient` with `get_auth(user)` to exercise the same permission-resolution path used by recent admin API tests.
3. Sync the main `operation-audit-log` spec with a single denied-access scenario covering the five admin endpoints.

## Risks / Trade-offs

- The denied-path test asserts status codes only, which keeps the slice stable but provides less route-level debugging detail if a future endpoint regresses.
