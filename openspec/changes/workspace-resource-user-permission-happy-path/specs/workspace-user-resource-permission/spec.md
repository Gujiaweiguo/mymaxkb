## MODIFIED Requirements

### Requirement: Workspace user-resource permissions support successful CE user-scoped administration flows
The system SHALL allow authorized CE administrators to view and edit workspace user-resource permissions through the user-scoped administration surface.

#### Scenario: administrator lists users authorized for a resource in CE
- **WHEN** an administrator requests the resource-user permission list for a resource in the CE default workspace
- **THEN** the system returns the current user authorization state for that resource

#### Scenario: administrator pages users authorized for a resource in CE
- **WHEN** an administrator requests the paged resource-user permission list for a resource in the CE default workspace
- **THEN** the system returns a paginated result with user authorization data for that resource

#### Scenario: administrator grants view permission from the resource axis in CE
- **WHEN** an administrator edits a resource's authorized users with `VIEW` in the CE default workspace
- **THEN** the system persists the mapped `WorkspaceUserResourcePermission` state for that user and resource

#### Scenario: administrator clears permission from the resource axis in CE
- **WHEN** an administrator edits a resource's authorized users with `NOT_AUTH` in the CE default workspace
- **THEN** the system updates the stored `WorkspaceUserResourcePermission` state to remove effective access for that user and resource
