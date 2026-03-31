## Why

System API key coverage already proved the view-layer create and page flow, but there was still no serializer-level contract test proving that generation returns the full secret exactly once while list/page responses return the masked representation without mutating the stored value.

## What Changes

- Add serializer-level masking contract coverage for system API key generation and paging
- Sync the secret-management-hardening capability so persisted system API keys are explicitly covered by the read-path redaction requirement
- Keep scope test-only; no production code changes

## Capabilities

### Modified Capabilities

- `secret-management-hardening`: verify persisted system API keys are redacted in read paths after creation

## Impact

- Extends `apps/system_manage/test_system_api_key.py`
- Completes parity with the existing application API key masking contract tests
