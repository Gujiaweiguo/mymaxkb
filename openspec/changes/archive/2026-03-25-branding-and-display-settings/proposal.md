## Why

The X-Pack documents separate visual branding and application display controls from security and resource management, and this repository already includes system theme settings plus application display-related permissions. Planning these as a dedicated change keeps visual customization shippable without entangling it with authentication, workspace, or connector work.

## What Changes

- Define community-edition requirements for system branding and appearance settings.
- Define community-edition requirements for per-application display settings, including visible chat presentation controls.
- Define how branding assets and display preferences are managed without changing access-control semantics.
- Establish a clear boundary between visual customization and security-sensitive application access restrictions.

## Capabilities

### New Capabilities
- `system-branding-settings`: Define configurable system appearance behavior, including theme, logos, login-page presentation, and site-level branding settings.
- `app-display-settings`: Define configurable application-facing display behavior, including chat presentation, avatars, entry icon behavior, history visibility, and disclaimer-style presentation controls.

### Modified Capabilities
- None.

## Impact

- Affected existing system appearance surfaces in `ui/src/views/system-setting/theme/**/*` and the related API client `ui/src/api/system-settings/theme.ts`.
- Affected application permission surfaces that already expose display-related permissions in `ui/src/utils/permission/data.ts`.
- Likely affects backend system-setting persistence under `apps/system_manage/models/system_setting.py` and any application-level setting serializers that currently store display configuration.
- Remains intentionally separate from app access restriction, chat-user authorization, and login authentication changes.
