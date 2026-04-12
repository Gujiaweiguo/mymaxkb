## MODIFIED Requirements

### Requirement: All API endpoints have integration tests
The system MUST maintain repeatable integration tests for the critical API-backed runtime paths that form this repository's supported regression baseline. For this change, the required integration baseline MUST cover representative API-backed flows for workflow-related behavior, chat-related behavior, and knowledge-related behavior rather than requiring immediate exhaustive endpoint coverage across every module.

#### Scenario: Workflow-related API path is covered
- **WHEN** contributors run the repository-supported integration test workflow for this change
- **THEN** at least one scoped workflow-related API-backed path is validated with meaningful assertions for request handling and expected response behavior

#### Scenario: Chat-related API path is covered
- **WHEN** contributors run the repository-supported integration test workflow for this change
- **THEN** at least one scoped chat-related API-backed path is validated with meaningful assertions for request handling and expected response behavior

#### Scenario: Knowledge-related API path is covered
- **WHEN** contributors run the repository-supported integration test workflow for this change
- **THEN** at least one scoped knowledge-related API-backed path is validated with meaningful assertions for request handling and expected response behavior

#### Scenario: Unsupported exhaustive endpoint expansion is not implied by this change
- **WHEN** contributors review the integration-testing contract introduced by this change
- **THEN** they can distinguish the required critical-path regression baseline from future broader endpoint-coverage work
