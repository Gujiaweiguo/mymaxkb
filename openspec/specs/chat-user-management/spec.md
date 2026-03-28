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
