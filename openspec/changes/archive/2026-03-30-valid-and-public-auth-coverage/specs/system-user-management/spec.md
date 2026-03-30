## MODIFIED Requirements

### Requirement: Administrative user lifecycle is managed explicitly
The system SHALL provide explicit administrative user lifecycle management for community edition, including creation, update, status control, search, and credential-maintenance operations.

#### Scenario: authenticated actor checks CE validation allowance
- **WHEN** an authenticated actor requests the supported validation endpoint with a count that remains within the CE allowance
- **THEN** the system reports that the requested action is valid
