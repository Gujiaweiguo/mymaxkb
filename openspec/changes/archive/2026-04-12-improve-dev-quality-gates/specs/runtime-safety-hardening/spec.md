## ADDED Requirements

### Requirement: Deployable runtime host validation must be explicitly configured
The system MUST define an explicit host-validation contract for deployable runtime profiles and MUST NOT rely on unrestricted host acceptance as the steady-state deploy configuration.

#### Scenario: Deployable runtime starts with explicit allowed hosts
- **WHEN** a deployable runtime profile is configured for web or related externally reachable service startup
- **THEN** the runtime resolves allowed hosts from explicit configuration instead of relying on an unrestricted wildcard default

#### Scenario: Development runtime preserves documented local behavior
- **WHEN** the repository is started through the documented local development workflow
- **THEN** local development host behavior remains available through the documented local configuration path without redefining the deployable host-validation contract

### Requirement: Critical startup and orchestration failures must not be silent
The system MUST surface actionable failures for critical startup, collect-static, migration, and service-orchestration paths instead of swallowing exceptions without diagnostic output.

#### Scenario: Critical startup helper encounters an exception
- **WHEN** a startup or orchestration helper encounters an unexpected exception while preparing the runtime
- **THEN** the failure is logged or surfaced explicitly enough for an operator or developer to identify the failing step

#### Scenario: Startup preparation cannot complete safely
- **WHEN** a required startup preparation step cannot complete successfully
- **THEN** the runtime does not report successful preparation implicitly and instead emits an explicit failure outcome
