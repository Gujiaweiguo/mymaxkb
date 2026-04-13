## Purpose

Define integration testing requirements and standards for API endpoints.
## Requirements
### Requirement: All API endpoints have integration tests
The system MUST have integration tests for every API endpoint across all modules.

#### Scenario: Endpoints are tested with valid requests
- **GIVEN** an API endpoint
- **WHEN** a valid request is sent with proper authentication
- **THEN** the endpoint returns expected response status and data

#### Scenario: Endpoints are tested with invalid requests
- **GIVEN** an API endpoint
- **WHEN** an invalid request is sent (missing fields, bad auth)
- **THEN** the endpoint returns appropriate error status and messages

### Requirement: Authentication and authorization are verified
The system MUST test that endpoints enforce proper auth and permissions.

#### Scenario: Unauthenticated access is rejected
- **GIVEN** a protected endpoint
- **WHEN** a request is sent without authentication
- **THEN** the endpoint returns 401 Unauthorized

#### Scenario: Insufficient permissions are rejected
- **GIVEN** a protected endpoint requiring specific permissions
- **WHEN** a request is sent by a user without those permissions
- **THEN** the endpoint returns 403 Forbidden

### Requirement: Database operations are verified
The system MUST test that API endpoints correctly interact with the database.

#### Scenario: Create operations persist data
- **WHEN** a create endpoint is called with valid data
- **THEN** the data is correctly stored in the database

#### Scenario: Query operations return correct results
- **WHEN** a query endpoint is called
- **THEN** it returns data matching the query parameters

### Requirement: integration validation SHALL prove built-in local-model removal
The system MUST include automated validation that proves the built-in `local_model` runtime, provider registration, and frontend exposure have been removed from supported production paths.

#### Scenario: removed local-model symbols are absent from production code
- **WHEN** repository-level removal validation runs for this change
- **THEN** production code no longer contains unexpected references to `model_local_provider`, `LocalModelProvider`, `SERVER_NAME == 'local_model'`, or built-in local-model startup/service wiring

### Requirement: integration validation SHALL prove legacy local-model state is handled deterministically
The system MUST include automated validation for the fail-fast behavior triggered by legacy local-model provider state after removal.

#### Scenario: legacy local-model state is exercised in validation
- **WHEN** integration or targeted backend validation resolves legacy `model_local_provider` state after this change
- **THEN** the validation asserts the defined actionable unsupported-provider failure path

### Requirement: integration validation SHALL preserve supported runtime quality signals
The system MUST validate that supported backend and frontend quality signals continue to pass after built-in local-model removal.

#### Scenario: supported runtime checks run after removal
- **WHEN** post-change validation executes
- **THEN** `python apps/manage.py check`, `cd ui && npm run type-check`, `cd ui && npm run lint`, and `cd ui && npm run test` succeed for the supported system state
