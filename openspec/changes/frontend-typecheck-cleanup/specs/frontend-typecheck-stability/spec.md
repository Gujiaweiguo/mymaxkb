## ADDED Requirements

### Requirement: Targeted frontend type-check failures are resolved
The system MUST eliminate the known TypeScript errors in the scoped frontend files so the targeted cleanup can be validated with the repo's frontend type-check command.

#### Scenario: Scoped files no longer produce type-check errors
- **WHEN** `npm run type-check` is executed after the cleanup
- **THEN** the previously failing files in the scoped change do not report TypeScript errors

### Requirement: Type-check cleanup preserves existing runtime behavior
The system MUST correct typing and control-flow issues in the scoped files without introducing unrelated feature changes or UI behavior changes.

#### Scenario: File-local fixes avoid unrelated refactors
- **WHEN** the scoped frontend files are updated to resolve TypeScript errors
- **THEN** the changes remain limited to type safety, return-shape correctness, local annotations, or equivalent minimal corrections

### Requirement: Cleanup follows existing file-local typing patterns
The system MUST align each fix with the typing style already used in the edited file instead of introducing a new repo-wide typing convention.

#### Scenario: Mixed typing style is preserved where appropriate
- **WHEN** a scoped file uses an existing local typing pattern
- **THEN** the cleanup follows that local pattern unless a change is required to resolve the specific type-check error

### Requirement: Touched frontend files remain statically verifiable
The system MUST validate the cleanup with the repo's frontend static-analysis signals required for the touched files.

#### Scenario: Type-check validation is completed
- **WHEN** the scoped cleanup is finished
- **THEN** `npm run type-check` is used to verify the updated frontend code path

#### Scenario: Lint validation is run when touched code requires it
- **WHEN** the cleanup changes frontend code that is subject to lint-sensitive rules
- **THEN** `npm run lint` is run to confirm the edited files remain lint-clean
