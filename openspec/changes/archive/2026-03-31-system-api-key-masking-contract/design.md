## Context

`SystemApiKeySerializer.generate()` returns `SystemApiKeySerializerModel(system_api_key).data`, which includes the full `secret_key` immediately after creation. `SystemApiKeySerializer.page()` maps results through `SystemApiKeyListSerializerModel`, where `get_secret_key()` masks long keys as `{prefix8}******{suffix4}`. Existing view-level tests only loosely checked that masking happened, leaving the exact serializer contract unpinned.

## Goals / Non-Goals

**Goals:**
- Verify system API key generation returns the full secret once
- Verify page/list responses return the exact masked representation
- Verify masking does not change the stored database secret

**Non-Goals:**
- No changes to the serializer or model implementation
- No expansion into auth/permission flows or cross-domain behavior
- No frontend or API response-shape refactors

## Decisions

1. Add a dedicated `SystemApiKeyMaskingTests` class to mirror the existing `ApplicationApiKeyMaskingTests` pattern.
2. Test the serializer layer directly instead of the view layer to pin the exact generate/page contract without HTTP setup noise.
3. Sync the redaction requirement in `secret-management-hardening` rather than `system-user-management`, because this slice is about persisted secret masking in read paths.

## Risks / Trade-offs

- This slice intentionally leaves the existing view-level system API key tests in place and only adds the stricter serializer contract on top.
