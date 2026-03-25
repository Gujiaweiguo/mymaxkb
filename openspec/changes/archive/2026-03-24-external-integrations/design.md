## Context

The X-Pack scope includes two integration-heavy areas: application channel integrations and Feishu document knowledge ingestion. This repository already shows Lark/Feishu, WeCom, and DingTalk references in application access and authentication-facing UI, plus a dedicated Feishu/Lark document import surface. Those capabilities are operationally different from RBAC and ownership work because they involve external credentials, callback URLs, provider-specific validation, and asynchronous synchronization behavior.

This change is intentionally isolated so integration-specific complexity does not expand the blast radius of the core access-model changes.

## Goals / Non-Goals

**Goals:**
- Define supported third-party application channel integration behavior.
- Define Feishu document knowledge import and synchronization behavior.
- Define planning boundaries for integration credentials, callbacks, and readiness state.
- Keep connector-specific work independently shippable after the access model stabilizes.

**Non-Goals:**
- Defining core administrative identity or workspace ownership semantics.
- Defining chat-user authorization policy itself.
- Defining branding or display customization.
- Defining operation logs or general system API key policy.

## Decisions

### 1. Channel integrations and Feishu knowledge sync stay in one integration-focused change

These capabilities both rely on external-provider configuration, external callback or sync behavior, and provider-specific readiness checks.

**Why this decision:** they share operational and implementation characteristics even though one targets applications and the other targets knowledge ingestion.

**Alternatives considered:**
- Split channel integrations and Feishu knowledge sync into separate changes. Rejected because both are connector-heavy and can still share one integration boundary.

### 2. Existing authentication/provider surfaces are reused conceptually, not re-owned here

This change may consume provider-configuration patterns established elsewhere, but it does not redefine the administrative authentication model.

**Why this decision:** it avoids turning the integration change into a second identity change.

**Alternatives considered:**
- Move provider-specific auth setup fully into this change. Rejected because admin login semantics already belong to the foundation change.

### 3. Connector readiness must be part of the product contract

An integration is not merely configured or not configured; it also has a readiness state driven by valid credentials, callback setup, or source authorization.

**Why this decision:** channel integrations and source sync fail in practice when partial configuration is treated as complete.

**Alternatives considered:**
- Leave readiness as an implementation detail. Rejected because the user-facing behavior materially depends on whether the connector is actually usable.

### 4. The first CE channel wave is limited to WeCom, DingTalk, and Lark

The first community-edition implementation pass should prioritize the three providers that already have the most complete visible surfaces across application access and authentication-related UI: WeCom, DingTalk, and Lark.

**Why this decision:** these providers already appear in application access configuration, scan-login settings, login/chat-user QR flows, and provider/channel enums, so they form the narrowest credible first implementation slice.

**Alternatives considered:**
- Include WeChat public account, Slack, and WeCom Bot in the first wave. Rejected because those providers currently look less complete or more specialized, and would expand the first connector slice before the core provider path is validated.

### 5. First-pass Feishu knowledge support is import-first, not full sync

The first community-edition pass for Feishu-backed knowledge sources should define source configuration, folder browse, and selected `docx` document import behavior first, while deferring scheduled or manual re-synchronization semantics until the backend connector and task surfaces exist.

**Why this decision:** the repository already contains substantial frontend Lark/Feishu knowledge import UI, but the corresponding backend routes, views, and sync tasks are not yet present. Import-first keeps the contract aligned with the smallest realistic implementation slice.

**Alternatives considered:**
- Define full one-way synchronization in the first pass. Rejected because that would overstate current backend readiness and force connector/task design decisions before the import path is validated.

### 6. Readiness requires more than saved configuration

A configured external integration should only be considered ready for active use when all applicable prerequisites are satisfied: credentials are valid, callback metadata is reachable where required, connection validation succeeds, and the integration can actually be enabled or disabled at runtime.

**Why this decision:** saving provider settings alone does not prove the integration can be used successfully, and partial configuration is a common failure mode for external channels and source connectors.

**Alternatives considered:**
- Treat persistence of settings as equivalent to readiness. Rejected because it hides the difference between configured, partially configured, and actually usable integrations.

### 7. Connector state should distinguish configured, ready, enabled, and failed conditions

