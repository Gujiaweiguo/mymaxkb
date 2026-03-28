## MODIFIED Requirements

### Requirement: Workspace lifecycle and authority model are defined for community edition
The system SHALL define workspace lifecycle, membership, ownership, and administrative authority behavior for community edition.

#### Scenario: non-admin actor is denied workspace management operations
- **WHEN** a non-ADMIN actor attempts to list, create, update, delete, or delete-check a workspace through the administrative workspace endpoints
- **THEN** the system denies the request with a forbidden response

#### Scenario: non-admin actor is denied workspace member-management operations
- **WHEN** a non-ADMIN actor attempts to list workspace members or add or remove a workspace member through the administrative workspace endpoints
- **THEN** the system denies the request with a forbidden response
