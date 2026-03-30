## MODIFIED Requirements

### Requirement: Administrative user lifecycle is managed explicitly
The system SHALL provide explicit administrative user lifecycle management for community edition, including creation, update, status control, search, and credential-maintenance operations.

#### Scenario: non-admin actor cannot manage system API keys
- **WHEN** a non-admin actor requests create, page, edit, or delete operations for system API keys
- **THEN** the system rejects the request with forbidden access
