## ADDED Requirements

### Requirement: Feishu document sources can populate knowledge content in the first CE pass
The system SHALL define how Feishu document sources are configured and imported for knowledge ingestion in the first community-edition pass, while leaving later synchronization behavior to a follow-up extension.

#### Scenario: administrator selects Feishu document source for knowledge import
- **WHEN** an authorized administrator configures a Feishu document source for a knowledge asset
- **THEN** the system permits the source selection and import workflow defined for Feishu-backed knowledge ingestion

#### Scenario: first-pass Feishu source does not imply ongoing synchronization
- **WHEN** an administrator completes the first-pass Feishu document import flow
- **THEN** the system treats the imported knowledge content as populated without implying that ongoing synchronization is already available

#### Scenario: unavailable Feishu source cannot complete ingestion
- **WHEN** the configured Feishu document source is unavailable or not authorized for import
- **THEN** the system fails the import operation without treating the knowledge source as successfully updated
