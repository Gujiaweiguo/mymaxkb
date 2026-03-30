## Purpose

Define how supported resources are shared across workspaces in community edition and how authorized workspaces consume those shared resources.

## Requirements

### Requirement: Shared resources can be exposed across authorized workspaces
The system SHALL define how supported resources are shared across workspaces in community edition and how authorized workspaces consume those shared resources.

#### Scenario: resource is shared to an authorized workspace set
- **WHEN** an authorized actor configures a supported resource for cross-workspace sharing
- **THEN** the system records the authorized workspace scope for that shared resource

#### Scenario: authorized workspace consumes shared resource
- **WHEN** a workspace is within the authorized scope of a shared resource
- **THEN** the system permits that workspace to view or consume the resource according to the defined sharing rules

#### Scenario: unauthorized workspace is denied shared resource access
- **WHEN** a workspace is outside the authorized scope of a shared resource
- **THEN** the system denies access to that shared resource

#### Scenario: administrator reads default shared authorization state
- **WHEN** an authorized administrator requests shared authorization for a supported resource without an existing configuration
- **THEN** the system returns the default shared authorization state

#### Scenario: administrator configures shared authorization for a tool resource
- **WHEN** an authorized administrator configures a tool resource for cross-workspace sharing
- **THEN** the system records the authorized workspace scope for that tool resource

#### Scenario: administrator updates existing shared authorization
- **WHEN** an authorized administrator submits a new shared authorization configuration for a resource that already has one
- **THEN** the system updates the stored authorization state for that resource

#### Scenario: administrator configures shared authorization for a knowledge resource
- **WHEN** an authorized administrator configures a knowledge resource for cross-workspace sharing
- **THEN** the system records the authorized workspace scope for that knowledge resource

#### Scenario: authorized actor pages resource relationships
- **WHEN** an authorized actor requests resource relationships for a resource through the mapping endpoint
- **THEN** the system returns a paginated list of matching resource relationships

#### Scenario: unauthorized actor is denied resource relationship access
- **WHEN** an actor without sufficient permission requests resource relationships for a resource
- **THEN** the system rejects the request with forbidden access

#### Scenario: resource relationship page can be empty
- **WHEN** an authorized actor requests resource relationships for a resource with no stored mappings
- **THEN** the system returns an empty paginated result
