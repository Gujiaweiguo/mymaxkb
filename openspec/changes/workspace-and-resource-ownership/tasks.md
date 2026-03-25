## 1. Workspace authority definition

- [x] 1.1 Map existing workspace creation, deletion, membership, and listing surfaces against the `workspace-ownership` spec
- [x] 1.2 Define required deletion constraints, membership rules, and authority transitions for the first implementation pass
- [x] 1.3 Confirm which workspace actions require system-level authority versus workspace-level authority

## 2. Resource ownership and authorization planning

- [x] 2.1 Inventory supported resource-management and resource-authorization surfaces that must align to the `resource-management-authorization` spec
- [x] 2.2 Define the baseline authorization matrix for workspace-scoped resources and direct resource grants
- [x] 2.3 Identify resource types that can inherit the shared ownership contract versus those needing special-case implementation tasks

## 3. Implementation breakdown

- [x] 3.1 Break backend implementation into workspace lifecycle, membership enforcement, and resource-authorization alignment workstreams
- [x] 3.2 Break frontend implementation into workspace management, resource-authorization UI, and resource-management visibility workstreams
- [x] 3.3 Define validation scenarios for allowed access, denied access, and workspace-deletion constraints

## 4. Cross-change handoff

- [x] 4.1 Record the ownership assumptions that `sharing-and-chat-user-access` must consume rather than redefine
- [x] 4.2 Record the authorization assumptions that `audit-and-system-api` must reuse for privileged control surfaces
- [x] 4.3 Confirm that cross-workspace sharing remains out of scope until the next change

## 5. Initial implementation slices

- [x] 5.1 Add a community-edition `Workspace` model and system workspace CRUD/list/delete-check backend contract
- [x] 5.2 Enforce initial workspace deletion constraints for known workspace-scoped resource families before delete
- [x] 5.3 Allow CE system admins to reach `/system/workspace` through `loadPermissionApi('workspace')` and route gating
- [x] 5.4 Hide unsupported CE workspace member-management UI until member endpoints are implemented
- [x] 5.5 Implement CE workspace member list/add/remove backend and re-enable the member panel
- [x] 5.6 Extend resource-management and resource-authorization surfaces to consume non-default workspaces end-to-end
  - [x] APPLICATION resource-authorization now consumes non-default workspaces in CE admin mode via workspace-specific member enumeration and workspace selection UI
  - [x] APPLICATION system resource-management now has a repo-local CE list endpoint, CE route access, workspace filtering, and only exposes supported operations
