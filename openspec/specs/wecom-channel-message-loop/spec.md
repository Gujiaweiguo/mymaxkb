## Purpose

TBD

## Requirements

### Requirement: Supported WeCom inbound messages drive persisted application conversations
The system SHALL treat supported WeCom callback payloads as application conversation input in community edition.

#### Scenario: supported WeCom text message creates or reuses a chat session
- **WHEN** a ready WeCom application callback receives a supported text message payload for an application
- **THEN** the system reuses the existing channel chat session for that sender when one exists, or creates a new channel chat session when one does not

#### Scenario: supported WeCom text message persists one chat record
- **WHEN** a ready WeCom application callback receives a supported text message payload with conversation content
- **THEN** the system persists that content as one application `ChatRecord` attached to the resolved channel chat session

#### Scenario: supported WeCom enter-agent event creates a chat shell
- **WHEN** a ready WeCom application callback receives the supported `enter_agent` event
- **THEN** the system creates or preserves channel conversation state so later supported messages can attach to that conversation

### Requirement: Supported WeCom message handling is idempotent at the message level
The system SHALL prevent duplicate persisted conversation work for retried WeCom message deliveries.

#### Scenario: duplicate WeCom message identifier does not create duplicate chat records
- **WHEN** the same supported WeCom message is delivered more than once with the same message identifier
- **THEN** the system does not create a duplicate `ChatRecord` for that message

#### Scenario: duplicate completed WeCom message does not rerun answer generation
- **WHEN** a duplicate supported WeCom message is delivered after its existing chat record already has generated answer content
- **THEN** the system does not rerun answer generation for that duplicate delivery

### Requirement: Supported WeCom messages reuse the existing CE answer-generation path
The system SHALL reuse the existing community-edition application answer path for supported WeCom message-loop inputs.

#### Scenario: supported WeCom text message updates the same chat record with generated answer content
- **WHEN** the system accepts a supported WeCom text message into the message loop
- **THEN** it reuses the existing application answer-generation path and writes the generated answer back into the same `ChatRecord`

#### Scenario: WeCom message metadata survives answer generation
- **WHEN** the system reuses the existing answer-generation path for a supported WeCom message
- **THEN** the channel metadata needed for idempotency and tracing remains preserved on the persisted conversation record

### Requirement: Unsupported or invalid WeCom callback payloads do not become conversation input
The system SHALL bound the WeCom message loop to explicitly supported payload classes.

#### Scenario: unsupported WeCom payload class is acknowledged without conversation side effects
- **WHEN** a ready WeCom callback receives a payload type that is not explicitly supported by the CE message loop
- **THEN** the system does not treat that payload as conversation input

#### Scenario: invalid WeCom callback payload is rejected without persisted conversation work
- **WHEN** a WeCom callback payload fails required validation for signature, decryptability, or supported message structure
- **THEN** the system does not persist conversation state for that payload
