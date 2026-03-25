## Context

This repository already exposes user, role, permission, and authentication management surfaces across backend and frontend layers. The X-Pack parity target expands those capabilities into a more explicit administrative identity foundation, so the first planning change must stabilize the system-user, role, permission, and admin-login model before later changes add workspace ownership, chat-user access, or privileged API behavior.

The main constraint is that later changes should consume a single vocabulary for administrative identity and RBAC rather than independently redefining who counts as an administrator, how permission checks are resolved, or which login methods govern the admin UI.

## Goals / Non-Goals

**Goals:**
- Define the canonical community-edition administrative identity model.
- Define built-in and custom role behavior at the planning level.
- Define the administrative login-authentication contract for supported methods.
- Establish permission vocabulary that later changes can reuse.

**Non-Goals:**
- Defining workspace ownership and resource-scoping rules.
- Defining chat-user or chat-user-group management.
- Defining shared-resource behavior.
- Defining app-display, branding, audit-log, or system API feature details.

## Decisions

### 1. Administrative identity and RBAC stay separate from chat-user identity

This change owns the system-user and admin-login model only. Chat-user identity remains a later, external-facing access layer.

**Why this decision:** the repository already distinguishes administrative and chat-facing surfaces, and mixing them would make later application and dataset access rules harder to reason about.

**Alternatives considered:**
- Plan system users and chat users together. Rejected because they serve different control planes and would blur admin and end-user access.

### 2. Login authentication is part of the foundation, but app access restriction is not

This change defines administrative sign-in behavior for the system. Application-facing password or chat-user access restriction belongs in the later sharing-and-chat-user-access change.

**Why this decision:** the admin entry point is foundational infrastructure, while application access restriction depends on chat-user and resource-access semantics.

**Alternatives considered:**
- Put all authentication-related behavior into one change. Rejected because admin login and application chat access have different actors and downstream dependencies.

### 3. RBAC definitions must become the shared contract for later changes

Later changes may add workspace-, resource-, or API-specific rules, but they should not redefine the base administrative role and permission contract.

**Why this decision:** it reduces cross-change drift and avoids reworking permission semantics after downstream planning is already written.

**Alternatives considered:**
- Let each later change define its own role interpretations. Rejected because that would create overlapping authority models.

## Risks / Trade-offs

- **[Risk] Existing permission constants and UI affordances may already encode assumptions not yet documented** → **Mitigation:** keep specs normative and let implementation map existing constants and guards back to the shared RBAC contract.
- **[Risk] Administrative login methods may differ materially in rollout complexity** → **Mitigation:** keep this change at the contract level and defer provider-specific implementation sequencing to tasks and later implementation planning.
- **[Risk] Downstream changes may try to add new identity concepts without updating the foundation** → **Mitigation:** explicitly treat this change as the source of truth for system-user and administrative RBAC terminology.

## Migration Plan

1. Define the community-edition contract for system users, roles, permissions, and admin login methods.
2. Align later workspace, sharing, audit, and system API planning docs to reuse that contract.
3. Defer implementation-specific provider rollout and admin UX details to the execution phase.

## Open Questions

- Which built-in roles should remain immutable versus customizable in community edition?
- Which administrative login methods should be considered in-scope for the first parity release versus later expansion?
- Does community edition require distinct permission inheritance behavior for custom roles, or is flat assignment sufficient at the planning level?
