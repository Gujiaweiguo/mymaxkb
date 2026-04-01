## ADDED Requirements

### Requirement: Administrative user lifecycle is managed explicitly
The system SHALL provide explicit administrative user lifecycle management for community edition, including creation, update, status control, search, and credential-maintenance operations.

#### Scenario: administrator creates a system user
- **WHEN** an authorized administrator creates a new administrative user
- **THEN** the system stores the user with the configured identity fields and source information
- **AND** the new user becomes governable through the administrative user-management surface

#### Scenario: administrator disables a system user
- **WHEN** an authorized administrator disables an existing administrative user
- **THEN** the system marks the user as inactive for administrative access
- **AND** the user remains auditable and searchable in management views

#### Scenario: administrator searches users by supported filters
- **WHEN** an authorized administrator filters administrative users by supported attributes such as name, account, source, or status
- **THEN** the system returns user-management results matching the provided filters

#### Scenario: authenticated actor checks CE validation allowance
- **WHEN** an authenticated actor requests the supported application or user validation endpoint with a count that remains within the CE allowance
- **THEN** the system reports that the requested action is valid

#### Scenario: authenticated actor is rejected for non-matching CE validation count
- **WHEN** an authenticated actor requests the CE validation endpoint with a count that does not match the supported application or user allowance
- **THEN** the system reports a CE validation failure

#### Scenario: authenticated actor is rejected when CE application or user quota is exhausted
- **WHEN** an authenticated actor requests the CE validation endpoint with the supported application or user allowance after the quota has been reached
- **THEN** the system reports a CE validation failure

#### Scenario: valid license bypasses CE validation enforcement
- **WHEN** a request reaches the validation endpoint while a valid license is present
- **THEN** the system reports the requested action as valid without applying the CE application-count or user-count limit

#### Scenario: non-admin actor cannot manage system API keys
- **WHEN** a non-admin actor requests create, page, edit, or delete operations for system API keys
- **THEN** the system rejects the request with forbidden access

#### Scenario: non-admin actor cannot mutate user-management endpoints
- **WHEN** a non-admin authenticated actor requests create, update, delete, batch-delete, or password-reset operations on the user-management surface
- **THEN** the system rejects each request with forbidden access

#### Scenario: administrator batch deletes system users
- **WHEN** an authorized administrator submits a non-empty set of system-user IDs to the batch-delete endpoint
- **THEN** the system deletes the targeted users from the administrative user-management surface

#### Scenario: administrator cannot batch delete with an empty user set
- **WHEN** an authorized administrator submits an empty user-ID set to the batch-delete endpoint
- **THEN** the system rejects the request with a user-ID validation error

#### Scenario: authenticated actor logs out and invalidates the current token
- **WHEN** an authenticated actor requests the logout endpoint with a valid bearer token
- **THEN** the system returns success
- **AND** the current token is invalidated for subsequent authenticated use
