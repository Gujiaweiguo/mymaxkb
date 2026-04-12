## Context

This change spans backend runtime safety, CI and local validation alignment, frontend structural maintainability, regression coverage, and runtime isolation for optional local-model functionality. The repository already has partial OpenSpec coverage for CI quality gates, backend testing, frontend static validation, E2E rollout, and local-model runtime decoupling, but recent repository inspection showed important gaps between those intended contracts and the current implementation state.

The most immediate backend concerns are deploy-time safety and diagnosability: permissive host validation in deployable settings, silent exception swallowing on startup/orchestration paths, and weak enforcement of backend-focused validation beyond the Django test command. On the frontend side, the project has a solid toolchain but still carries avoidable structural duplication in the two app entry points, a monolithic shared request layer, and weak static-safety discipline around shared infrastructure files. The project also has broad automated-test intent but relatively uneven protection in the most complex product surfaces, especially workflow- and orchestration-heavy paths.

This design treats the change as an engineering-foundation pass rather than a product-feature change. The goal is to tighten contracts and remove high-leverage maintenance risks without turning the effort into an open-ended architectural rewrite.

## Goals / Non-Goals

**Goals:**
- Define a phased technical approach for improving engineering quality gates across backend and frontend workflows.
- Establish runtime safety expectations for deployable environments, especially around host validation and explicit failure behavior for critical startup paths.
- Reduce frontend maintenance risk by consolidating duplicated bootstrap behavior and defining modular boundaries for shared request/bootstrap infrastructure.
- Improve regression protection for critical business paths with repository-supported validation signals rather than aspirational or unsupported tooling.
- Clarify how optional local-model support should remain isolated from the default runtime footprint.

**Non-Goals:**
- Re-architect the Django application into multiple services.
- Perform a repository-wide TypeScript strictness migration or remove all existing `any` usage in one pass.
- Introduce unsupported backend tooling conventions that do not match the repository's current Django-based test workflow.
- Make all E2E scenarios mandatory immediately, especially those that depend on external credentials or unstable infrastructure.
- Redesign product behavior, UI flows, or user-facing feature contracts unrelated to engineering safety and maintainability.

## Decisions

### Decision: Treat this as a contract-tightening change, not a broad rewrite

The change will focus on tightening engineering contracts that are already implied by the repository structure and OpenSpec coverage: CI validation, runtime safety, testability, and structural maintainability. This keeps the scope bounded and makes the work verifiable.

**Why:** The repository already contains meaningful conventions, test commands, and OpenSpec capabilities. The immediate risk is not lack of architecture, but drift between the intended engineering contract and the current code/config state.

**Alternatives considered:**
- **Broad platform refactor first:** rejected because it would greatly expand scope and delay risk reduction.
- **Only patch the most urgent bug-level issues:** rejected because the same classes of problems would recur without stronger validation contracts.

### Decision: Separate spec changes into safety, quality-gate, frontend-structure, and runtime-isolation concerns

This change will modify existing capabilities where repository contracts already exist and add narrowly scoped new capabilities where the current specs do not yet describe the needed behavior.

**Why:** Existing capabilities such as `ci-quality-gates`, `backend-unit-testing`, `frontend-typecheck-stability`, `e2e-testing`, and `local-model-runtime-decoupling` already provide a partial contract surface. Reusing them avoids spec duplication while allowing this change to sharpen requirements. New capabilities are only introduced for gaps that are not yet represented: runtime safety hardening and frontend structure hygiene.

**Alternatives considered:**
- **Create one brand-new umbrella capability for all optimization work:** rejected because it would overlap heavily with existing specs and weaken traceability.
- **Only modify existing capabilities:** rejected because runtime safety and frontend structure hygiene need first-class requirement language.

### Decision: Prefer repository-supported verification commands over introducing a new backend validation stack

Backend validation requirements will continue to center on the supported Django test workflow and deploy-safe management checks, while frontend validation will center on the existing `type-check`, `lint`, `test`, and phased E2E workflow.

**Why:** The repository already documents supported commands in README and development guidance. Introducing an additional backend lint/type-check stack as a mandatory requirement before the project is ready would create more friction than value. The change should first enforce the strongest signals the repository already supports.

