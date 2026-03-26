## Purpose

Define unit testing requirements and standards for backend code.

## Requirements

### Requirement: Backend unit tests cover all services, serializers, and utilities
The system MUST have unit tests for all service layer logic, serializer validation, and utility functions.

#### Scenario: Service layer functions are tested
- **GIVEN** a service function with business logic
- **WHEN** the function is called with valid and invalid inputs
- **THEN** tests verify expected behavior for both cases

#### Scenario: Serializer validation is tested
- **GIVEN** a serializer with validation rules
- **WHEN** data is passed to the serializer
- **THEN** tests verify validation passes for valid data and fails for invalid data

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
