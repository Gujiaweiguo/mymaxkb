## Context

The repository already ships a meaningful secret-scanning foundation: `.github/workflows/secret-scan.yml` runs gitleaks in CI, `.pre-commit-config.yaml` wires local gitleaks hooks, `.gitleaks.toml` extends the default rule set, `.gitleaksignore` contains reviewed suppressions, and `SECURITY.md` documents the triage model. The main remaining problem is not missing infrastructure but incomplete tuning: several tracked, safe files still contain secret-like placeholder or test-only values that can make the workflow noisy or brittle.

The clearest first slice is to validate the current scanner output against the checked-in tree, then narrow the reviewed exclusions for the currently known false-positive classes such as `.env.local-dev.example`, `docker-compose.dev.yml`, CI-only workflow secrets, and test-only token fixtures.

## Goals / Non-Goals

**Goals:**
- Start with a small, verifiable guardrail slice that makes existing gitleaks behavior actionable
- Add only narrow reviewed exclusions and allowlists for known safe tracked content
- Preserve real-secret detection by avoiding broad path suppression where a narrower rule will do

**Non-Goals:**
- Replacing gitleaks with a different scanning tool in the first slice
- Building a full custom secret-classification framework
- Scanning gitignored local `.env` files or developer machines beyond documented workflows

## Decisions

### 1. Start with configuration tuning and verification, not new tooling

**Why:** the repo already has CI and local scanning wired up. The smallest missing seam is reliable tuning against the repo’s current false-positive surface, not missing scanner infrastructure.

**Alternative considered:** add a second scanner immediately. Rejected because the current gitleaks setup should be made trustworthy before adding layered complexity.

### 2. Prefer narrow path-based exclusions for clearly safe tracked files

**Why:** files like `.env.local-dev.example` and `docker-compose.dev.yml` are tracked and intentionally contain development placeholders or non-production defaults. Narrow path allowlists for those exact files are safer than broad regex suppression across the repository.

**Alternative considered:** broad rule-level suppression for token/password-like patterns. Rejected because that would weaken real-secret detection in unrelated files.

### 3. Use one explicit repo-level verification step as the acceptance signal

**Why:** the fastest way to prove the guardrail works is to run gitleaks against the repo tree with the checked-in config and confirm there are no unreviewed findings after tuning.

**Alternative considered:** rely only on existing CI workflow success. Rejected because CI may not make it obvious which tracked false positives are still untreated until the tuning is explicit and reproducible locally.

## Risks / Trade-offs

- **[Risk] A path allowlist could hide a future real secret in the same file** → **Mitigation:** only allowlist files whose contents are intentionally placeholder/test-only and document that decision in `SECURITY.md`
- **[Risk] Scanner output may vary between local and CI modes** → **Mitigation:** standardize one documented local verification command using the repo’s checked-in config
- **[Risk] Broad test-file exclusions could suppress real secrets accidentally committed to tests** → **Mitigation:** prefer reviewed file-level allowlists first; use broader test-path exclusions only if the narrower approach proves unmanageable

## Migration Plan

1. Run a baseline gitleaks scan against the repository using the checked-in config
2. Add the smallest reviewed exclusions/allowlists needed for clearly safe tracked files
3. Update `SECURITY.md` with the local verification and reviewed-exception workflow if needed
4. Re-run the same scan to confirm a clean actionable baseline

## Open Questions

- Should test-only fixture paths receive broad allowlisting, or should exceptions remain file-specific for now?
- Is a follow-up CI verification step needed in `ci.yml`, or is the dedicated `secret-scan.yml` workflow sufficient once tuned?
