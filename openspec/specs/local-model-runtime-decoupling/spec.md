# local-model-runtime-decoupling Specification

## Purpose
TBD - created by archiving change ollama-local-model-decoupling-2026-04-10. Update Purpose after archive.
## Requirements
### Requirement: local_model startup SHALL be explicitly configurable
The system SHALL support `MAXKB_ENABLE_LOCAL_MODEL` to control whether local_model participates in web startup orchestration.

#### Scenario: local_model disabled for web startup
- **WHEN** `MAXKB_ENABLE_LOCAL_MODEL=false` and web startup command is executed
- **THEN** local_model process is not started as part of web startup

#### Scenario: local_model enabled for web startup
- **WHEN** `MAXKB_ENABLE_LOCAL_MODEL=true` and web startup command is executed
- **THEN** local_model process is started according to configured startup strategy

### Requirement: local_model standalone startup SHALL remain available
The system SHALL keep standalone startup of local_model available independent of web startup mode.

#### Scenario: standalone local_model startup
- **WHEN** operator runs local_model standalone startup command
- **THEN** local_model starts successfully without requiring web process startup

### Requirement: runtime profile SHALL be observable
The system SHALL emit deterministic runtime markers for `runtime_profile` and local_model enablement state during startup.

#### Scenario: runtime marker emitted on startup
- **WHEN** any startup entrypoint initializes runtime profile
- **THEN** logs include machine-parseable markers for profile and local_model state

