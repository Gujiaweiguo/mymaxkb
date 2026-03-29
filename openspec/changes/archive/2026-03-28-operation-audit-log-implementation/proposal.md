## Why

Community-edition operation audit logs already exist end-to-end for recording, viewing, filtering, exporting, and retention configuration, but one critical operational gap remains: the configured retention policy is not actually enforced by a cleanup job. We should close that lifecycle gap first instead of rebuilding an already-shipped log UI/API surface.

## What Changes

- define the implementation change for operation audit logs around the missing retention-lifecycle enforcement path
- add a minimal first slice that implements and verifies scheduled cleanup of operation logs using the existing clean-time setting
- sequence follow-up slices for decorator-level regression coverage and any additional audit event expansion after cleanup is stable

## Capabilities

### New Capabilities
- None

### Modified Capabilities
- `operation-audit-log`: complete the existing operation-log lifecycle by enforcing configured retention cleanup for stored administrative operation logs

## Impact

- Backend scheduled job registration in `apps/common/job/__init__.py`
- New backend cleanup job following existing scheduler patterns under `apps/common/job/`
- Existing operation-log model, serializer, and tests in `apps/system_manage/models/log_management.py`, `apps/system_manage/serializers/log_management.py`, and `apps/system_manage/test_log_management.py`
- Existing frontend clean-time configuration UI remains in place and should not need behavioral changes for the first slice
