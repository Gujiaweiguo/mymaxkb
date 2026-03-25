## ADDED Requirements

### Requirement: Repository changes must be scanned for newly introduced secrets
The repository SHALL provide an automated secret-scanning path for local development and CI. The default scanning workflow MUST detect newly introduced credential-like material in tracked changes before those changes are merged.

#### Scenario: Developer checks local changes before commit
- **WHEN** a developer runs the repository's local secret-scanning workflow on staged or local changes
- **THEN** the workflow reports candidate secrets before the change is committed

#### Scenario: Pull request or branch change enters CI
- **WHEN** a proposed change is evaluated in CI
- **THEN** the repository runs automated secret scanning against the configured scope for that change

### Requirement: Secret scanning must support tuned exclusions and reviewed exceptions
The secret-scanning workflow SHALL support explicit exclusions and reviewed allowlists for known false-positive locations such as vendored dependencies, generated assets, and non-secret documentation examples. Exceptions MUST be narrow enough to avoid suppressing unrelated findings.

#### Scenario: Scanner reaches a vendored or generated path
- **WHEN** the scan encounters a path explicitly classified as vendored, generated, or otherwise outside the intended enforcement scope
- **THEN** the scanner excludes that path according to repository configuration

#### Scenario: Known example content resembles a credential
- **WHEN** a reviewed example or documentation string matches a scanner rule without containing a real secret
- **THEN** the repository applies a narrow allowlist or equivalent exception without suppressing unrelated findings elsewhere

### Requirement: Guardrail outcomes must be actionable to operators and developers
Secret-scanning results SHALL identify enough context for a developer or operator to determine whether the finding is a real secret, a weak default, or a false positive candidate. The workflow MUST preserve enough detail to support remediation or allowlist review.

#### Scenario: Scanner flags a candidate secret
- **WHEN** the scanning workflow produces a finding
- **THEN** the output includes the affected file or change context and enough rule detail for triage

#### Scenario: Finding is determined to be a false positive
- **WHEN** a reviewer determines that a scanner finding is not a real secret
- **THEN** the repository has a documented path to record a scoped exception rather than requiring the finding to be ignored ad hoc
