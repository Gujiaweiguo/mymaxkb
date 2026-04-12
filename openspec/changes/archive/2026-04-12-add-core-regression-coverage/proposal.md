## Why

The repository already has meaningful backend, frontend, and CI validation infrastructure, but regression protection is uneven across the highest-value runtime paths. Core flows such as workflow execution, chat behavior, and knowledge-processing need a clearer, repeatable baseline before broader quality, typing, or dependency changes proceed.

## What Changes

- Define a scoped regression baseline for critical backend runtime paths, especially workflow execution, chat-pipeline behavior, and knowledge-processing flows.
- Clarify which API-backed runtime paths require repeatable integration coverage under the repository-supported test contract.
- Clarify the stable frontend and end-to-end regression baseline for critical user-visible flows without forcing deferred or credential-dependent scenarios into the required gate.
- Align CI quality gates and local reproduction guidance with the scoped regression baseline so contributors can tell which validations are mandatory.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `backend-unit-testing`: strengthen the requirement that critical backend business paths have meaningful, repeatable regression coverage using the repository-supported Django test workflow.
- `api-integration-testing`: refine which critical API-backed runtime paths must be covered as integration-level regression protection for this repository.
- `e2e-testing`: clarify the stable critical-flow baseline that protects key user-visible paths without expanding required coverage to unstable or credential-dependent scenarios.
- `ci-quality-gates`: align required CI validation with the scoped regression baseline and documented local reproduction guidance.

## Impact

- Backend tests under `apps/application/`, `apps/chat/`, `apps/knowledge/`, and related runtime-sensitive modules
- Frontend and E2E validation expectations under `ui/`
- CI/testing documentation and required validation contracts
- No breaking API or product behavior changes are intended; this change focuses on regression protection and validation scope
