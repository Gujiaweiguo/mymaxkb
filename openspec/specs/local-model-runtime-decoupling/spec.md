# local-model-runtime-decoupling Specification

## Purpose
Define the runtime contract after removing the built-in `local_model` service and enforcing external-API-only model integration.

## Requirements
### Requirement: local-model runtime SHALL NOT be bundled with the main application
The system SHALL NOT provide a built-in `local_model` runtime, startup mode, service orchestration path, or `SERVER_NAME == 'local_model'` execution profile as part of the supported main-application deployment model.

#### Scenario: unsupported local_model startup mode is invoked
- **WHEN** an operator or code path attempts to start or resolve the removed `local_model` runtime mode
- **THEN** the system rejects the mode as unsupported instead of starting a bundled local-model service

### Requirement: built-in local-model routing and profile branching SHALL be absent
The system SHALL remove built-in local-model URL inclusion, WSGI branching, settings branching, and service registration from production runtime paths.

#### Scenario: supported runtime initializes after removal
- **WHEN** the supported web/task runtime paths initialize after this change
- **THEN** they do so without any built-in `local_model` route inclusion or `SERVER_NAME == 'local_model'` branch dependency

### Requirement: model integration SHALL remain external-API-only
The system SHALL support model integration only through external API providers and SHALL NOT own embedded local embedding/reranker runtime execution.

#### Scenario: external provider runtime remains supported
- **WHEN** a supported external API provider is configured and used after this change
- **THEN** model access proceeds through the external provider path without requiring a bundled local-model runtime
