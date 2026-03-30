## MODIFIED Requirements

### Requirement: Administrative operations are logged and reviewable
The system SHALL record and expose administrative operation logs for community edition, including retention-lifecycle enforcement for stored log records.

#### Scenario: non-admin user is denied access to operation-log management endpoints
- **WHEN** a non-admin user requests the operation-log page, menu options, export, or retention-setting endpoints
- **THEN** the system responds with forbidden access
