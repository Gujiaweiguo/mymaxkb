## MODIFIED Requirements

### Requirement: System login authentication supports configured administrative sign-in methods
The system SHALL provide configurable administrative login authentication for community edition and enforce supported sign-in methods consistently at the admin entry point.

#### Scenario: administrator reads default login auth settings
- **WHEN** an authorized administrator requests login auth settings before any configuration has been saved
- **THEN** the system returns the normalized default login auth configuration

#### Scenario: administrator reads persisted login auth settings
- **WHEN** an authorized administrator requests login auth settings after configuration has been saved
- **THEN** the system returns the persisted login auth configuration with normalized response fields

#### Scenario: administrator updates login auth settings
- **WHEN** an authorized administrator submits login auth settings through the admin endpoint
- **THEN** the system persists the normalized configuration and returns the normalized response payload
