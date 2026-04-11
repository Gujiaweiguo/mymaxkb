## MODIFIED Requirements

### Requirement: Critical user flows have E2E tests
The system MUST have E2E tests for the most important user journeys, and the repository MUST define which of those scenarios are immediately required in CI versus phased in later as the E2E suite matures.

#### Scenario: Login flow is tested
- **GIVEN** the application is deployed
- **WHEN** a user navigates to login and enters credentials
- **THEN** they are authenticated and redirected to the dashboard

#### Scenario: User management flow is tested
- **GIVEN** an admin user is logged in
- **WHEN** they create, edit, and delete a user
- **THEN** the operations complete successfully

#### Scenario: Application flow is tested
- **GIVEN** a user is logged in
- **WHEN** they create and configure an application
- **THEN** the application is saved and visible in the list

#### Scenario: CI-required E2E scope is explicit
- **WHEN** contributors review the repository testing contract
- **THEN** they can determine which E2E scenarios are required for CI pass/fail decisions and which remain phased or advisory

## ADDED Requirements

### Requirement: Phased E2E rollout preserves a stable required baseline
The system MUST allow the CI pipeline to introduce end-to-end coverage incrementally without making unstable or externally credential-dependent scenarios mandatory before they are ready.

#### Scenario: Credential-dependent E2E scenarios are not forced prematurely
- **WHEN** an E2E scenario depends on external credentials, unstable infrastructure, or non-deterministic setup
- **THEN** the scenario is not treated as part of the mandatory CI baseline until the repository explicitly promotes it to required status
