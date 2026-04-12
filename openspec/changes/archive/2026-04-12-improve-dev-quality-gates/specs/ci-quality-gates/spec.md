## ADDED Requirements

### Requirement: Deploy-oriented repository safety checks participate in the CI baseline
The system MUST run repository-supported deploy-oriented safety checks in continuous integration when a change affects runtime configuration, startup behavior, or CI enforcement itself.

#### Scenario: Runtime-safety-affecting change triggers deploy-oriented validation
- **WHEN** a change touches runtime settings, startup orchestration, deployment-sensitive configuration, or CI definitions for required validation
- **THEN** CI runs the repository-supported deploy-oriented safety checks and reports the results as part of the required validation baseline

### Requirement: CI quality-gate documentation maps checks to local reproduction commands
The system MUST document each required CI quality gate with the corresponding supported local reproduction path when local prerequisites are necessary.

#### Scenario: Contributor investigates a failing required check
- **WHEN** a contributor reviews a failing required CI quality gate
- **THEN** they can identify the supported local command sequence and prerequisites needed to reproduce that gate without guessing at undocumented workflow steps
