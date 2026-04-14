## ADDED Requirements

### Requirement: System login authentication supports configured administrative sign-in methods
The system SHALL provide configurable administrative login authentication for community edition and enforce supported sign-in methods consistently at the admin entry point.

#### Scenario: enabled authentication method is used for admin login
- **WHEN** an administrative login method is enabled and correctly configured
- **THEN** the system permits eligible administrative users to authenticate through that method

#### Scenario: disabled authentication method is not available
- **WHEN** an administrative login method is disabled or not configured
- **THEN** the system does not present it as an active administrative sign-in path

#### Scenario: unsupported actor fails authentication
- **WHEN** a login attempt does not satisfy the configured authentication requirements
- **THEN** the system denies administrative access

#### Scenario: administrator lists configured platform login sources
- **WHEN** an authorized administrator requests the platform source configuration list for administrative login integrations
- **THEN** the system returns the supported platform source entries and their current configuration state

#### Scenario: non-admin actor cannot manage platform login sources
- **WHEN** a non-admin actor requests platform source list, save, or validate operations for administrative login integrations
- **THEN** the system rejects the request with forbidden access

#### Scenario: administrator reads default login auth settings
- **WHEN** an authorized administrator requests login auth settings before any configuration has been saved
- **THEN** the system returns the normalized default login auth configuration

#### Scenario: administrator reads persisted login auth settings
- **WHEN** an authorized administrator requests login auth settings after configuration has been saved
- **THEN** the system returns the persisted login auth configuration with normalized response fields

#### Scenario: administrator updates login auth settings
- **WHEN** an authorized administrator submits login auth settings through the admin endpoint
- **THEN** the system persists the normalized configuration and returns the normalized response payload

#### Scenario: non-admin actor cannot manage admin login auth settings
- **WHEN** a non-admin actor requests admin login-auth read or update operations
- **THEN** the system rejects the request with forbidden access

#### Scenario: captcha image is generated when the login failure threshold is reached
- **WHEN** a login username reaches the configured captcha threshold
- **THEN** the system returns a base64 captcha image for that username

#### Scenario: captcha image is omitted when the login failure threshold is not reached
- **WHEN** a login username remains below the configured captcha threshold
- **THEN** the system returns an empty captcha payload

#### Scenario: licensed login requires and validates captcha after threshold is reached
- **WHEN** a login username reaches the configured captcha threshold under the licensed login flow
- **THEN** the system rejects login attempts without a captcha
- **AND** the system accepts a correct captcha value for the same username

#### Scenario: verification codes are validated against cached values
- **WHEN** a caller submits an email verification code for a supported operation type
- **THEN** the system accepts the matching cached code
- **AND** the system rejects missing or incorrect codes

#### Scenario: authenticated actor switches language to a supported locale
- **WHEN** an authenticated actor requests the language-switch endpoint with a supported locale
- **THEN** the system persists the new language for that actor

#### Scenario: authenticated actor cannot switch language to an unsupported locale
- **WHEN** an authenticated actor requests the language-switch endpoint with an unsupported locale
- **THEN** the system rejects the request with an error listing the supported locales

### Requirement: Authenticated actor resets the current password successfully
The system SHALL allow an authenticated actor to reset the current password and SHALL clear any password-change-required state for that actor as part of the successful update.

#### Scenario: authenticated actor resets the current password successfully
- **WHEN** an authenticated actor submits a supported new password and matching confirmation to the current-password reset endpoint
- **THEN** the system updates the stored password for that actor
- **AND** the system clears any password-change-required state for that actor
- **AND** the current authentication token is invalidated

#### Scenario: authenticated actor cannot reset the current password with invalid input
- **WHEN** an authenticated actor submits mismatched or unsupported new-password values to the current-password reset endpoint
- **THEN** the system rejects the request with a password validation error

### Requirement: Authenticated actor reads the current profile contract
The system SHALL return the current authenticated profile contract, including whether the authenticated local actor is required to change the current password before normal administrative use continues.

#### Scenario: authenticated actor reads the current profile contract
- **WHEN** an authenticated actor requests the current-profile endpoint
- **THEN** the system returns the actor identity, source, language, role, permissions, and workspace membership fields for that actor
- **AND** the system includes whether password editing is currently required for that actor

### Requirement: Local authenticated actor sees the password-change flag when required
The system SHALL surface the password-change-required state for local authenticated actors and SHALL enforce that flagged actors remain in the password-change flow until the current password is successfully updated.

#### Scenario: local authenticated actor sees the password-change flag when required
- **WHEN** a local authenticated actor with a required password change requests the current-profile endpoint
- **THEN** the system marks the profile as requiring password edit

#### Scenario: local authenticated actor is blocked from normal authenticated APIs while password change is required
- **WHEN** a local authenticated actor with a required password change requests an authenticated API outside the approved password-change flow endpoints
- **THEN** the system rejects the request because password change is required before continuing

#### Scenario: local authenticated actor can complete the password-change flow while blocked
- **WHEN** a local authenticated actor with a required password change requests the current-profile, current-password-reset, logout, or language-switch endpoint during the enforced password-change flow
- **THEN** the system allows the request to proceed according to the endpoint contract
