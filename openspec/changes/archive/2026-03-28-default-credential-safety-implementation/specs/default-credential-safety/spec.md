## MODIFIED Requirements

### Requirement: Bootstrap credentials must not remain predictable standing credentials
The system SHALL treat bootstrap credentials as one-time setup inputs rather than permanent defaults and enforce the resulting hardening state consistently across authenticated administrative access paths.

#### Scenario: flagged bootstrap account attempts normal authenticated access
- **WHEN** an administrative account is marked as requiring password change because it still uses a bootstrap or initialization credential
- **THEN** the system blocks normal authenticated access except for approved password-change and session-management paths

#### Scenario: bootstrap credential flag has been cleared after rotation
- **WHEN** the administrative account has completed the required password rotation flow
- **THEN** the system permits subsequent authenticated access without the bootstrap-only restriction

### Requirement: First-use credential hardening must be enforceable
The system SHALL expose an enforceable first-use hardening path for flagged bootstrap accounts and surface that state to the administrative client.

#### Scenario: profile indicates password hardening is required
- **WHEN** a flagged LOCAL administrative user retrieves the current profile state
- **THEN** the system returns the password-change-required indicator needed to drive first-use hardening UX
