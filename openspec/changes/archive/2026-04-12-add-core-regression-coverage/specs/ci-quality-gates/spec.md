## MODIFIED Requirements

### Requirement: Continuous integration runs required repository validation commands
The system MUST run the repository's supported validation commands in continuous integration for pull requests and protected-branch updates according to the scoped regression baseline defined by the repository testing contract. For this change, required CI validation MUST remain aligned with the supported backend tests, frontend tests, and required safety checks, while avoiding accidental promotion of advisory or deferred E2E scenarios into merge-blocking gates.

#### Scenario: Required baseline checks run for qualifying changes
- **WHEN** a pull request updates backend code, frontend code, shared validation logic, or CI definitions affecting the scoped regression baseline
- **THEN** continuous integration runs the required repository-supported validation commands for that baseline and reports them as merge-blocking checks

#### Scenario: Advisory or deferred scenarios are not promoted implicitly
- **WHEN** a validation scenario is marked advisory, phased, or deferred in the repository testing contract
- **THEN** continuous integration does not treat that scenario as a required merge-blocking gate unless the repository explicitly promotes it

### Requirement: CI quality-gate documentation maps checks to local reproduction commands
The system MUST document each required CI quality gate with the corresponding supported local reproduction path and any necessary prerequisites so contributors can reproduce the scoped regression baseline without guessing.

#### Scenario: Contributor can reproduce a required scoped gate locally
- **WHEN** a contributor reviews a failing required CI quality gate for the scoped regression baseline
- **THEN** they can identify the supported local command sequence and prerequisites needed to reproduce that gate
