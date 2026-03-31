## MODIFIED Requirements

### Requirement: Chat users and chat user groups are managed explicitly
The system SHALL provide community-edition management for chat users and chat user groups, including lifecycle, source tracking, and group assignment behavior.

#### Scenario: community edition returns empty chat-user sync types
- **WHEN** an authorized administrator requests the chat-user sync-types endpoint in community edition
- **THEN** the system returns a successful response with an empty list of available sync types
