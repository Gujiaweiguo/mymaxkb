## Context

The repo already has mixed secret-handling behavior. System API keys are masked in list responses, model-provider credentials are decrypted and then selectively redacted before returning, and some tool/knowledge secrets are obscured in UI-facing responses. But application API keys still use a serializer with `fields = "__all__"`, so the full `secret_key` is returned in list responses and rendered directly in the application overview UI. This is the clearest secret-exposure gap because it already has a working system-level precedent inside the same product.

Other higher-risk issues exist — plaintext SMTP/platform secrets in settings responses, provider client secrets loaded fully into forms, and unsalted MD5 password hashing — but they are broader and cross more modules. The safest first slice is to harden application API key exposure only.

## Goals / Non-Goals

**Goals:**
- Start secret-management hardening with the smallest real leak: application API key display and API responses
- Reuse the existing masking pattern already used for system API keys
- Add focused backend and frontend regression coverage proving list responses are masked and masked values are not treated as raw copyable secrets

**Non-Goals:**
- Changing how API keys are stored at rest in the first slice
- Redesigning all settings forms that currently load full secrets
- Migrating password hashing or secret-source configuration in this change’s first PR

## Decisions

### 1. Start with application API key masking, not broader secret storage redesign

**Why:** the application API key leak is the highest-confidence, lowest-risk issue. The system API key implementation already shows the desired behavior, so we can harden one capability without introducing a new masking model.

**Alternative considered:** begin with SMTP/provider secret redaction. Rejected because those flows involve many forms and update semantics (e.g. “leave blank to keep existing”), which is a larger cross-cutting change.

### 2. Mask only list/read exposure and preserve one-time full-key creation semantics

**Why:** returning the full key once at creation time is operationally useful and already matches system API key behavior. The harmful part is subsequent read/list echoing of the stored secret.

**Alternative considered:** mask create responses too. Rejected because it changes operator workflow more aggressively and is not necessary to close the standing exposure gap.

### 3. Pair backend masking with a small frontend guard for masked keys

**Why:** once the backend returns masked values, the application API key dialog should recognize those values as masked and avoid presenting them as raw secrets that can be copied or treated as full credentials.

**Alternative considered:** backend-only fix. Rejected because the frontend currently assumes every listed value is a full secret and would present a misleading copy action.

## Risks / Trade-offs

- **[Risk] Existing consumers may rely on list endpoints returning full application API keys** → **Mitigation:** keep create/generate responses unchanged and limit masking to list/read serializers
- **[Risk] Frontend copy behavior may still expose masked values as if they were usable** → **Mitigation:** add a simple masked-value check mirroring the existing system API key dialog behavior
- **[Risk] Broader secret leaks remain after this slice** → **Mitigation:** explicitly sequence email/provider/platform secret redaction as follow-up slices rather than implying this change solves all secret-hardening problems

## Migration Plan

1. Add backend tests for masked application API key list responses while preserving create-time full secret return
2. Add the backend serializer masking change
3. Update the frontend application API key dialog to treat masked secrets as masked display values, not raw copyable keys
4. Run the focused backend/frontend verification for the application API key flow

## Open Questions

- Should the next slice target email/password-like settings redaction or platform/provider secret redaction first?
- Do application API keys need partial reveal/copy-last-created UX later, or is one-time create response enough for community edition?
