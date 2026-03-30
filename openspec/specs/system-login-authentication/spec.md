## ADDED Requirements

### Requirement: System login authentication supports configured administrative sign-in methods
The system SHALL provide configurable administrative login authentication for community edition and enforce supported sign-in methods consistently at the admin entry point.

#### Scenario: enabled authentication method is used for admin login
- **WHEN** an administrative login method is enabled and correctly configured
- **THEN** the system permits eligible administrative users to authenticate through that method

#### Scenario: disabled authentication method is not available
- **WHEN** an administrative login method is disabled or not configured
- **THEN** the system does not present it as an active administrative sign-in path

#### Scenario: unsupported actor fails authentication
- **WHEN** a login attempt does not satisfy the configured authentication requirements
- **THEN** the system denies administrative access

#### Scenario: administrator lists configured platform login sources
- **WHEN** an authorized administrator requests the platform source configuration list for administrative login integrations
- **THEN** the system returns the supported platform source entries and their current configuration state

#### Scenario: non-admin actor cannot manage platform login sources
- **WHEN** a non-admin actor requests platform source list, save, or validate operations for administrative login integrations
- **THEN** the system rejects the request with forbidden access

#### Scenario: administrator reads default login auth settings
- **WHEN** an authorized administrator requests login auth settings before any configuration has been saved
- **THEN** the system returns the normalized default login auth configuration

#### Scenario: administrator reads persisted login auth settings
- **WHEN** an authorized administrator requests login auth settings after configuration has been saved
- **THEN** the system returns the persisted login auth configuration with normalized response fields

#### Scenario: administrator updates login auth settings
- **WHEN** an authorized administrator submits login auth settings through the admin endpoint
- **THEN** the system persists the normalized configuration and returns the normalized response payload

#### Scenario: non-admin actor cannot manage admin login auth settings
- **WHEN** a non-admin actor requests admin login-auth read or update operations
- **THEN** the system rejects the request with forbidden access
