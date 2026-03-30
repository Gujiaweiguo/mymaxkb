## Why

Email setting endpoints are only covered by two thin status-code checks today. There is no proof that email settings persist correctly, that updates overwrite existing values, that the test-connection endpoint succeeds when SMTP is reachable, or that non-admin users are forbidden from managing email settings.

## What Changes

- Add focused tests for email-setting GET/PUT/POST behavior
- Verify persistence and overwrite behavior for `SystemSetting(type=EMAIL)`
- Add non-admin denied-path coverage for email-setting management
- Keep scope test-only; no production code changes

## Capabilities

### New Capabilities

- `email-settings`: community-edition email configuration can be read, updated, and validated through the admin API

## Impact

- New test module under `apps/system_manage/`
- New main OpenSpec capability for email settings
