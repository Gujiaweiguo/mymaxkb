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