The planning contract should distinguish at least four operational conditions for external integrations: configured but not yet validated, ready for use, enabled or disabled at runtime, and failed after validation or activation.

**Why this decision:** the repository already uses explicit task and execution state vocabulary for other asynchronous features, and external integrations need the same distinction between saved configuration, successful validation, and runtime health.

**Alternatives considered:**
- Model integrations as a binary configured/not-configured switch. Rejected because it collapses partial configuration, validation failure, and runtime failure into one ambiguous state.

### 8. Feishu first-pass failure handling centers on import visibility, not automated recovery

The first Feishu/Lark knowledge-source pass should explicitly cover authentication failures, inaccessible folders, per-document import failures, and manual retry visibility, while deferring automated resynchronization and conflict-oriented recovery.

**Why this decision:** first-pass Feishu support is import-first, so the most important product behavior is whether import succeeds, fails, or partially fails, not whether the system can automatically reconcile future source changes.

**Alternatives considered:**
- Define scheduled sync, webhook-driven refresh, and retry orchestration in the first pass. Rejected because those behaviors depend on backend connector execution that is not yet part of the minimum CE slice.

### 9. Configuration storage assumptions should separate system provider settings from application or knowledge-specific settings

System-level provider configuration, application-level channel configuration, and knowledge-source configuration should be treated as separate storage concerns even when they share credential or callback concepts.

**Why this decision:** scan-login style provider setup, per-application channel enablement, and Feishu knowledge import each operate at different scope boundaries and should not be collapsed into one generic settings shape during planning.

**Alternatives considered:**
- Treat all provider configuration as one flat global settings object. Rejected because application and knowledge integrations need resource-scoped state, enablement, and validation outcomes.

## Risks / Trade-offs

- **[Risk] Provider capabilities differ widely across WeCom, DingTalk, Lark/Feishu, and WeChat** → **Mitigation:** define a shared connector contract and let provider-specific tasks branch later.
- **[Risk] Feishu document sync may need async or retry behavior not shared by application channels** → **Mitigation:** keep the first pass import-focused and defer sync-specific retry/refresh behavior until the connector path is implemented.
- **[Risk] Integration setup may overlap with chat-user scan-login configuration** → **Mitigation:** treat shared provider metadata as reusable infrastructure while keeping feature ownership separate.
- **[Risk] Persisted configuration may be mistaken for operational readiness** → **Mitigation:** require explicit validation and state transitions before treating an integration as usable.

## Migration Plan

1. Define channel-integration requirements and readiness expectations.
2. Define Feishu document import requirements first, then extend to sync once backend connector surfaces exist.
3. Reference earlier identity and sharing decisions rather than reopening them.
4. Defer provider-specific credential schemas and callback implementation details to execution planning.
5. Treat automated resync, webhook refresh, conflict resolution, and backoff-based retry as post-first-pass extensions.

## Implementation planning notes

### Backend workstreams

1. System-level provider configuration and validation for scan-login style integrations
2. Application-level channel configuration, readiness evaluation, and callback handling
3. Feishu/Lark knowledge import endpoints and execution path for import-first behavior

### Frontend workstreams

1. System authentication provider settings with readiness feedback
2. Application channel configuration with validation and enable/disable feedback
3. Feishu knowledge-source creation and import UI wired to real backend responses
4. Chat-user authentication settings that reflect provider readiness and unsupported states clearly

### Verification scenarios

1. A fully configured integration validates successfully and can be enabled for use
2. A partially configured integration remains saved but not ready, with a visible reason
3. An unusable integration surfaces validation or runtime failure without being treated as active
4. A Feishu import-first source can complete folder browse and selected `docx` import within the saved root-token subtree, follow paginated folder listings so large trees remain complete, report per-item `created` / `skipped` / `failed` outcomes for manual retry visibility, and still avoid implying ongoing sync

### Deferred beyond first pass

1. Scheduled automatic sync
2. Webhook-driven sync or refresh
3. Incremental delta sync
4. Bidirectional synchronization or conflict resolution
5. Automated retry with backoff

## Open Questions

- Which second-wave channels should follow the initial WeCom / DingTalk / Lark rollout?
- Should later Feishu synchronization be modeled as one knowledge-source extension or as a reusable connector framework capability?
- Which provider settings can reuse existing auth-setting storage versus needing dedicated integration configuration?
