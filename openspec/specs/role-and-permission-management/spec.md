## ADDED Requirements

### Requirement: Administrative roles and permissions are centrally managed
The system SHALL define and manage administrative roles and permissions for community edition, including built-in role behavior and custom permission assignment boundaries.

#### Scenario: built-in administrative role is assigned
- **WHEN** an authorized administrator assigns a built-in administrative role to a system user
- **THEN** the system grants the permissions associated with that built-in role
- **AND** the assignment is reflected consistently in permission-gated administrative surfaces

#### Scenario: custom role is configured within supported boundaries
- **WHEN** an authorized administrator creates or edits a custom role
- **THEN** the system stores the configured permission set within the supported role model
- **AND** users assigned to that role receive the configured permission behavior

#### Scenario: unauthorized actor attempts role mutation
- **WHEN** an actor without sufficient permission attempts to create, edit, or assign an administrative role
- **THEN** the system denies the operation

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

#### Scenario: non-admin actor cannot list workspace roles
- **WHEN** a non-admin actor requests the workspace role list endpoint
- **THEN** the system rejects the request with forbidden access

#### Scenario: public actor reads login auth settings
- **WHEN** an unauthenticated actor requests the public login-auth settings endpoint
- **THEN** the system returns the current public login-auth configuration

#### Scenario: public login auth settings have deterministic defaults
- **WHEN** no login-auth setting has been persisted
- **THEN** the public login-auth settings endpoint returns the built-in CE default configuration
