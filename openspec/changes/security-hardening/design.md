## Context

The current repository scan did not show strong evidence of live third-party API keys committed in the active tree, but it did reveal several security baseline problems in source-controlled code: hardcoded fallback secrets, predictable default credentials, and secret-handling logic that can continue operating when required values are missing. The change also spans developer workflow because preventing regressions requires repository-level secret scanning rather than relying only on manual review.

This work affects multiple modules: backend configuration loading, Django startup settings, Celery signing, RSA secret handling, user bootstrap flows, and repository automation. The design therefore needs to define how the application behaves when required secrets are absent and how secret scanning is introduced without creating unmanageable false positives.

## Goals / Non-Goals

**Goals:**
- Require sensitive runtime secrets to come from explicit environment or approved configuration sources instead of insecure hardcoded fallbacks.
- Remove or constrain predictable default passwords and bootstrap credential behavior so they are not treated as long-lived security controls.
- Add repository guardrails that scan for committed secrets locally and in CI.
- Keep the rollout operationally practical by distinguishing hard failures for true secrets from allowlisted documentation, examples, and UI strings.

**Non-Goals:**
- Replace the entire authentication model or redesign all user-management flows.
- Re-architect all credential storage for model providers beyond the specific hardcoded secret issues identified in this audit.
- Deliver a full application-security program covering unrelated concerns such as XSS, SSRF, CSRF, or dependency vulnerability management.
- Rewrite repository history as part of this change unless follow-up investigation proves an actual leaked live credential exists.

## Decisions

### 1. Sensitive configuration must fail closed instead of silently falling back

The application will distinguish between non-sensitive defaults (for example hostnames or ports) and sensitive settings such as Django secret keys, signing keys, encryption passphrases, and similar secret material. Sensitive values should be sourced from environment variables or an approved external configuration source. If they are missing, startup or the affected feature path should fail with a clear operator-facing error rather than substituting an insecure default.

**Why this decision:** a running system with a predictable fallback secret is harder to notice and more dangerous than an explicit startup failure.

**Alternatives considered:**
- Keep current fallbacks and document them better. Rejected because documentation does not reduce exploitability.
- Auto-generate missing secrets on startup. Rejected for this phase because generated values can break clustered deployments, key continuity, and operational reproducibility unless carefully designed.

### 2. Bootstrap credentials must be treated as one-time setup inputs, not standing defaults

Default administrator or initialization passwords should not remain predictable after installation. The preferred behavior is to require an explicitly provided bootstrap password or force first-use rotation before the account can be used as a normal long-lived credential.

**Why this decision:** documented default passwords are operationally convenient but create a known attack path when deployments are left unchanged.

**Alternatives considered:**
- Preserve a documented default admin password. Rejected because it normalizes insecure production posture.
- Randomly generate a password and only print it once. Partially acceptable, but operational UX and delivery channel need explicit design in implementation; therefore this is a possible implementation path, not the design requirement itself.

### 3. Secret scanning should use layered enforcement with tuned scope

Repository guardrails should combine a fast local scanner and a CI scanner. Gitleaks is the best fit for fast local and CI pattern scanning, while TruffleHog remains useful for deeper git scanning and validation-oriented follow-up. Scanner configuration must exclude noisy vendor/generated paths and allowlist known non-secret examples where justified.

**Why this decision:** a single scanner either produces too much noise or misses useful classes of findings. A layered model keeps developer feedback fast while preserving deeper audit coverage.

**Alternatives considered:**
- Use only detect-secrets. Rejected as the main guardrail because baseline-heavy workflows add overhead before the repository has a well-tuned rule set.
- Use only TruffleHog. Rejected because it is heavier for routine local prevention and is better as complementary depth than the sole first-line check.

### 4. False-positive control is part of the design, not a later cleanup task

Initial scanning configuration should explicitly exclude paths such as vendored dependencies, generated assets, and known documentation/example content that contains words like `password`, `token`, or `secret` without storing real credentials. Allowlisting should be narrow and reviewable.

**Why this decision:** if the initial guardrail is too noisy, developers will bypass it and the control will fail socially even if it is technically present.

**Alternatives considered:**
- Start with strict default scanning everywhere and tune later. Rejected because the first rollout should be usable enough to gain adoption.

## Risks / Trade-offs

- **[Risk] Startup failures increase after removing secret fallbacks** → **Mitigation:** document required variables, validate configuration early, and provide actionable error messages.
- **[Risk] Existing deployments may depend on documented default passwords or fallback behavior** → **Mitigation:** introduce migration notes and a staged rollout path that makes unsafe configuration visible before enforcing harder failures where possible.
- **[Risk] Secret scanning may generate developer friction through false positives** → **Mitigation:** start with tuned excludes and allowlists, and keep exceptions narrow and auditable.
- **[Risk] Changing secret-handling behavior can affect compatibility across services or workers** → **Mitigation:** identify all consumers of signing/encryption material and keep key-source behavior consistent across web, task, and local-model paths.

## Migration Plan

1. Inventory all sensitive fallback values and classify them into runtime-critical secrets versus low-risk defaults.
2. Update code paths so sensitive values come from explicit configuration and fail safely when absent.
3. Update bootstrap credential handling to eliminate standing predictable defaults.
4. Add secret scanning configuration and local/CI execution paths with tuned exclusions.
5. Validate deployment documentation so required secret inputs are clear before enforcement tightens.

**Rollback strategy:** if enforcement causes unexpected operational failures, revert to the previous release while preserving any rotated real secrets. Do not restore removed insecure defaults as an emergency workaround without explicit risk acceptance.

## Open Questions

- Should bootstrap credential hardening require an operator-supplied password, a generated one-time password, or a forced password-reset flow on first login?
- Which secret sources are acceptable beyond environment variables, if any, for this repository's deployment model?
- Should CI block on all gitleaks findings immediately, or begin in report-only mode until exclusions are stabilized?
