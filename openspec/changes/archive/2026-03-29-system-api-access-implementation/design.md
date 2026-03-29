## Context

The repository already has a substantial system API access implementation. Community-edition code includes a `SystemApiKey` model, CRUD views and serializers, an auth handler that accepts `system-` bearer tokens, and frontend management UI through the avatar API-key dialog. Tests already cover key creation, update, deletion, expiry, inactivity, and one successful authenticated access path through the system profile endpoint.

The clearest missing runtime seam is cross-domain enforcement. `SystemApiKey` stores `allow_cross_domain` and `cross_domain_list`, and the edit drawer exposes those fields, but `CrossDomainMiddleware` only checks `application-` and `agent-` token prefixes. For system API keys, the cross-domain settings are effectively dead configuration today.

## Goals / Non-Goals

**Goals:**
- Start with the smallest runtime gap in system API access: cross-domain enforcement for system API keys
- Reuse the existing system API key fields and middleware pattern rather than introducing a new access model
- Add focused backend tests proving allowed and denied origin behavior for `system-` tokens

**Non-Goals:**
- Rebuilding the existing system API key frontend dialog or adding a dedicated page in the first slice
- Expanding system API keys to broad new endpoint permissions in the first slice
- Redesigning the auth handler to add scopes or per-key permission matrices yet

## Decisions

### 1. Start with middleware enforcement, not CRUD or UI changes

**Why:** the CRUD model and UI already exist. The smallest missing contract is runtime enforcement of `allow_cross_domain` and `cross_domain_list` for `system-` tokens.

**Alternative considered:** add a standalone `/system/api-key` page first. Rejected because that is a UX enhancement, not the primary missing behavior in the credential model.

### 2. Reuse the existing prefix-based branch in `CrossDomainMiddleware`

**Why:** the middleware already branches on bearer-token prefixes for `application-` and `agent-`. Extending that logic to `system-` keys is the smallest consistent implementation path.

**Alternative considered:** move cross-domain enforcement into the auth handler. Rejected because cross-domain response headers are currently managed centrally in middleware, and splitting enforcement paths would increase complexity.

### 3. Keep first-slice tests in `test_system_api_key.py`

**Why:** system API key tests already live there and cover lifecycle and auth acceptance. Adding cross-domain regression tests in the same module keeps the capability contract in one place.

**Alternative considered:** create a new middleware-specific test module. Rejected for the first slice because the behavior is tightly coupled to system API key semantics already covered in the existing test file.

## Risks / Trade-offs

- **[Risk] Middleware behavior may differ between real browser preflight and test requests** → **Mitigation:** start with focused response-header tests against representative requests rather than over-modeling full browser behavior
- **[Risk] Existing application/agent cross-domain behavior could be affected by shared middleware edits** → **Mitigation:** keep the change as a prefix-specific branch for `system-` tokens only and rerun existing system API key tests
- **[Risk] Cross-domain settings may still not matter if system API keys remain usable on too few endpoints** → **Mitigation:** treat broader endpoint authorization as a later slice after runtime policy enforcement is correct

## Migration Plan

1. Add backend tests for allowed and denied cross-domain behavior on `system-` API keys
2. Extend `CrossDomainMiddleware` to recognize `system-` tokens and apply the existing cross-domain config model
3. Run the focused system API key tests
4. Evaluate whether a follow-up slice should broaden endpoint authorization or improve UI discoverability

## Open Questions

- Should the next slice after cross-domain enforcement broaden system API key permissions beyond the current profile endpoint model?
- Is a dedicated system API key route/page worth doing later, or is the existing avatar dialog sufficient for community edition?
