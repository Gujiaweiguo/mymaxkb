## MODIFIED Requirements

### Requirement: The stable critical-flow E2E baseline must be explicit
The system MUST define a stable minimum end-to-end regression baseline for critical user flows that can participate in regression protection without depending on deferred or credential-dependent scenarios. For this change, the stable baseline MUST explicitly identify which repository-supported user-visible flows remain advisory and which stay deferred because they depend on external credentials or unstable setup, while keeping the required CI baseline explicit in the repository testing contract.

#### Scenario: Stable advisory flows are identified
- **WHEN** contributors review the repository E2E testing contract after this change
- **THEN** they can identify the minimum stable user-visible flows that participate in regression protection without mistaking them for merge-blocking requirements

#### Scenario: Advisory flows remain distinguishable from required flows
- **WHEN** contributors review the repository E2E testing contract after this change
- **THEN** they can distinguish advisory or phased E2E scenarios from the stable required baseline without inferring hidden requirements

#### Scenario: Credential-dependent flows remain deferred until explicitly promoted
- **WHEN** an E2E scenario depends on external credentials or non-deterministic setup
- **THEN** it is not treated as part of the mandatory stable baseline until the repository explicitly promotes it
