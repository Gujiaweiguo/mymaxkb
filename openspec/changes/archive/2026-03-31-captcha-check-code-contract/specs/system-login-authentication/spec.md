## MODIFIED Requirements

### Requirement: System login authentication supports configured administrative sign-in methods
The system SHALL provide configurable administrative login authentication for community edition and enforce supported sign-in methods consistently at the admin entry point.

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
