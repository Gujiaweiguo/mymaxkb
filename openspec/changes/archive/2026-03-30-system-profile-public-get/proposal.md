## Why

`GET /profile` is the only `system_manage` endpoint that still has no meaningful automated coverage. The current smoke test only checks status code 200 and does not verify the shape or semantics of the returned system profile payload.

## What Changes

- Add public GET coverage for `/profile`
- Verify the response shape matches the serializer contract
- Keep scope test-only; no production code changes

## Capabilities

### New Capabilities

- `system-profile`: public system profile information is exposed through a stable read-only API

## Impact

- New small test module under `apps/system_manage/`
- New main OpenSpec capability for system profile exposure
