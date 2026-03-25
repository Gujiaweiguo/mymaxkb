## ADDED Requirements

### Requirement: Supported DingTalk callback events drive bounded application conversation state
The system SHALL define a bounded DingTalk channel message loop in community edition based on explicitly supported callback payload classes.

#### Scenario: supported DingTalk org-add event creates chat shells for all delivered users
- **WHEN** a ready DingTalk application callback receives a supported `user_add_org` event with one or more user identifiers
- **THEN** the system creates one channel chat shell per delivered user for that application

#### Scenario: repeated supported DingTalk org-add event does not duplicate chat shells
- **WHEN** the same supported DingTalk org-add event is delivered again with the same event identifier
- **THEN** the system does not create duplicate channel chat shells for that repeated event

#### Scenario: unsupported DingTalk callback event is acknowledged without conversation side effects
- **WHEN** a ready DingTalk application callback receives an event type that is not explicitly supported by the CE message loop
- **THEN** the system does not treat that event as conversation input

### Requirement: DingTalk message-loop expansion is gated by confirmed supported message payloads
The system SHALL only reuse the CE conversation and answer-generation path for DingTalk payloads that are explicitly confirmed as supported for message-loop behavior.

#### Scenario: unsupported or unconfirmed DingTalk message payload does not claim answer-generation behavior
- **WHEN** a DingTalk callback payload has not been explicitly defined as a supported message-loop input
- **THEN** the system does not treat that payload as a message-to-answer conversation step

#### Scenario: confirmed supported DingTalk message payload reuses CE conversation handling
- **WHEN** a DingTalk callback payload class is explicitly defined as supported for conversation input
- **THEN** the system reuses the existing CE chat session, persistence, and answer-generation path for that payload class

### Requirement: DingTalk transport validation remains a prerequisite to any routed message-loop behavior
The system SHALL require successful DingTalk callback verification before any routed conversation side effect is applied.

#### Scenario: invalid DingTalk callback transport does not create conversation state
- **WHEN** a DingTalk callback fails required signature, decryptability, or owner-key validation
- **THEN** the system does not persist conversation state for that callback
