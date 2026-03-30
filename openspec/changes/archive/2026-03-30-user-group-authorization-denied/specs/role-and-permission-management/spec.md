## MODIFIED Requirements

### Requirement: Authorization is enforced for role and permission management operations
The system SHALL enforce authorization on role and permission management operations.

#### Scenario: non-admin actor cannot list user groups
- **WHEN** a non-admin actor requests the system user group list endpoint
- **THEN** the system rejects the request with forbidden access

#### Scenario: non-admin actor cannot create or update user groups
- **WHEN** a non-admin actor submits a create or update request to the system user group endpoint
- **THEN** the system rejects the request with forbidden access

#### Scenario: non-admin actor cannot delete a user group
- **WHEN** a non-admin actor requests deletion of a system user group
- **THEN** the system rejects the request with forbidden access

#### Scenario: non-admin actor cannot manage user group members
- **WHEN** a non-admin actor requests user group member add, remove, or paged member listing operations
- **THEN** the system rejects each request with forbidden access
