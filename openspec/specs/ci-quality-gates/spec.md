# ci-quality-gates Specification

## Purpose
TBD - created by archiving change ci-validation-gates. Update Purpose after archive.
## Requirements
### Requirement: Continuous integration runs required repository validation commands
The system MUST run the repository's supported validation commands in continuous integration for pull requests and protected-branch updates according to the scoped regression baseline defined by the repository testing contract. For this change, required CI validation MUST remain aligned with the supported backend tests, frontend tests, and required safety checks, while avoiding accidental promotion of advisory or deferred E2E scenarios into merge-blocking gates.

#### Scenario: Required baseline checks run for qualifying changes
- **WHEN** a pull request updates backend code, frontend code, shared validation logic, or CI definitions affecting the scoped regression baseline
- **THEN** continuous integration runs the required repository-supported validation commands for that baseline and reports them as merge-blocking checks

#### Scenario: Advisory or deferred scenarios are not promoted implicitly
- **WHEN** a validation scenario is marked advisory, phased, or deferred in the repository testing contract
- **THEN** continuous integration does not treat that scenario as a required merge-blocking gate unless the repository explicitly promotes it

#### Scenario: Advisory E2E startup failure remains distinguishable from test failure
- **WHEN** the advisory E2E job cannot complete backend startup or readiness checks before browser tests begin
- **THEN** CI reports the advisory job failure as a startup/readiness problem without changing its advisory status
- **AND** the job leaves enough diagnostic output to identify whether the backend process or readiness probe failed

### Requirement: CI failures block merge readiness
The system MUST treat required validation job failures as merge-blocking signals until the failing checks pass on the updated revision.

#### Scenario: Required check fails
- **WHEN** a required CI validation job exits unsuccessfully
- **THEN** the change is not considered merge-ready until the failing validation is corrected and rerun successfully

### Requirement: Local and CI validation workflows stay aligned
The system MUST document how contributors reproduce required CI validation locally using the project's supported local-first workflow.

#### Scenario: Contributor reproduces CI locally
- **WHEN** a contributor reads the repository development or testing guidance after a CI failure
- **THEN** they can identify the corresponding local commands and environment prerequisites needed to reproduce the failing validation step

### Requirement: E2E enforcement can be phased in without redefining CI contracts
The system MUST allow end-to-end validation to be introduced or promoted in phases while keeping the required baseline CI contract explicit.

#### Scenario: Initial CI rollout excludes full E2E blocking
- **WHEN** the repository introduces the first required CI quality gates
- **THEN** the baseline required checks remain explicit even if some Playwright scenarios are initially advisory, scoped, or promoted in a later phase

#### Scenario: Advisory E2E artifact handling does not obscure the primary failure mode
- **WHEN** an advisory E2E run exits before Playwright generates its normal report output
- **THEN** CI handles report upload intentionally without surfacing a secondary missing-artifact warning as the primary diagnostic signal

### Requirement: Deploy-oriented repository safety checks participate in the CI baseline
The system MUST run repository-supported deploy-oriented safety checks in continuous integration when a change affects runtime configuration, startup behavior, or CI enforcement itself.

#### Scenario: Runtime-safety-affecting change triggers deploy-oriented validation
- **WHEN** a change touches runtime settings, startup orchestration, deployment-sensitive configuration, or CI definitions for required validation
- **THEN** CI runs the repository-supported deploy-oriented safety checks and reports the results as part of the required validation baseline

### Requirement: CI quality-gate documentation maps checks to local reproduction commands
The system MUST document each required CI quality gate with the corresponding supported local reproduction path and any necessary prerequisites so contributors can reproduce the scoped regression baseline without guessing.

#### Scenario: Contributor can reproduce a required scoped gate locally
- **WHEN** a contributor reviews a failing required CI quality gate for the scoped regression baseline
- **THEN** they can identify the supported local command sequence and prerequisites needed to reproduce that gate
