## MODIFIED Requirements

### Requirement: Ready DingTalk application integration exposes executable callback behavior
The system SHALL define how a ready DingTalk application integration uses its saved callback configuration in community edition.

#### Scenario: configured DingTalk application exposes callback metadata
- **WHEN** an authorized administrator configures DingTalk access for an application
- **THEN** the system exposes the callback information required to finish external DingTalk setup

#### Scenario: inactive or unready DingTalk application integration cannot be treated as active runtime access
- **WHEN** the DingTalk application configuration is incomplete, disabled, or not ready
- **THEN** the system does not treat the integration as available for active callback-driven use

#### Scenario: ready DingTalk callback runtime hands off supported payloads to the message loop boundary
- **WHEN** a ready DingTalk application callback receives a verified payload class that is explicitly supported for channel runtime behavior
- **THEN** the downstream conversation behavior is governed by the DingTalk channel message-loop contract rather than the authentication setup contract alone
