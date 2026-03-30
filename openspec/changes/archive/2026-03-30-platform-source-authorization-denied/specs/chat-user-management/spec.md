## MODIFIED Requirements

### Requirement: Chat users and chat user groups are managed explicitly
The system SHALL provide community-edition management for chat users and chat user groups, including lifecycle, source tracking, and group assignment behavior.

#### Scenario: non-admin actor cannot manage chat-user platform sources
- **WHEN** a non-admin actor requests chat-user platform source list, save, or validate operations
- **THEN** the system rejects the request with forbidden access
