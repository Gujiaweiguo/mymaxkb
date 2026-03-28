## Why

Read/list denied-path coverage already proved that the current resource-authorization GET endpoints reject non-privileged users correctly. The next smallest unresolved surface is write/edit authorization, which should be verified separately so unauthorized mutation paths cannot hide behind correct read-only behavior.

## What Changes

- Add denied-path integration coverage for resource-authorization write/edit endpoints using real `Auth` objects.
- Verify that non-privileged actors receive forbidden responses when attempting to edit user-resource or resource-user authorization data.
- Keep the slice mutation-only and backend-first; do not widen into serializer refactors, ownership redesign, or cross-workspace sharing semantics.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `resource-management-authorization`: tighten the executable contract so denied-path write/edit authorization for workspace resource-authorization views is explicitly verified.

## Impact

- Affected backend tests in `apps/system_manage/test_integration.py`.
- Affected resource-authorization views in `apps/system_manage/views/user_resource_permission.py` only if tests expose a narrow permission-gate mismatch.
- No API shape, database schema, or frontend behavior changes are intended in this slice unless denied-path tests prove a real authorization flaw.
