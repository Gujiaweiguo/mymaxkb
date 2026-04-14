## MODIFIED Requirements

### Requirement: Authenticated actor resets the current password successfully
The system SHALL allow an authenticated actor to reset the current password and SHALL clear any password-change-required state for that actor as part of the successful update.

#### Scenario: authenticated actor resets the current password successfully
- **WHEN** an authenticated actor submits a supported new password and matching confirmation to the current-password reset endpoint
- **THEN** the system updates the stored password for that actor
- **AND** the system clears any password-change-required state for that actor
- **AND** the current authentication token is invalidated

### Requirement: Authenticated actor reads the current profile contract
The system SHALL return the current authenticated profile contract, including whether the authenticated local actor is required to change the current password before normal administrative use continues.

#### Scenario: authenticated actor reads the current profile contract
- **WHEN** an authenticated actor requests the current-profile endpoint
- **THEN** the system returns the actor identity, source, language, role, permissions, and workspace membership fields for that actor
- **AND** the system includes whether password editing is currently required for that actor

### Requirement: Local authenticated actor sees the password-change flag when required
The system SHALL surface the password-change-required state for local authenticated actors and SHALL enforce that flagged actors remain in the password-change flow until the current password is successfully updated.

#### Scenario: local authenticated actor sees the password-change flag when required
- **WHEN** a local authenticated actor with a required password change requests the current-profile endpoint
- **THEN** the system marks the profile as requiring password edit

#### Scenario: local authenticated actor is blocked from normal authenticated APIs while password change is required
- **WHEN** a local authenticated actor with a required password change requests an authenticated API outside the approved password-change flow endpoints
- **THEN** the system rejects the request because password change is required before continuing

#### Scenario: local authenticated actor can complete the password-change flow while blocked
- **WHEN** a local authenticated actor with a required password change requests the current-profile, current-password-reset, logout, or language-switch endpoint during the enforced password-change flow
- **THEN** the system allows the request to proceed according to the endpoint contract
