## MODIFIED Requirements

### Requirement: Chat users and chat user groups are managed explicitly
The system SHALL provide community-edition management for chat users and chat user groups, including lifecycle, source tracking, and group assignment behavior.

#### Scenario: create chat user rejects duplicate username
- **WHEN** an authorized actor attempts to create a chat user with a username that already exists
- **THEN** the system rejects the request with an error indicating the username is already taken

#### Scenario: create chat user rejects duplicate nick name
- **WHEN** an authorized actor attempts to create a chat user with a nick name that already exists
- **THEN** the system rejects the request with an error indicating the nick name is already taken

#### Scenario: create chat user rejects weak password
- **WHEN** an authorized actor attempts to create a chat user with a password that does not meet the supported complexity requirements
- **THEN** the system rejects the request with an error indicating the password policy
