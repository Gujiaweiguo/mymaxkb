## ADDED Requirements

### Requirement: The stable critical-flow E2E baseline must be explicit
The system MUST define a stable minimum E2E baseline for critical user flows that can participate in regression protection without depending on deferred or credential-dependent scenarios.

#### Scenario: Stable required E2E scope is identified
- **WHEN** contributors review the repository testing contract for this change
- **THEN** they can identify which critical user flows form the stable E2E baseline independently from deferred or advisory scenarios

#### Scenario: Deferred scenarios remain outside the stable baseline
- **WHEN** an E2E scenario depends on external credentials, unstable infrastructure, or non-deterministic setup
- **THEN** that scenario is not required to satisfy the stable baseline until the repository explicitly promotes it
