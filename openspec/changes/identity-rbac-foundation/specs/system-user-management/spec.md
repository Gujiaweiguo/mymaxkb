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
