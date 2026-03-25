## Context

The repository already includes operation-log UI and API-key surfaces, plus chat and application models that recognize system API key identity. These are cross-cutting administrative capabilities: they reflect and expose the settled authority model rather than define it. Planning them late reduces the chance that earlier changes force repeated rewrites of audit-event semantics or privileged API behavior.

This change should therefore consume the outcomes of identity, ownership, and delegated-access planning rather than reopen those questions.

## Goals / Non-Goals

**Goals:**
- Define operation-log behavior, filtering, export, and retention expectations.
- Define system API access and API key lifecycle expectations.
- Align privileged API behavior with the settled authorization model.
- Keep audit and external-control surfaces independently reviewable after the core model stabilizes.

**Non-Goals:**
- Defining the underlying role model.
- Defining workspace ownership or delegated chat-user access.
- Defining external application-channel integration behavior.
- Defining branding, theme, or display settings.

## Decisions

### 1. Audit is planned after authority semantics settle

This change assumes earlier planning already defines who is allowed to perform administrative, workspace, and delegated access actions.

**Why this decision:** audit records are only useful if they reflect a stable action and authority model.

**Alternatives considered:**
- Plan operation logs in parallel with identity and workspace changes. Rejected because event vocabulary and filter dimensions could churn repeatedly.

### 2. System API access is modeled as privileged administrative control, not generic public integration

This change defines API key lifecycle and privileged system API access, not every external integration endpoint.

**Why this decision:** it keeps system API behavior distinct from connector-specific integrations and aligns it with administrative control surfaces.

**Alternatives considered:**
- Combine system API with external integrations. Rejected because API key governance and connector setup have different ownership and risk profiles.

### 3. Retention and export are first-class audit behaviors

Operation logs are not complete as a product capability unless administrators can retain, filter, and export them under supported policy.

**Why this decision:** the X-Pack docs present logs as an operational tool, not just a hidden storage table.

**Alternatives considered:**
- Treat retention and export as later improvements. Rejected because they are core user-visible aspects of the feature.

## Risks / Trade-offs

- **[Risk] Existing log capture may be incomplete relative to the final parity target** → **Mitigation:** keep the planning contract focused on required behavior and let implementation inventory current coverage against it.
- **[Risk] API key behavior may overlap with application-level API key or chat identity flows** → **Mitigation:** define this change as the owner of privileged system API credentials only.
- **[Risk] Late discovery of missing event fields could expand implementation scope** → **Mitigation:** include export, filtering, and retention behavior in tasks so implementation validates the full operational surface, not just log insertion.

## Operational Rollout Notes

- System API keys are currently an **admin-managed privileged credential** surface. The avatar API-key entry should remain administrator-only while the backend contract stays global rather than user-scoped.
- Full system API secrets are intentionally returned **only at creation time**. List/read surfaces should treat secrets as masked values, and operational guidance should instruct administrators to copy and store the secret when it is first issued.
- Runtime system-key authentication is intentionally scoped narrowly in the first release. It should be documented as supporting protected system-profile access, not as a blanket replacement for existing user-token authentication across all system endpoints.
- Operation-log retention is currently represented as saved cleanup configuration on `SystemSetting(type=LOG)`. Operational documentation should describe it as configured policy until automated cleanup enforcement is expanded.

## Migration Plan

1. Define operation-log behavior and operational controls.
2. Define privileged system API access and credential lifecycle.
3. Align the planning docs with earlier identity and authorization changes.
4. Defer event-schema and token-storage implementation details to execution planning.

## Open Questions

- Which administrative and resource actions must be considered mandatory audit events in the first release?
- Does community edition require per-key metadata such as expiration, status, and allowed origin controls from day one?
- Which system-profile or documentation surfaces should be considered part of the system API contract versus separate informational endpoints?
