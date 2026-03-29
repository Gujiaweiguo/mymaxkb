## MODIFIED Requirements

### Requirement: Resource management and authorization follow workspace-aware boundaries
The system SHALL define resource management visibility and authorization behavior for supported workspace-scoped resources in community edition.

#### Scenario: authorized actor views managed resources within allowed scope
- **WHEN** an actor has sufficient authority to view managed resources for a workspace or administrative scope
- **THEN** the system returns the resources visible within that authorized scope

#### Scenario: authorized actor grants or updates supported resource access
- **WHEN** an actor with sufficient authority modifies supported resource authorization within the defined model
- **THEN** the system persists the grant or update according to workspace-aware authorization rules

#### Scenario: actor without sufficient authority attempts resource management
- **WHEN** an actor lacks the authority required for a resource-management or resource-authorization action
- **THEN** the system denies the action

#### Scenario: CE USER actor denied application management without resource grant
- **WHEN** a CE USER actor without explicit application resource permission attempts application CRUD operations on a workspace
- **THEN** the system returns 403 for each denied operation

#### Scenario: CE USER actor denied knowledge management without resource grant
- **WHEN** a CE USER actor without explicit knowledge resource permission attempts knowledge CRUD operations on a workspace
- **THEN** the system returns 403 for each denied operation

#### Scenario: CE USER actor denied model management without resource grant
- **WHEN** a CE USER actor without explicit model resource permission attempts model CRUD operations on a workspace
- **THEN** the system returns 403 for each denied operation

#### Scenario: CE USER actor denied tool management without resource grant
- **WHEN** a CE USER actor without explicit tool resource permission attempts tool CRUD operations on a workspace
- **THEN** the system returns 403 for each denied operation

#### Scenario: CE USER actor denied trigger management without resource grant
- **WHEN** a CE USER actor without explicit trigger resource permission attempts trigger CRUD operations on a workspace
- **THEN** the system returns 403 for each denied operation

#### Scenario: CE USER actor with resource VIEW grant can list and read but not write
- **WHEN** a CE USER actor has a WorkspaceUserResourcePermission VIEW grant for a resource type in a workspace
- **THEN** the system allows list and read operations on that resource type within the workspace
- **AND** the system denies create, update, and delete operations on that resource type

#### Scenario: CE USER actor with resource MANAGE grant can perform all CRUD operations
- **WHEN** a CE USER actor has a WorkspaceUserResourcePermission MANAGE grant for a resource type in a workspace
- **THEN** the system allows all CRUD operations on that resource type within the workspace
