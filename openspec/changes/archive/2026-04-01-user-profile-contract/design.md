## Context

`UserProfileView` returns `result.success(UserProfileSerializer().profile(request.user, request.auth))`. The serializer emits identity, source, role, permissions, password-edit flag, language, workspace membership, and role-name fields. Existing integration coverage only asserted HTTP 200, leaving the payload contract effectively unpinned.

## Goals / Non-Goals

**Goals:**
- Verify the current-profile endpoint returns the expected identity and membership fields for an authenticated user
- Verify the password-change flag is surfaced for a local actor with `require_password_change=True`

**Non-Goals:**
- No production changes to profile serialization
- No expansion into workspace-scoped profile endpoints or language-switch behavior
- No frontend profile tests

## Decisions

1. Add a dedicated `UserProfileContractIntegrationTests` class to `apps/users/test_integration.py` so the users-domain endpoint contracts stay together.
2. Use real auth objects from `get_auth(user)` so the view receives the same `role_list` and `permission_list` structures as production.
3. Assert the stable payload contract rather than over-constraining the full role-list contents, since CE returns both base roles and workspace-scoped role strings.

## Risks / Trade-offs

- The slice intentionally verifies the live payload shape, including the current workspace object format and populated permission list, instead of forcing a narrower contract than the endpoint actually returns.
