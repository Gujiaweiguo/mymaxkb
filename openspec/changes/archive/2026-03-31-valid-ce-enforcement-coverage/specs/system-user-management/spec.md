## MODIFIED Requirements

### Requirement: Administrative user lifecycle is managed explicitly
The system SHALL provide explicit administrative user lifecycle management for community edition, including creation, update, status control, search, and credential-maintenance operations.

#### Scenario: authenticated actor is rejected for non-matching CE validation count
- **WHEN** an authenticated actor requests the CE validation endpoint with a count that does not match the supported application allowance
- **THEN** the system reports a CE validation failure

#### Scenario: authenticated actor is rejected when CE application quota is exhausted
- **WHEN** an authenticated actor requests the CE validation endpoint with the supported application allowance after the quota has been reached
- **THEN** the system reports a CE validation failure

#### Scenario: valid license bypasses CE validation enforcement
- **WHEN** a request reaches the validation endpoint while a valid license is present
- **THEN** the system reports the requested action as valid without applying the CE application-count limit
