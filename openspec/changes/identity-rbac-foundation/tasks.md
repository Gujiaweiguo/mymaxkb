## 1. Administrative identity requirements

- [x] 1.1 Map existing system-user management surfaces and backend entry points against the `system-user-management` spec
- [x] 1.2 Define the exact built-in administrative roles and permission categories required for community edition
- [x] 1.3 Confirm which current user fields, filters, and status transitions are mandatory for parity in the first implementation pass

## 2. Authentication foundation planning

- [x] 2.1 Inventory supported admin login methods already surfaced in the repository and align them to the `system-login-authentication` spec
- [x] 2.2 Define which administrative login methods are in-scope for phase-one implementation versus deferred follow-up
- [x] 2.3 Identify the persistence and validation surfaces that must support admin authentication settings

## 3. RBAC implementation planning

- [x] 3.1 Break backend implementation into user lifecycle, role/permission resolution, and admin-auth configuration workstreams
- [x] 3.2 Break frontend implementation into user management, role management, and authentication settings workstreams
- [x] 3.3 Define verification criteria for permission-gated admin surfaces before downstream changes begin

## 4. Cross-change handoff

- [x] 4.1 Record the RBAC terms and permission assumptions that `workspace-and-resource-ownership` must reuse
- [x] 4.2 Record the identity assumptions that `sharing-and-chat-user-access` and `audit-and-system-api` must treat as foundational
- [x] 4.3 Confirm that application-facing access restriction remains outside this change

## 5. Initial implementation slices

- [x] 5.1 Fix community-edition auth fallback so default role-based system and workspace permissions are included in `Auth.permission_list`
- [x] 5.2 Align community-edition user-management payloads with stable role metadata where EE role models are absent
- [x] 5.3 Define and implement community-edition storage and validation for admin login-auth settings
- [x] 5.4 Narrow the first supported admin login-method set and wire the backend config surface to it
- [x] 5.5 Update CE frontend identity-management surfaces to match the supported role and auth capabilities without EE-only affordances
