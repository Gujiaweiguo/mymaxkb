## Why

Community edition already exposes user, role, permission, and authentication surfaces, but the X-Pack parity scope requires a clear foundation for who can sign in to the admin system, how administrative identities are managed, and how permissions are assigned and enforced. This change comes first because later workspace, sharing, audit, and API behavior all depend on a stable system-user and RBAC model.

## What Changes

- Define community-edition requirements for system user lifecycle management, including creation, status changes, credential resets, and source tracking.
- Define role and permission management requirements, including built-in roles, custom role boundaries, and permission assignment behavior.
- Define system login authentication requirements for supported administrative sign-in methods and configuration surfaces.
- Establish the identity and RBAC assumptions that later workspace, sharing, and system API changes must reuse.

## Capabilities

### New Capabilities
- `system-user-management`: Define how administrative users are created, updated, disabled, searched, and maintained in community edition.
- `role-and-permission-management`: Define built-in roles, custom role behavior, and permission assignment rules for administrative users.
- `system-login-authentication`: Define how administrative users authenticate into the system and how supported login methods are configured.

### Modified Capabilities
- None.

## Impact

- Affected backend identity and permission surfaces under `apps/users/**/*` and shared permission constants in `apps/common/constants/permission_constants.py`.
- Affected existing administrative frontend surfaces in `ui/src/views/system/user-manage/**/*`, `ui/src/views/system/role/**/*`, and `ui/src/views/system-setting/authentication/**/*`.
- Affected administrative API clients including `ui/src/api/system/user-manage.ts`, `ui/src/api/system/role.ts`, and `ui/src/api/system/auth.ts`.
- Establishes the identity contract consumed by later workspace, sharing, audit, and system API changes.
