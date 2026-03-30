## MODIFIED Requirements

### Requirement: Shared resources can be exposed across authorized workspaces
The system SHALL define how supported resources are shared across workspaces in community edition and how authorized workspaces consume those shared resources.

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
