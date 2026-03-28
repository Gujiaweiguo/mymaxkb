## ADDED Requirements

### Requirement: Chat-user access to applications and datasets is policy controlled
The system SHALL define chat-user and chat-user-group access control for supported applications and datasets, including application access restriction behavior.

#### Scenario: authorized chat user accesses a protected application or dataset
- **WHEN** a chat user or chat user group satisfies the configured access policy for a protected application or dataset
- **THEN** the system permits access through the defined protected path

#### Scenario: unauthorized chat user is denied protected access
- **WHEN** a chat user or chat user group does not satisfy the configured access policy for a protected application or dataset
- **THEN** the system denies access

#### Scenario: application requires password or authenticated chat-user access
- **WHEN** an application is configured to require password-based or authenticated access restriction
- **THEN** the system enforces that access restriction before granting application access
