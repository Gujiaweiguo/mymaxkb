## MODIFIED Requirements

### Requirement: Workspace lifecycle and authority model are defined for community edition
The system SHALL define workspace lifecycle, membership, ownership, and administrative authority behavior for community edition.

#### Scenario: authorized administrator creates a workspace
- **WHEN** an authorized actor creates a workspace with valid workspace information
- **THEN** the system creates the workspace within the community-edition workspace model
- **AND** the workspace is available for subsequent membership and resource-scoping operations

#### Scenario: workspace cannot be removed while constrained resources remain
- **WHEN** an authorized actor attempts to delete a workspace that still violates defined deletion constraints
- **THEN** the system denies deletion
- **AND** the response indicates that the workspace is not yet eligible for removal

#### Scenario: workspace authority is enforced on membership actions
- **WHEN** an actor without sufficient workspace authority attempts to manage workspace membership
- **THEN** the system denies the membership-management operation

#### Scenario: workspace deletion blocked by application resources
- **WHEN** a workspace contains applications or application folders
- **THEN** the system reports the workspace as not deletable

#### Scenario: workspace deletion blocked by knowledge resources
- **WHEN** a workspace contains knowledge bases, knowledge folders, or knowledge workflows
- **THEN** the system reports the workspace as not deletable

#### Scenario: workspace deletion blocked by tool resources
- **WHEN** a workspace contains tools or tool folders
- **THEN** the system reports the workspace as not deletable

#### Scenario: workspace deletion blocked by model resources
- **WHEN** a workspace contains models
- **THEN** the system reports the workspace as not deletable

#### Scenario: workspace deletion blocked by trigger resources
- **WHEN** a workspace contains triggers
- **THEN** the system reports the workspace as not deletable

#### Scenario: workspace deletion blocked by resource permissions
- **WHEN** a workspace contains workspace user resource permissions
- **THEN** the system reports the workspace as not deletable

#### Scenario: workspace deletion succeeds when all constraints are clear
- **WHEN** a workspace has no constrained resources
- **THEN** the system reports the workspace as deletable and the deletion succeeds

#### Scenario: default workspace rejects member management
- **WHEN** an administrator attempts to add, list, or remove members on the default workspace
- **THEN** the system rejects the operation with an error

#### Scenario: workspace name must be unique on creation
- **WHEN** an administrator creates a workspace with a name that already exists
- **THEN** the system rejects the creation

#### Scenario: workspace name must be unique on update
- **WHEN** an administrator updates a workspace name to one that already exists on a different workspace
- **THEN** the system rejects the update

#### Scenario: workspace update via POST with id field
- **WHEN** an administrator POSTs to the workspace endpoint with an existing workspace id and a new name
- **THEN** the system updates the workspace name
