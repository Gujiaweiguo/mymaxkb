## Purpose

Define E2E testing requirements and standards for critical user flows.

## Requirements

### Requirement: Critical user flows have E2E tests
The system MUST have E2E tests for the most important user journeys.

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

### Requirement: E2E tests run in isolation
The system MUST have E2E tests that do not interfere with each other.

#### Scenario: Tests use independent data
- **WHEN** E2E tests run
- **THEN** each test has independent test data and cleanup

### Requirement: E2E tests verify both happy path and error handling
The system MUST test successful operations and error scenarios.

#### Scenario: Happy path is tested
- **GIVEN** valid inputs and states
- **WHEN** user performs an action
- **THEN** the action completes successfully

#### Scenario: Error path is tested
- **GIVEN** invalid inputs or error conditions
- **WHEN** user performs an action
- **THEN** appropriate error messages are shown
