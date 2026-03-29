## Why

The repository already has gitleaks in CI and pre-commit, but the current guardrail is not yet fully tuned to the repo’s real false-positive surface. Several tracked developer/CI files still contain safe placeholder or test-only strings that look like secrets, which makes the scanning contract incomplete and brittle.

## What Changes

- define the implementation change for secret-scanning guardrails around verified scanning behavior and narrowly scoped reviewed exclusions
- add a minimal first slice that validates current gitleaks behavior against the repo and tunes configuration for clearly safe tracked false-positive paths
- sequence follow-up slices for stronger local developer onboarding and any additional scanner coverage if needed

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `secret-scanning-guardrails`: make the repository’s local and CI secret-scanning workflow actionable by aligning exclusions and reviewed exceptions with the current tracked false-positive surface

## Impact

- Gitleaks configuration in `.gitleaks.toml` and reviewed exceptions in `.gitleaksignore`
- Developer/security documentation in `SECURITY.md` and possibly related workflow docs
- CI secret-scanning behavior in `.github/workflows/secret-scan.yml` if verification output or scope tuning is needed
- Example files and test fixtures that may require narrow reviewed allowlisting, such as `.env.local-dev.example`, `docker-compose.dev.yml`, and test-only token fixtures
