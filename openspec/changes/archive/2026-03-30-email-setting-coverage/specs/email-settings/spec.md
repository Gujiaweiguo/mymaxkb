## ADDED Requirements

### Requirement: Email settings are managed explicitly through the admin API
The system SHALL allow authorized administrators to read, update, and validate community-edition email settings through the administrative API.

#### Scenario: administrator reads default email settings state
- **WHEN** an authorized administrator requests email settings before any configuration has been saved
- **THEN** the system returns an empty email-settings state

#### Scenario: administrator creates or updates email settings
- **WHEN** an authorized administrator submits valid email configuration through the email settings endpoint
- **THEN** the system persists that configuration for future reads and updates

#### Scenario: administrator validates email settings successfully
- **WHEN** an authorized administrator requests email-settings validation with valid SMTP configuration
- **THEN** the system reports success

#### Scenario: non-admin actor cannot manage email settings
- **WHEN** a non-admin actor requests email-settings read, update, or validation operations
- **THEN** the system rejects the request with forbidden access
