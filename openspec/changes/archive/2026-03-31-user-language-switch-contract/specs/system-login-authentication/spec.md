## MODIFIED Requirements

### Requirement: System login authentication supports configured administrative sign-in methods
The system SHALL provide configurable administrative login authentication for community edition and enforce supported sign-in methods consistently at the admin entry point.

#### Scenario: authenticated actor switches language to a supported locale
- **WHEN** an authenticated actor requests the language-switch endpoint with a supported locale
- **THEN** the system persists the new language for that actor

#### Scenario: authenticated actor cannot switch language to an unsupported locale
- **WHEN** an authenticated actor requests the language-switch endpoint with an unsupported locale
- **THEN** the system rejects the request with an error listing the supported locales
