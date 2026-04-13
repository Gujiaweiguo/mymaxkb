## MODIFIED Requirements

### Requirement: legacy built-in local-model provider state SHALL fail fast with actionable guidance
The system SHALL detect persisted or requested `model_local_provider` usage after built-in local-model removal and SHALL raise a deterministic, actionable unsupported-provider error instead of failing through opaque import or lookup errors.

#### Scenario: legacy local-model provider record is resolved
- **WHEN** provider resolution encounters persisted or requested `provider='model_local_provider'`
- **THEN** the system returns the defined unsupported-provider failure path with actionable guidance

### Requirement: UI SHALL expose only supported external provider options
The system SHALL NOT present the removed built-in local-model provider as a configurable provider option in the model-management UI.

#### Scenario: provider list is rendered after removal
- **WHEN** the model-management UI renders provider metadata and grouping
- **THEN** it excludes the built-in local-model provider and only shows supported external provider options

### Requirement: supported external providers SHALL remain available during removal
The system SHALL preserve supported external provider registration and validation behavior while removing the built-in local-model provider.

#### Scenario: external provider remains listed and usable
- **WHEN** provider list and credential validation flows execute after this change
- **THEN** supported external providers remain available with their documented behavior intact
