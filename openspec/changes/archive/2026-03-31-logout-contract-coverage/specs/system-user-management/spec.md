## MODIFIED Requirements

### Requirement: Administrative user lifecycle is managed explicitly
The system SHALL provide explicit administrative user lifecycle management for community edition, including creation, update, status control, search, and credential-maintenance operations.

#### Scenario: authenticated actor logs out and invalidates the current token
- **WHEN** an authenticated actor requests the logout endpoint with a valid bearer token
- **THEN** the system returns success
- **AND** the current token is invalidated for subsequent authenticated use
