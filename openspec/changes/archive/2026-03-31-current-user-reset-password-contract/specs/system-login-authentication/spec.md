## MODIFIED Requirements

### Requirement: System login authentication supports configured administrative sign-in methods
The system SHALL provide configurable administrative login authentication for community edition and enforce supported sign-in methods consistently at the admin entry point.

#### Scenario: authenticated actor resets the current password successfully
- **WHEN** an authenticated actor submits a supported new password and matching confirmation to the current-password reset endpoint
- **THEN** the system updates the stored password for that actor
- **AND** the current authentication token is invalidated

#### Scenario: authenticated actor cannot reset the current password with invalid input
- **WHEN** an authenticated actor submits mismatched or unsupported new-password values to the current-password reset endpoint
- **THEN** the system rejects the request with a password validation error
