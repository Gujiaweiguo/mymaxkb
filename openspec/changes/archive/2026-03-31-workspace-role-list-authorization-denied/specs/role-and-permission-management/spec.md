## MODIFIED Requirements

### Requirement: Administrative roles and permissions are centrally managed
The system SHALL define and manage administrative roles and permissions for community edition, including built-in role behavior and custom permission assignment boundaries.

#### Scenario: non-admin actor cannot list workspace roles
- **WHEN** a non-admin actor requests the workspace role list endpoint
- **THEN** the system rejects the request with forbidden access
