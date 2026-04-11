## ADDED Requirements

### Requirement: Startup matrix tests SHALL cover local_model mode permutations
The system MUST include integration checks for startup behavior under enabled, disabled, and unreachable local_model conditions.

#### Scenario: local_model disabled startup path
- **WHEN** startup executes with `MAXKB_ENABLE_LOCAL_MODEL=false`
- **THEN** logs confirm local_model disabled marker and no local_model startup action

#### Scenario: local_model enabled startup path
- **WHEN** startup executes with `MAXKB_ENABLE_LOCAL_MODEL=true`
- **THEN** logs confirm local_model enabled marker and expected startup behavior

#### Scenario: local_model unreachable path
- **WHEN** startup or provider calls execute with unreachable local_model endpoint
- **THEN** system records unreachable marker and remains serviceable for non-local-model features
