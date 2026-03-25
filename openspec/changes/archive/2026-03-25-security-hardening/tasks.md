## 1. Secret source inventory and hardening

- [x] 1.1 Inventory current sensitive fallback values in backend config, startup settings, signing, and RSA helper paths
- [x] 1.2 Classify each current default as sensitive secret material or non-sensitive operational metadata
- [x] 1.3 Remove insecure hardcoded fallback secrets from `apps/maxkb/conf.py`, `apps/maxkb/settings/base/*.py`, and `apps/ops/celery/hmac_signed_serializer.py`
- [x] 1.4 Update secret-handling helpers such as `apps/local_model/serializers/rsa_util.py` to require approved secret sources instead of hardcoded passphrases
- [x] 1.5 Add explicit configuration validation and operator-facing failure messages for missing required sensitive secrets

## 2. Bootstrap credential safety

- [x] 2.1 Identify all code and setup paths that currently depend on predictable default administrator or initialization passwords
- [x] 2.2 Implement the chosen bootstrap credential strategy so installation no longer relies on a standing predictable default password
- [x] 2.3 Enforce first-use credential hardening for bootstrap accounts before normal ongoing administrative use
- [x] 2.4 Update user bootstrap responses, initialization flows, and related checks to match the new credential policy

## 3. Secret scanning guardrails

- [x] 3.1 Add repository secret-scanning configuration for local and CI usage with an initial Gitleaks-focused ruleset
- [x] 3.2 Tune scanner exclusions for vendored, generated, and other high-noise paths such as `.opencode/node_modules`
- [x] 3.3 Add a documented allowlist path for reviewed false positives without broadly suppressing unrelated findings
- [x] 3.4 Add CI automation to run secret scanning on proposed changes and preserve actionable finding details
- [x] 3.5 Define or add a local developer workflow for running secret scans before commit or review

## 4. Documentation and validation

- [x] 4.1 Update deployment and setup documentation to describe required secret inputs and the new bootstrap credential behavior
- [x] 4.2 Document the triage process for scanner findings, including real secret, weak default, and false positive handling
- [x] 4.3 Verify that application startup fails safely when required secret inputs are absent and that non-sensitive defaults still work as intended
- [x] 4.4 Run the configured secret scanners against the repository to confirm tuned exclusions and actionable outputs
