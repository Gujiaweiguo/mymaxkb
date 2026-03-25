## MODIFIED Requirements

### Requirement: Ready WeCom application integration exposes executable callback behavior
The system SHALL define how a ready WeCom application integration uses its saved callback configuration in community edition.

#### Scenario: configured WeCom application exposes callback metadata
- **WHEN** an authorized administrator configures WeCom access for an application
- **THEN** the system exposes the callback information required to finish external WeCom setup

#### Scenario: inactive or unready WeCom application integration cannot be treated as active runtime access
- **WHEN** the WeCom application configuration is incomplete, disabled, or not ready
- **THEN** the system does not treat the integration as available for active callback-driven use

#### Scenario: ready WeCom callback runtime hands off supported message payloads to the message loop
- **WHEN** a ready WeCom application callback receives a supported runtime payload after callback verification succeeds
- **THEN** the downstream conversation behavior is governed by the WeCom channel message-loop contract rather than the authentication setup contract alone
