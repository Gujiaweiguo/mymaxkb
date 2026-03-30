## ADDED Requirements

### Requirement: Public system profile information is exposed consistently
The system SHALL expose public system profile information through a stable read-only API.

#### Scenario: public actor reads system profile
- **WHEN** any actor requests the public system profile endpoint
- **THEN** the system returns the current public profile payload including version, edition, license validity, and RSA key information
