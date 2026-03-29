## MODIFIED Requirements

### Requirement: Sensitive runtime secrets must not rely on insecure source-controlled fallbacks
The system SHALL source sensitive runtime secrets from explicit operator-provided configuration, such as environment variables or an approved external configuration source. The system MUST NOT substitute insecure hardcoded fallback values for sensitive secrets used in application integrity, encryption, or message signing.

#### Scenario: Required secret is missing during startup
- **WHEN** the application starts without a required sensitive secret value
- **THEN** the application fails with an explicit configuration error instead of using a predictable fallback secret

#### Scenario: Non-sensitive defaults remain allowed
- **WHEN** a configuration value is classified as non-sensitive operational metadata, such as a host or port default
- **THEN** the system may continue using a documented default without treating that value as a secret source

### Requirement: Secret source behavior must be consistent across runtime paths
The system SHALL apply the same secret-sourcing rules across web, worker, and related runtime paths that depend on shared secret material. Components that use signing keys, secret keys, or encryption passphrases MUST resolve those values from the same approved configuration contract.

#### Scenario: Web and task runtimes load signing material
- **WHEN** the web process and background task process both require signing or encryption material
- **THEN** both runtimes load the secret from approved configuration instead of deriving different implicit fallback values

#### Scenario: Secret-handling helper is invoked without configured secret material
- **WHEN** a helper responsible for encryption or signing is called without configured secret material
- **THEN** the helper returns an explicit configuration failure instead of inventing or deriving a substitute secret

### Requirement: Persisted secrets are redacted in read paths
The system SHALL avoid echoing stored secret values back to administrators in normal read/list responses when the full secret is not required for immediate one-time use.

#### Scenario: persisted application API key is listed after creation
- **WHEN** an administrator lists existing application API keys after initial creation
- **THEN** the system returns a masked representation instead of the full stored secret while preserving key-management metadata
