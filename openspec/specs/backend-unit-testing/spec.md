## Purpose

Define unit testing requirements and standards for backend code.
## Requirements
### Requirement: Backend unit tests cover all services, serializers, and utilities
The system MUST have unit tests for all service layer logic, serializer validation, and utility functions, and the supported backend test suite MUST be runnable through the repository's standard Django test command in local development and CI.

#### Scenario: Service layer functions are tested
- **GIVEN** a service function with business logic
- **WHEN** the function is called with valid and invalid inputs
- **THEN** tests verify expected behavior for both cases

#### Scenario: Serializer validation is tested
- **GIVEN** a serializer with validation rules
- **WHEN** data is passed to the serializer
- **THEN** tests verify validation passes for valid data and fails for invalid data

#### Scenario: Backend test command is CI-compatible
- **WHEN** continuous integration executes the repository-supported backend test command
- **THEN** the command validates the supported backend test suite without requiring ad hoc manual steps outside the documented workflow

### Requirement: Test coverage meets minimum threshold
The system MUST maintain 80%+ unit test coverage for backend code.

#### Scenario: Coverage is measured
- **WHEN** `pytest --cov=apps` is run
- **THEN** coverage report shows 80%+ for all modules

### Requirement: Tests are isolated and repeatable
The system MUST have tests that do not depend on external services or shared state.

#### Scenario: Tests use fixtures
- **GIVEN** test fixtures defined in `conftest.py`
- **WHEN** tests run
- **THEN** each test has independent data and cleanup

### Requirement: Backend test execution is a required CI quality gate
The system MUST run the supported backend test suite as a required CI check for changes that affect backend code or shared repository behavior.

#### Scenario: Backend-impacting change triggers backend validation
- **WHEN** a change touches backend application code, shared Python code, or CI configuration affecting backend validation
- **THEN** CI runs the supported backend test suite and reports its result as a required quality gate

### Requirement: Backend testing guidance matches the repository-supported test stack
The system MUST define backend testing expectations in terms of the repository-supported Django test workflow instead of requiring unsupported coverage or fixture tooling conventions.

#### Scenario: Backend testing contract references supported commands
- **WHEN** contributors or CI follow the backend testing contract for this repository
- **THEN** the contract refers to the supported Django test command and documented environment setup rather than unsupported pytest coverage or global fixture assumptions

### Requirement: Critical backend business paths have meaningful regression coverage
The system MUST provide repeatable backend regression coverage for critical repository-supported business paths, including workflow execution, knowledge-processing behavior, or equivalent high-value paths selected for the scoped change.

#### Scenario: Critical backend path is covered by supported tests
- **WHEN** the scoped change identifies a critical backend business path as part of the required regression baseline
- **THEN** the repository-supported Django test workflow includes automated validation for that path

#### Scenario: Placeholder-only backend coverage is insufficient for critical paths
- **WHEN** a critical backend path is only represented by placeholder or nominal test presence without meaningful assertions
- **THEN** the scoped backend testing work upgrades that path to meaningful repeatable assertions using the repository-supported test stack
