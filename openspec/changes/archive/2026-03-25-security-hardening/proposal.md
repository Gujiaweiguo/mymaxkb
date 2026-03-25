## Why

The repository currently does not show strong evidence of committed live API keys, but it does contain several hardcoded secrets, predictable fallback values, and default credentials that weaken the security baseline. These issues should be addressed now so that future deployments do not inherit unsafe defaults and so secret scanning becomes part of normal development rather than a one-off audit.

## What Changes

- Remove or tightly constrain hardcoded and fallback secrets used for application startup, encryption, and message signing.
- Strengthen default credential handling so initialization paths do not rely on predictable passwords or publicly documented weak defaults.
- Add repository-level secret scanning guardrails for local development and CI to catch newly introduced secrets before they are merged.
- Define the expected behavior when required secrets are missing so the system fails safely instead of silently falling back to insecure values.

## Capabilities

### New Capabilities
- `secret-management-hardening`: Define requirements for loading sensitive values from environment or approved configuration sources without insecure hardcoded fallbacks.
- `default-credential-safety`: Define requirements for bootstrap credentials and initialization flows so default passwords are not reused as a standing security mechanism.
- `secret-scanning-guardrails`: Define requirements for automated secret detection in the repository, including local and CI enforcement paths.

### Modified Capabilities
- None.

## Impact

- Affected backend configuration and startup paths, including `apps/maxkb/conf.py`, `apps/maxkb/settings/base/web.py`, `apps/ops/celery/hmac_signed_serializer.py`, and secret-handling helpers such as `apps/local_model/serializers/rsa_util.py`.
- Affected user bootstrap and password initialization behavior in `apps/users/views/user.py` and related setup flows.
- Affected repository tooling and developer workflow through the addition of secret scanning commands, configuration, and CI/pre-commit checks.
- May require deployment and operations updates to ensure required secret values are explicitly provided in runtime environments.
