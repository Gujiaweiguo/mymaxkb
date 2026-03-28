## Why

The archived workspace-and-resource-ownership change defined workspace authority rules, but the current integration coverage does not yet prove that denied-path authorization is enforced through the real `Auth` object path. This change is needed now to lock in a narrow, backend-first authorization baseline before later workspace and resource work builds on unverified assumptions.

## What Changes

- Add denied-path integration coverage for community-edition workspace CRUD and workspace member-management endpoints using real `Auth` objects instead of placeholder tokens.
- Verify that non-ADMIN actors receive 403 responses on workspace management operations that remain ADMIN-only in the current contract.
- Keep the slice backend-first and test-focused; do not widen scope into new workspace roles, member-management redesign, or resource-authorization policy changes.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `workspace-ownership`: tighten the executable contract so denied-path authorization for workspace CRUD and membership operations is explicitly verified through integration coverage.

## Impact

- Affected backend tests in `apps/system_manage/test_integration.py`.
- Affected authentication utility usage in tests via `apps/common/auth/handle/impl/user_token.py` and `apps/common/constants/permission_constants.py`.
- No database schema, API shape, or frontend behavior changes are intended in this slice.