**Alternatives considered:**
- **Require pytest/coverage as the primary backend contract:** rejected because the repository currently documents Django test commands as the supported path.
- **Require strict TypeScript or zero-`any` immediately:** rejected because it would expand scope beyond maintainable cleanup.

### Decision: Frontend cleanup should target shared infrastructure choke points first

The design prioritizes the shared bootstrap path and the request layer before broader store or page-level cleanup.

**Why:** `main.ts` and `chat.ts` duplication creates immediate drift risk, and the request layer is a central dependency for most business flows. Cleaning those choke points improves maintainability and testability with a relatively contained change surface.

**Alternatives considered:**
- **Start with broad page/component decomposition:** rejected because it would produce a large, hard-to-verify diff.
- **Start with a global store rewrite:** rejected because it touches many consumers and is better handled as a follow-on effort unless directly required by tasks in this change.

### Decision: Runtime safety hardening should prefer explicit configuration failures over permissive fallbacks

Critical startup and orchestration paths should fail explicitly when required safety-related configuration is absent or invalid, and should log actionable diagnostics instead of swallowing exceptions.

**Why:** Silent startup failures and permissive deploy defaults are high-cost operational risks. Engineering foundation work should reduce ambiguity for operators and developers before pursuing deeper optimization.

**Alternatives considered:**
- **Preserve permissive defaults for compatibility:** rejected because insecure or silent behavior is exactly what this change is intended to reduce.
- **Over-correct by making all configuration strict immediately:** rejected because some non-sensitive defaults are still reasonable and already supported by existing secret-handling specs.

### Decision: Heavy local-model dependencies should remain optional in default runtime expectations

The design will treat local-model functionality as an optional runtime concern whose dependency and startup contracts should not unnecessarily burden the default web/task footprint.

**Why:** Inspection showed that some heavyweight dependencies are used in limited paths relative to the overall repository. The design should preserve local-model functionality while making default deployment expectations clearer and leaner.

**Alternatives considered:**
- **Leave dependency footprint as-is:** rejected because it keeps unnecessary coupling in the runtime contract.
- **Split services aggressively now:** rejected because the immediate need is contract clarity, not service decomposition.

## Risks / Trade-offs

- **[Risk] Quality-gate tightening increases short-term CI friction** → **Mitigation:** phase requirements through explicit specs and tasks, and prefer repository-supported commands contributors can reproduce locally.
- **[Risk] Runtime safety hardening may expose latent environment misconfiguration** → **Mitigation:** document required configuration clearly and stage deploy-oriented checks alongside local reproduction guidance.
- **[Risk] Frontend shared-infrastructure cleanup may touch broad call paths** → **Mitigation:** keep the cleanup focused on bootstrap/request boundaries first and avoid unrelated page-level refactors.
- **[Risk] Regression-coverage goals can become open-ended** → **Mitigation:** scope coverage work to critical knowledge, workflow, and application-management flows rather than trying to backfill all historical gaps.
- **[Risk] Local-model runtime decoupling may create confusion about supported deployment modes** → **Mitigation:** keep the contract explicit about what remains supported in default web/task mode versus optional local-model mode.

## Migration Plan

1. Finalize specs for the modified and new capabilities so the contract is explicit before implementation.
2. Break implementation into phased tasks: runtime safety and CI baseline first, frontend shared-infrastructure cleanup second, focused regression coverage and local-model runtime isolation third.
3. Update repository documentation and CI workflow in step with any newly required validation command so local and CI behavior remain aligned.
4. Roll out deploy-safety checks in a way that surfaces misconfiguration early and clearly.
5. Keep rollback simple by treating most work as additive contract enforcement and narrowly scoped structural cleanup rather than irreversible system redesign.

## Open Questions

- Should backend linting become part of the required baseline in this change, or should this change stop at Django checks plus supported tests and leave backend lint standardization for a later change?
- How much of the current frontend request/store cleanup belongs in this change versus a follow-on frontend maintainability change?
- Should local-model dependency isolation be expressed only as runtime/startup behavior, or also as packaging/dependency-profile requirements?
- Which critical frontend and backend flows should be treated as the minimum required regression baseline for this phase?
