## 1. Secret-scanning baseline exploration

- [x] 1.1 Review the existing gitleaks CI workflow, pre-commit hook, allowlist config, and reviewed ignore file
- [x] 1.2 Run or inspect the current repository-level secret scan to identify the smallest false-positive tuning gap in tracked files

## 2. Minimal guardrail tuning slice

- [x] 2.1 Add the narrowest reviewed allowlist/exclusion updates needed for the current tracked false-positive surface
- [x] 2.2 Update developer/security documentation for the local verification and exception-review workflow if the current docs are incomplete
- [x] 2.3 Re-run the repository-configured secret scan and confirm the tuned workflow remains actionable

## 3. Follow-up scope decision

- [x] 3.1 Evaluate whether test-fixture exclusions should remain file-specific or expand to broader test-path conventions
- [x] 3.2 Evaluate whether the dedicated `secret-scan.yml` workflow is sufficient or a follow-up CI integration step belongs in this change

## 4. Packaging and verification

- [x] 4.1 Run the final secret-scanning verification for the implemented slice
- [ ] 4.2 Package the change into atomic commits and create a PR
