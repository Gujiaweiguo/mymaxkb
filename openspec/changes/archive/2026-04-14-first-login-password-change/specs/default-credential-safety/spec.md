## MODIFIED Requirements

### Requirement: First-use credential hardening must be enforceable
The system SHALL provide an enforceable first-use hardening path for bootstrap accounts. A bootstrap credential, if one is used, MUST be rotated or replaced before the account is treated as a normal long-lived administrator account.

#### Scenario: Bootstrap account signs in for the first time
- **WHEN** a bootstrap account authenticates using an initialization credential
- **THEN** the system requires credential rotation or equivalent hardening before allowing normal ongoing administrative use
- **AND** the account remains restricted to the enforced password-change flow until that hardening step succeeds

#### Scenario: Bootstrap credential has already been rotated
- **WHEN** the administrator account has completed the required first-use hardening step
- **THEN** subsequent authentication proceeds without repeating the bootstrap-only restriction
