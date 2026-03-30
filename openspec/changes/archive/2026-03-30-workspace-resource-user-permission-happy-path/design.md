## Context

`WorkspaceResourceUserPermissionView` looked unreachable in the prior slice because tests used non-default workspaces and non-matching CE role assumptions. Follow-up tracing showed the endpoint is reachable in CE through the `RoleConstants.WORKSPACE_MANAGE.get_workspace_role()` decorator branch when the request uses `workspace_id='default'` and the caller is an ADMIN user.

## Goals / Non-Goals

**Goals:**
- Add resource-axis happy-path tests for list, page, grant VIEW, and clear with `NOT_AUTH`
- Keep fixtures aligned with CE auth resolution (`default` workspace)
- Verify persisted `WorkspaceUserResourcePermission` rows after edit operations

**Non-Goals:**
- No production permission/decorator changes
- No expansion into custom-role or EE-only workspace role mappings
- No attempt to generalize CE beyond the `default` workspace contract it already uses

## Decisions

1. Extend `apps/system_manage/test_permission_happy_path.py` instead of creating another module so user-axis and resource-axis happy paths stay together.
2. Use `Tool` as the representative resource type again because it has the lightest fixture setup and already exercises the shared serializer logic.
3. Use `Workspace.objects.get_or_create(id='default', defaults={'name': 'default'})` so the URL workspace_id matches CE auth resolution.
4. Use an ADMIN actor for the resource-axis requests because that is the confirmed CE happy path exposed by the existing decorator stack.

## Risks / Trade-offs

- **CE-specific assumption**: tests deliberately lock onto `default` workspace behavior; this is accurate for CE but should not be over-generalized to EE.
- **Single resource type**: still only covers `TOOL`; shared serializer/view logic and existing denied-path suites mitigate the gap.
