## Why

Operation logs and system API exposure are cross-cutting administrative capabilities, and the repository already includes log-management and API-key surfaces. They should be planned after identity, ownership, and sharing rules are clear so audit events and privileged API contracts reflect the final authority model instead of forcing rework later.

## What Changes

- Define community-edition requirements for operation log capture, filtering, export, and retention management.
- Define community-edition requirements for system API access, including API key lifecycle and privileged administrative control surfaces.
- Define how audit and API behavior depend on the settled identity, workspace, and authorization model.
- Establish a late-stage control-surface contract that later implementation can verify against the earlier planning changes.

## Capabilities

### New Capabilities
- `operation-audit-log`: Define administrative operation logging, filtering, export, and retention behavior in community edition.
- `system-api-access`: Define system API exposure, API key management, and privileged access behavior in community edition.

### Modified Capabilities
- None.

## Impact

- Affected backend log and profile surfaces in `apps/system_manage/views/log_management.py`, `apps/system_manage/models/system_setting.py`, `apps/system_manage/api/system.py`, and `apps/system_manage/views/system_profile.py`.
- Affected frontend administrative surfaces in `ui/src/views/system/operate-log/**/*` and system API key clients in `ui/src/api/system/api-key.ts` and `ui/src/api/system/operate-log.ts`.
- Depends on final identity, permission, workspace, and sharing semantics established by earlier changes.
- May affect privileged chat and application access flows where system API keys are already represented as chat user types.
