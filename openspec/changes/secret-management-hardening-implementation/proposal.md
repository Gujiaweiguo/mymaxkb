## Why

Secret handling in the codebase is inconsistent: some privileged credentials are masked in read paths, but others are still returned in full and rendered directly in the UI. The smallest and clearest gap is application API keys, which are currently exposed without masking even though system API keys already demonstrate the intended safer behavior.

## What Changes

- define the implementation change for secret management hardening around response-time redaction of stored secrets rather than a broad storage redesign
- add a minimal first slice that masks application API keys in backend list responses and prevents the frontend from treating masked values as copyable raw secrets
- sequence follow-up slices for email/provider/platform secret redaction and, separately, deeper storage hardening such as password hashing or secret-source cleanup

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `secret-management-hardening`: harden how persisted secrets are exposed to administrators by masking returned secret values instead of echoing full stored credentials

## Impact

- Backend application API key serialization in `apps/application/serializers/application_api_key.py`
- Existing application API key backend tests and any new masking coverage under `apps/application/`
- Frontend application API key dialog in `ui/src/views/application-overview/component/APIKeyDialog.vue`
- Follow-up slices may extend to email settings, platform source secrets, and provider credential redaction, but not in the first implementation step
