## MODIFIED Requirements

### Requirement: System login authentication supports configured administrative sign-in methods
The system SHALL provide configurable administrative login authentication for community edition and enforce supported sign-in methods consistently at the admin entry point.

#### Scenario: authenticated actor reads the current profile contract
- **WHEN** an authenticated actor requests the current-profile endpoint
- **THEN** the system returns the actor identity, source, language, role, permissions, and workspace membership fields for that actor

#### Scenario: local authenticated actor sees the password-change flag when required
- **WHEN** a local authenticated actor with a required password change requests the current-profile endpoint
- **THEN** the system marks the profile as requiring password edit
