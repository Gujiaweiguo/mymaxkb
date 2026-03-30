## MODIFIED Requirements

### Requirement: System login authentication supports configured administrative sign-in methods
The system SHALL provide configurable administrative login authentication for community edition and enforce supported sign-in methods consistently at the admin entry point.

#### Scenario: non-admin actor cannot manage admin login auth settings
- **WHEN** a non-admin actor requests admin login-auth read or update operations
- **THEN** the system rejects the request with forbidden access
