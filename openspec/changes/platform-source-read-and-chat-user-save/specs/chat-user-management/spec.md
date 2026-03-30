## MODIFIED Requirements

### Requirement: Chat users and chat user groups are managed explicitly
The system SHALL provide community-edition management for chat users and chat user groups, including lifecycle, source tracking, and group assignment behavior.

#### Scenario: administrator lists configured chat-user platform sources
- **WHEN** an authorized administrator requests the chat-user platform source configuration list
- **THEN** the system returns the supported chat-user platform source entries and their current configuration state

#### Scenario: administrator saves chat-user platform source configuration
- **WHEN** an authorized administrator saves a chat-user platform source configuration for a supported external platform
- **THEN** the system persists that chat-user platform source configuration for later synchronization and administration
