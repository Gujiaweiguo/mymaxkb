# ci-quality-gates Specification

## Purpose
TBD - created by archiving change ci-validation-gates. Update Purpose after archive.
## Requirements
### Requirement: Continuous integration runs required repository validation commands
The system MUST run the repository's supported backend and frontend validation commands in continuous integration for pull requests and protected-branch updates.

#### Scenario: Pull request validation runs required checks
- **WHEN** a pull request updates backend or frontend code
- **THEN** continuous integration runs backend tests, frontend type-check, frontend lint, and frontend unit/component tests using the repository-supported commands

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

