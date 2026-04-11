## ADDED Requirements

### Requirement: Frontend static checks run in CI
The system MUST run the repository-supported frontend static checks in CI as required validation signals for frontend-impacting changes.

#### Scenario: Frontend static checks run in CI
- **WHEN** a change affects frontend code or CI configuration related to frontend validation
- **THEN** continuous integration runs `npm run type-check` and `npm run lint` and reports their results as required validation signals

### Requirement: Frontend unit and component validation participates in the CI baseline
The system MUST run the repository-supported frontend unit and component test command as part of the required CI validation baseline for frontend-impacting changes.

#### Scenario: Frontend test suite is required for frontend-impacting changes
- **WHEN** a change touches frontend application code, shared frontend test infrastructure, or CI configuration affecting frontend validation
- **THEN** CI runs the supported frontend unit and component test command alongside the required static checks
