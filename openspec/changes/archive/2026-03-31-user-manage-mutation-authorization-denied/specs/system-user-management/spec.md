## MODIFIED Requirements

### Requirement: Administrative user lifecycle is managed explicitly
The system SHALL provide explicit administrative user lifecycle management for community edition, including creation, update, status control, search, and credential-maintenance operations.

#### Scenario: non-admin actor cannot mutate user-management endpoints
- **WHEN** a non-admin authenticated actor requests create, update, delete, batch-delete, or password-reset operations on the user-management surface
- **THEN** the system rejects each request with forbidden access
