## ADDED Requirements

### Requirement: Bootstrap credentials must not remain predictable standing credentials
The system SHALL treat bootstrap credentials as one-time setup inputs rather than permanent defaults. The system MUST NOT rely on a publicly documented or source-controlled predictable default password as the normal long-lived administrator credential.

#### Scenario: Installation without explicit bootstrap credential
- **WHEN** an installation or initialization flow reaches the point where an administrator credential is required
- **THEN** the system requires an explicit bootstrap credential path or an approved one-time initialization mechanism instead of silently using a predictable default password

#### Scenario: Predictable documented password is not accepted as steady-state behavior
- **WHEN** an operator deploys the system with no credential override and attempts to rely on a known default password
- **THEN** the system blocks or redirects that flow to the approved bootstrap or rotation path

### Requirement: First-use credential hardening must be enforceable
The system SHALL provide an enforceable first-use hardening path for bootstrap accounts. A bootstrap credential, if one is used, MUST be rotated or replaced before the account is treated as a normal long-lived administrator account.

#### Scenario: Bootstrap account signs in for the first time
- **WHEN** a bootstrap account authenticates using an initialization credential
- **THEN** the system requires credential rotation or equivalent hardening before allowing normal ongoing administrative use
- **AND** the account remains restricted to the enforced password-change flow until that hardening step succeeds

#### Scenario: Bootstrap credential has already been rotated
- **WHEN** the administrator account has completed the required first-use hardening step
- **THEN** subsequent authentication proceeds without repeating the bootstrap-only restriction
