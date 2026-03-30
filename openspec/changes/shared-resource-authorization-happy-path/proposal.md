## Why

Shared resource authorization already has denied-path integration coverage and unit-level happy-path coverage, but there is no integration test proving an admin can successfully GET and POST shared resource authorization through the real API routing and auth stack.

## What Changes

- Add admin happy-path integration tests for shared resource authorization GET/POST endpoints
- Cover default GET behavior, create, overwrite, and knowledge-type support
- Keep scope limited to tests and OpenSpec artifacts; no production code changes

## Capabilities

### Modified Capabilities

- `shared-resources`: verify admin can configure and retrieve shared resource authorization through the API layer

## Impact

- Extends `apps/system_manage/test_integration.py`
- Strengthens end-to-end evidence for shared-resource configuration in CE
