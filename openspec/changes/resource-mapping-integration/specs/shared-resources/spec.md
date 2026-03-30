## MODIFIED Requirements

### Requirement: Shared resources can be exposed across authorized workspaces
The system SHALL define how supported resources are shared across workspaces in community edition and how authorized workspaces consume those shared resources.

#### Scenario: authorized actor pages resource relationships
- **WHEN** an authorized actor requests resource relationships for a resource through the mapping endpoint
- **THEN** the system returns a paginated list of matching resource relationships

#### Scenario: unauthorized actor is denied resource relationship access
- **WHEN** an actor without sufficient permission requests resource relationships for a resource
- **THEN** the system rejects the request with forbidden access

#### Scenario: resource relationship page can be empty
- **WHEN** an authorized actor requests resource relationships for a resource with no stored mappings
- **THEN** the system returns an empty paginated result
