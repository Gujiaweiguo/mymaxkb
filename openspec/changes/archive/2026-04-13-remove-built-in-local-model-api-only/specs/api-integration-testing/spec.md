## MODIFIED Requirements

### Requirement: integration validation SHALL prove built-in local-model removal
The system MUST include automated validation that proves the built-in `local_model` runtime, provider registration, and frontend exposure have been removed from supported production paths.

#### Scenario: removed local-model symbols are absent from production code
- **WHEN** repository-level removal validation runs for this change
- **THEN** production code no longer contains unexpected references to `model_local_provider`, `LocalModelProvider`, `SERVER_NAME == 'local_model'`, or built-in local-model startup/service wiring

### Requirement: integration validation SHALL prove legacy local-model state is handled deterministically
The system MUST include automated validation for the fail-fast behavior triggered by legacy local-model provider state after removal.

#### Scenario: legacy local-model state is exercised in validation
- **WHEN** integration or targeted backend validation resolves legacy `model_local_provider` state after this change
- **THEN** the validation asserts the defined actionable unsupported-provider failure path

### Requirement: integration validation SHALL preserve supported runtime quality signals
The system MUST validate that supported backend and frontend quality signals continue to pass after built-in local-model removal.

#### Scenario: supported runtime checks run after removal
- **WHEN** post-change validation executes
- **THEN** `python apps/manage.py check`, `cd ui && npm run type-check`, `cd ui && npm run lint`, and `cd ui && npm run test` succeed for the supported system state
