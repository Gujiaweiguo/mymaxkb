## ADDED Requirements

### Requirement: local model provider calls SHALL fail gracefully
The system SHALL return controlled, standardized errors when local_model provider endpoints are unreachable, without terminating the web process.

#### Scenario: local_model endpoint unreachable
- **WHEN** local_model provider request times out or connection is refused
- **THEN** API returns controlled error response and web process remains healthy

### Requirement: provider availability SHALL be signaled in UI
The system SHALL display explicit availability hints for providers that depend on local/external model services.

#### Scenario: local capability unavailable
- **WHEN** local model capability is disabled or unreachable
- **THEN** model management UI shows clear non-blocking availability warning

#### Scenario: local capability available
- **WHEN** local model capability is enabled and reachable
- **THEN** UI shows normal available state for local providers

### Requirement: Ollama provider behavior SHALL remain backward compatible
The system SHALL preserve existing Ollama provider API-base behavior and validation semantics during this change.

#### Scenario: Ollama provider listed and usable
- **WHEN** provider list and credential validation flows execute
- **THEN** `model_ollama_provider` remains available with unchanged behavior
