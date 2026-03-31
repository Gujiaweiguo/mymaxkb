## Purpose

Define community-edition management for chat users and chat user groups, including lifecycle, source tracking, and group assignment behavior.

## Requirements

### Requirement: Chat users and chat user groups are managed explicitly
The system SHALL provide community-edition management for chat users and chat user groups, including lifecycle, source tracking, and group assignment behavior.

#### Scenario: authorized administrator creates a chat user
- **WHEN** an authorized actor creates a chat user with supported identity fields
- **THEN** the system stores the chat user in the managed chat-user directory

#### Scenario: chat user is assigned to one or more groups
- **WHEN** an authorized actor assigns a chat user to supported chat user groups
- **THEN** the system persists the group relationships for downstream authorization use

#### Scenario: synchronized chat-user source is tracked
- **WHEN** a chat user enters the system through a supported external source or synchronization path
- **THEN** the system records the source for later filtering and administration

#### Scenario: create chat user rejects duplicate username
- **WHEN** an authorized actor attempts to create a chat user with a username that already exists
- **THEN** the system rejects the request with an error indicating the username is already taken

#### Scenario: create chat user rejects duplicate nick name
- **WHEN** an authorized actor attempts to create a chat user with a nick name that already exists
- **THEN** the system rejects the request with an error indicating the nick name is already taken

#### Scenario: create chat user rejects weak password
- **WHEN** an authorized actor attempts to create a chat user with a password that does not meet the supported complexity requirements
- **THEN** the system rejects the request with an error indicating the password policy

#### Scenario: administrator lists configured chat-user platform sources
- **WHEN** an authorized administrator requests the chat-user platform source configuration list
- **THEN** the system returns the supported chat-user platform source entries and their current configuration state

#### Scenario: administrator saves chat-user platform source configuration
- **WHEN** an authorized administrator saves a chat-user platform source configuration for a supported external platform
- **THEN** the system persists that chat-user platform source configuration for later synchronization and administration

#### Scenario: non-admin actor cannot manage chat-user platform sources
- **WHEN** a non-admin actor requests chat-user platform source list, save, or validate operations
- **THEN** the system rejects the request with forbidden access

#### Scenario: community edition returns empty chat-user sync types
- **WHEN** an authorized administrator requests the chat-user sync-types endpoint in community edition
- **THEN** the system returns a successful response with an empty list of available sync types
