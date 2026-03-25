## 1. Chat-user and group planning

- [x] 1.1 Map existing chat-user, chat-user-group, and source-sync surfaces against the `chat-user-management` spec
- [x] 1.2 Define the minimum parity set for chat-user lifecycle, group assignment, and source tracking in community edition
- [x] 1.3 Confirm the first implementation pass for third-party sync and bulk-assignment behavior

## 2. Shared-resource and delegated-access planning

- [x] 2.1 Inventory existing shared-resource and resource-mapping surfaces that must align to the `shared-resources` spec
- [x] 2.2 Define the delegated-access matrix for shared workspaces, applications, and datasets under the `chat-user-resource-access` spec
- [x] 2.3 Define how password-based application restriction and authenticated chat-user access are represented as supported access modes

## 3. Implementation breakdown

- [x] 3.1 Break backend implementation into chat-user management, group authorization, and resource-access enforcement workstreams
- [x] 3.2 Break frontend implementation into system-chat-user, system-shared, and application access-setting workstreams
- [x] 3.3 Define verification scenarios for allow, deny, revoke, and group-based authorization behavior
- [x] 3.4 Add CE knowledge chat-user authorization backend for group and user assignment flows
- [x] 3.5 Register CE knowledge authorization filtering for dataset search/runtime enforcement
- [x] 3.6 Expose CE knowledge chat-user access from knowledge settings using the existing chat-user page
- [x] 3.7 Verify Slice 4 with targeted Django tests plus frontend diagnostics and repo-wide type/lint signal review

## 4. Cross-change handoff

- [x] 4.1 Reuse ownership and primary authorization assumptions from `workspace-and-resource-ownership`
- [x] 4.2 Record provider and access prerequisites that `external-integrations` may reuse without redefining delegated access
- [x] 4.3 Confirm that system admin login semantics remain outside this change
