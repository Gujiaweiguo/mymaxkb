## MODIFIED Requirements

### Requirement: Resource management and authorization follow workspace-aware boundaries
The system SHALL define resource management visibility and authorization behavior for supported workspace-scoped resources in community edition.

#### Scenario: non-privileged actor is denied user-resource authorization writes
- **WHEN** a non-privileged actor attempts to modify user-resource authorization data through administrative workspace resource-authorization PUT endpoints
- **THEN** the system denies the request with a forbidden response

#### Scenario: non-privileged actor is denied resource-user authorization writes
- **WHEN** a non-privileged actor attempts to modify resource-user authorization data through administrative workspace resource-authorization PUT endpoints
- **THEN** the system denies the request with a forbidden response
