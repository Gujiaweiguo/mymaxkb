## MODIFIED Requirements

### Requirement: Administrative user lifecycle is managed explicitly
The system SHALL provide explicit administrative user lifecycle management for community edition, including creation, update, status control, search, and credential-maintenance operations.

#### Scenario: administrator batch deletes system users
- **WHEN** an authorized administrator submits a non-empty set of system-user IDs to the batch-delete endpoint
- **THEN** the system deletes the targeted users from the administrative user-management surface

#### Scenario: administrator cannot batch delete with an empty user set
- **WHEN** an authorized administrator submits an empty user-ID set to the batch-delete endpoint
- **THEN** the system rejects the request with a user-ID validation error
