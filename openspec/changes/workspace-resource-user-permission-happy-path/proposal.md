## Why

The CE codebase already supports resource-axis permission management through `WorkspaceResourceUserPermissionView`, but our previous happy-path slice intentionally excluded it after using the wrong workspace/auth fixture shape. Follow-up analysis confirmed the endpoint is testable in CE when requests target the synthetic `default` workspace and use an ADMIN actor.

## What Changes

- Add CE happy-path integration tests for `WorkspaceResourceUserPermissionView` list, page, and edit flows
- Reuse the existing `test_permission_happy_path.py` module and fixture helpers
- Keep scope limited to tests and OpenSpec artifacts; no production code changes

## Capabilities

### Modified Capabilities

- `workspace-user-resource-permission`: add verified CE resource-axis happy-path coverage

## Impact

- Extends backend integration coverage for the resource-axis permission endpoints
- Documents the required CE fixture shape (`workspace_id='default'`, ADMIN actor)
