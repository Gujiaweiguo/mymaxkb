## Why

Workspace authorization hardening already proved that denied-path integration coverage can expose real CE permission gaps that existing allow-path tests missed. Resource authorization has a separate view-layer permission surface, so it needs its own narrow denied-path read/list verification before write or ownership semantics are touched.

## What Changes

- Add denied-path integration coverage for resource-authorization read/list endpoints using real `Auth` objects.
- Verify that actors without sufficient authority receive forbidden responses when reading user-resource or resource-user authorization data.
- Keep the slice read-only and backend-first; do not expand into authorization writes, sharing semantics, or serializer refactors.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `resource-management-authorization`: tighten the executable contract so denied-path read/list authorization for workspace resource-authorization views is explicitly verified.

## Impact

- Affected backend tests in `apps/system_manage/test_integration.py`.
- Affected resource-authorization views in `apps/system_manage/views/user_resource_permission.py` only insofar as tests validate their existing permission gates.
- No API shape, database schema, or frontend behavior changes are intended in this slice unless tests expose a narrow permission mismatch.
