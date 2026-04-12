## MODIFIED Requirements

### Requirement: Critical backend business paths have meaningful regression coverage
The system MUST provide repeatable backend regression coverage for critical repository-supported business paths selected for the scoped change. For this change, the minimum backend regression baseline MUST cover workflow execution behavior, chat-pipeline behavior, and knowledge-processing behavior through the repository-supported Django test workflow.

#### Scenario: Critical backend baseline covers workflow execution behavior
- **WHEN** contributors run the supported backend Django test workflow for this change
- **THEN** the suite includes automated regression validation for at least one scoped workflow execution path under `apps/application/`

#### Scenario: Critical backend baseline covers chat-pipeline behavior
- **WHEN** contributors run the supported backend Django test workflow for this change
- **THEN** the suite includes automated regression validation for at least one scoped chat-pipeline behavior under `apps/application/` or `apps/chat/`

#### Scenario: Critical backend baseline covers knowledge-processing behavior
- **WHEN** contributors run the supported backend Django test workflow for this change
- **THEN** the suite includes automated regression validation for at least one scoped knowledge-processing behavior under `apps/knowledge/`

#### Scenario: Placeholder-only coverage remains insufficient for scoped critical paths
- **WHEN** a scoped critical backend path is represented only by nominal test presence without meaningful assertions
- **THEN** the repository-supported backend testing work for this change upgrades that path to repeatable assertions that validate observable behavior
