## MODIFIED Requirements

### Requirement: System login authentication supports configured administrative sign-in methods
The system SHALL support configurable administrative login authentication for community edition.

#### Scenario: non-admin actor cannot manage platform login sources
- **WHEN** a non-admin actor requests platform source list, save, or validate operations for administrative login integrations
- **THEN** the system rejects the request with forbidden access
