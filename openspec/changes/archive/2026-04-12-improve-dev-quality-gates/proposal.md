## Why

The repository now supports a broad product surface across Django services, workflow execution, retrieval, model-provider integrations, and two Vue-based frontend entry points, but its engineering safety rails have not kept pace with that complexity. Recent inspection found gaps in runtime safety, CI enforcement, frontend structure hygiene, and regression coverage that increase the risk of silent failures, insecure deployment defaults, and high-cost refactors.

## What Changes

- Tighten required engineering quality gates so backend and frontend validation remain enforced, reproducible locally, and aligned with the repository's supported workflow.
- Harden runtime safety expectations for deployable environments, including safer host validation defaults and explicit failure behavior instead of silent exception swallowing on critical startup and orchestration paths.
- Reduce avoidable frontend maintenance risk by consolidating duplicated app bootstrap logic and defining clearer boundaries for shared request/bootstrap structure.
- Strengthen regression protection for core backend and frontend flows so critical workflow, knowledge, and application-management paths have meaningful automated validation.
- Clarify how heavy local-model dependencies are isolated from general runtime paths so optional local-model support does not unnecessarily burden standard web/task deployments.

## Capabilities

### New Capabilities
- `runtime-safety-hardening`: Define runtime safety requirements for deployable environments, including explicit host validation contracts and non-silent failure behavior for critical startup/orchestration paths.
- `frontend-structure-hygiene`: Define maintainability requirements for shared frontend bootstrap and request-layer structure so dual entry points do not drift and shared infrastructure remains modular.

### Modified Capabilities
- `ci-quality-gates`: Expand and tighten the CI contract so required backend/frontend validation, deploy-oriented checks, and local reproduction guidance stay aligned.
- `backend-unit-testing`: Narrow the repository-supported backend regression contract around meaningful, repeatable Django-backed coverage for critical business paths rather than placeholder or purely nominal test presence.
- `frontend-typecheck-stability`: Extend frontend verification expectations to cover maintainable static-validation discipline around high-risk shared infrastructure files touched by this cleanup.
- `e2e-testing`: Clarify the minimum critical-user-flow coverage expected for stable regression protection while preserving phased rollout for advisory or credential-dependent scenarios.
- `local-model-runtime-decoupling`: Tighten the runtime contract so optional local-model dependencies and startup behavior remain decoupled from the default web/task runtime footprint.

## Impact

- Backend settings and startup paths under `apps/maxkb/settings/`, `apps/maxkb/conf.py`, `main.py`, and related orchestration helpers.
- Backend validation workflow in CI, pre-commit, and repository development/testing documentation.
- Frontend bootstrap, request infrastructure, store usage patterns, and validation workflow under `ui/src/` and `ui/package.json`.
- Existing OpenSpec capabilities for CI, testing, frontend validation, and local-model runtime behavior.
- Dependency/runtime packaging strategy for heavy local-model libraries used in limited execution paths.
