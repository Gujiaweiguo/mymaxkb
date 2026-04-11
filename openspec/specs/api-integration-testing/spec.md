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

### Requirement: Startup matrix tests SHALL cover local_model mode permutations
The system MUST include integration checks for startup behavior under enabled, disabled, and unreachable local_model conditions.

#### Scenario: local_model disabled startup path
- **WHEN** startup executes with `MAXKB_ENABLE_LOCAL_MODEL=false`
- **THEN** logs confirm local_model disabled marker and no local_model startup action

#### Scenario: local_model enabled startup path
- **WHEN** startup executes with `MAXKB_ENABLE_LOCAL_MODEL=true`
- **THEN** logs confirm local_model enabled marker and expected startup behavior

#### Scenario: local_model unreachable path
- **WHEN** startup or provider calls execute with unreachable local_model endpoint
- **THEN** system records unreachable marker and remains serviceable for non-local-model features

