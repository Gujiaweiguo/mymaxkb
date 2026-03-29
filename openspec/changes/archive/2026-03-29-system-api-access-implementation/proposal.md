## Why

System API access is already largely implemented: managed system API keys exist, the backend authenticates `system-` tokens, and the frontend exposes full CRUD through the avatar API-key dialog. The main missing runtime seam is that cross-domain controls stored on system API keys are not enforced by the existing middleware, so part of the privileged credential model is currently configuration-only.

## What Changes

- define the implementation change for system API access around the currently missing runtime enforcement seams rather than rebuilding existing API-key CRUD
- add a minimal first slice that enforces system API key cross-domain rules in middleware and verifies allowed versus denied origin behavior
- sequence follow-up slices for broader endpoint authorization scope and any dedicated system API key page if that becomes necessary

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `system-api-access`: complete the managed system API credential model by enforcing configured cross-domain behavior for valid system API keys

## Impact

- Backend cross-domain enforcement in `apps/common/middleware/cross_domain_middleware.py`
- Existing system API key model, serializer, auth handler, and tests in `apps/system_manage/models/system_api_key.py`, `apps/system_manage/serializers/system_api_key.py`, `apps/common/auth/handle/impl/system_api_key.py`, and `apps/system_manage/test_system_api_key.py`
- Existing frontend system API key dialog remains in place for the first slice and should not require UI changes
