## Context

`SharedResourceAuthorizationView` is a narrow admin-only API around `SharedResourceAuthorizationSerializer`. The serializer and utility behavior are already covered by `apps/system_manage/tests.py` and `apps/common/utils/test_shared_resource_auth.py`, but there is no APIClient-based happy-path integration test proving the routing, `TokenAuth`, and `@has_permissions(RoleConstants.ADMIN)` stack succeeds for admins.

## Goals / Non-Goals

**Goals:**
- Add integration tests for admin GET default response
- Add integration tests for admin POST create and overwrite behavior
- Add integration coverage for `KNOWLEDGE` resource type in addition to `TOOL`

**Non-Goals:**
- No production serializer/view changes
- No duplicate unit-level validation-path coverage already present in `apps/system_manage/tests.py`
- No consumer-side cross-workspace usage tests

## Decisions

1. Extend `apps/system_manage/test_integration.py` so all integration authorization tests remain co-located.
2. Reuse `APIClient` with `get_auth(admin_user)` for the admin actor, matching the working pattern in other recent integration slices.
3. Use both `Tool` and `Knowledge` fixtures so we cover the two supported shared resource types without broadening beyond the serializer’s actual enum map.

## Risks / Trade-offs

- These tests intentionally overlap some serializer happy-path behavior, but only at the API integration layer, which is the missing evidence today.
