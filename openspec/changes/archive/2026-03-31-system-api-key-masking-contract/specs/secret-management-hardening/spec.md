## MODIFIED Requirements

### Requirement: Persisted secrets are redacted in read paths
The system SHALL avoid echoing stored secret values back to administrators in normal read/list responses when the full secret is not required for immediate one-time use.

#### Scenario: persisted system API key is listed after creation
- **WHEN** an administrator lists existing system API keys after initial creation
- **THEN** the system returns a masked representation instead of the full stored secret while preserving key-management metadata
