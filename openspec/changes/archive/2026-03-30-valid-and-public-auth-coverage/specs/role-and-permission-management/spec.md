## MODIFIED Requirements

### Requirement: Authorization is enforced for role and permission management operations
The system SHALL enforce authorization on role and permission management operations.

#### Scenario: public actor reads login auth settings
- **WHEN** an unauthenticated actor requests the public login-auth settings endpoint
- **THEN** the system returns the current public login-auth configuration

#### Scenario: public login auth settings have deterministic defaults
- **WHEN** no login-auth setting has been persisted
- **THEN** the public login-auth settings endpoint returns the built-in CE default configuration
