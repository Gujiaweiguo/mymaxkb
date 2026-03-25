## ADDED Requirements

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
