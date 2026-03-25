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
