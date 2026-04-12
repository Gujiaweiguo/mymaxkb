## ADDED Requirements

### Requirement: Default runtime expectations must not require local-model-only dependency weight
The system MUST keep the default web and task runtime contract independent from local-model-only dependency expectations when those dependencies are not required for the selected runtime mode.

#### Scenario: Default runtime mode does not require local-model feature paths
- **WHEN** an operator runs the supported default web or task runtime mode without enabling local-model behavior
- **THEN** the runtime contract does not require local-model-only dependency expectations beyond what is necessary for the selected mode

#### Scenario: Optional local-model mode remains available
- **WHEN** an operator explicitly enables or starts local-model functionality through the supported runtime path
- **THEN** the repository continues to support that mode without redefining the default runtime contract for other modes
