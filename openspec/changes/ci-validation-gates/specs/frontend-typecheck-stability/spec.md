## MODIFIED Requirements

### Requirement: Touched frontend files remain statically verifiable
The system MUST validate the cleanup with the repo's frontend static-analysis signals required for the touched files, and the supported frontend static checks MUST be runnable in CI as part of the repository's ongoing validation baseline.

#### Scenario: Type-check validation is completed
- **WHEN** the scoped cleanup is finished
- **THEN** `npm run type-check` is used to verify the updated frontend code path

#### Scenario: Lint validation is run when touched code requires it
- **WHEN** the cleanup changes frontend code that is subject to lint-sensitive rules
- **THEN** `npm run lint` is run to confirm the edited files remain lint-clean

#### Scenario: Frontend static checks run in CI
- **WHEN** a change affects frontend code or CI configuration related to frontend validation
- **THEN** continuous integration runs the repository-supported frontend static checks and reports their results as required validation signals

## ADDED Requirements

### Requirement: Frontend unit and component validation participates in the CI baseline
The system MUST run the repository-supported frontend unit and component test command as part of the required CI validation baseline for frontend-impacting changes.

#### Scenario: Frontend test suite is required for frontend-impacting changes
- **WHEN** a change touches frontend application code, shared frontend test infrastructure, or CI configuration affecting frontend validation
- **THEN** CI runs the supported frontend unit and component test command alongside the required static checks
