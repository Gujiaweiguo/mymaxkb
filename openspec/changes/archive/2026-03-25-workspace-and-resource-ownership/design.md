## Context

The repository already contains workspace lists, member management, workspace-aware permission constants, user-resource permission tables, resource-mapping infrastructure, and shared authorization helpers. That means community edition does not need a speculative workspace model invented from scratch; it needs a stable planning boundary that defines ownership and resource scope before later changes add shared access, chat-user access, or external API control.

This change depends on the identity and RBAC foundation because workspace authority is still exercised by system users under the administrative permission model. It is intentionally narrower than the full X-Pack bundle: its job is to define primary ownership and authorization, not every downstream access path.

## Goals / Non-Goals

**Goals:**
- Define workspace lifecycle, membership, and administrative authority behavior.
- Define resource ownership and resource-management visibility within workspace-aware boundaries.
- Define the relationship between workspace authority and resource-level authorization.
- Create the ownership baseline that later sharing and system API changes must consume.

**Non-Goals:**
- Defining cross-workspace sharing policy.
- Defining chat-user or chat-user-group authorization.
- Defining application-channel integrations or knowledge-source connectors.
- Defining audit-log retention or system API key behavior.

## Decisions

### 1. Workspace ownership is the primary authority model

This change defines who administers a workspace, who manages membership, and how workspace authority constrains resource administration.

**Why this decision:** later shared-resource or delegated-access behavior only makes sense after the primary workspace authority is settled.

**Alternatives considered:**
- Plan sharing and ownership together. Rejected because it would merge primary authority and delegated access into one oversized slice.

### 2. Resource authorization is defined here, not in the sharing change

This change owns the primary model for resource visibility and authorization. Later changes may extend access through sharing or chat-user policies, but they should not redefine primary resource authority.

**Why this decision:** existing workspace/resource-authorization surfaces are already closer to ownership semantics than to downstream sharing semantics.

**Alternatives considered:**
- Move all resource authorization into the sharing change. Rejected because shared access is downstream of primary ownership.

### 3. Resource-type differences are handled under a shared ownership contract

Supported resources may vary in details, but they should inherit a common ownership and authorization vocabulary rather than each introducing independent rules at the planning level.

**Why this decision:** it keeps the planning set coherent and avoids six separate resource-specific mini-designs.

**Alternatives considered:**
- Write separate ownership models for each resource type. Rejected because it would fragment the change and create unnecessary drift.

## Risks / Trade-offs

- **[Risk] Existing resource-management surfaces may not align perfectly across all resource types** → **Mitigation:** define a shared baseline and capture type-specific exceptions only where they materially change authorization behavior.
- **[Risk] Workspace deletion and membership constraints may differ from current behavior in subtle ways** → **Mitigation:** keep deletion and membership rules explicit in specs and avoid inferring behavior from UI alone.
- **[Risk] Later sharing work may attempt to reopen primary ownership semantics** → **Mitigation:** treat this change as the source of truth for primary workspace and resource authority.

## Migration Plan

1. Define the workspace authority model and its lifecycle constraints.
2. Define resource-authorization behavior for workspace-scoped resources.
3. Reference this ownership model from later sharing, audit, and API planning docs.
4. Defer resource-type implementation mapping and data migration details to execution planning.

## Open Questions

- Does community edition need an explicit distinction between workspace owner and workspace administrator at the planning level?
- Which resource types need first-class authorization scenarios versus inheriting a common resource contract?
- Should per-resource grants be treated as direct grants, role-derived grants, or both in the first implementation pass?
