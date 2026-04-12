## Context

The repository already has backend Django tests, frontend Vitest coverage, Playwright E2E coverage, and CI quality gates, but the protection level is uneven across the most valuable runtime paths. The goal of this change is not to maximize overall coverage or introduce a new testing framework. The goal is to define and implement a stable, repository-supported regression baseline around the flows most likely to be affected by near-term maintenance work: workflow execution, chat behavior, and knowledge-related processing.

This change touches multiple existing capabilities rather than introducing a new one. That makes design useful here because the work crosses backend tests, API integration expectations, frontend or E2E validation scope, and CI gate definitions. Without an explicit design, the change could easily expand into an unbounded "test everything" effort.

Constraints:
- The repository uses Django's supported test workflow for backend validation and does not rely on a standardized pytest-first contract.
- Frontend validation already includes `npm run test`, `npm run type-check`, and `npm run lint`.
- Some E2E scenarios depend on external credentials or unstable setup and cannot be promoted blindly into required CI gates.
- The change must improve regression protection without redefining product behavior.

## Goals / Non-Goals

**Goals:**
- Define a minimum critical-path regression baseline that is explicit, repeatable, and narrow enough to implement in one scoped change.
- Cover one representative backend path each for workflow execution, chat behavior, and knowledge-processing behavior.
- Cover representative API-backed runtime behavior for those same domains where integration-level validation provides more confidence than lower-level tests.
- Clarify which user-visible E2E flows are required, which are advisory, and which remain deferred.
- Align CI-required checks and local reproduction guidance with the scoped baseline.

**Non-Goals:**
- Achieve exhaustive endpoint coverage across all backend modules.
- Introduce a new repository-wide testing framework or replace the current Django/Vitest/Playwright split.
- Promote all existing E2E scenarios to required CI gates.
- Refactor unrelated application code or change runtime architecture as part of this change.
- Set global coverage thresholds beyond what existing repository capabilities already define.

## Decisions

### Decision: Use a representative-path baseline instead of exhaustive coverage

This change will select one meaningful path in each high-value backend domain: workflow execution, chat behavior, and knowledge-processing. The same philosophy applies to integration and E2E coverage: representative, stable flows rather than broad endpoint or page coverage.

**Why:** This keeps the change implementable and ensures it creates real protection quickly. Exhaustive coverage would delay value, expand scope, and likely stall before producing a trustworthy baseline.

**Alternative considered:** Require broad endpoint-by-endpoint or module-by-module coverage. Rejected because it is too large for a first regression-focused change and would mix baseline definition with long-term testing backlog work.

### Decision: Keep backend critical-path protection in the repository-supported Django test workflow

Backend regression validation for this change will be implemented through the supported Django test command and existing test layout conventions.

**Why:** The repo already treats Django test execution as the supported backend contract locally and in CI. Using that contract avoids introducing tool ambiguity or fragmenting the validation story.

**Alternative considered:** Introduce a separate pytest-led path for the scoped change. Rejected because it would change testing conventions and distract from the actual goal of strengthening regression protection.

### Decision: Treat API integration tests as a focused extension of the baseline, not an all-endpoint promise

The modified integration-testing capability will explicitly require representative API-backed validation for workflow, chat, and knowledge domains, while making clear that this change does not promise full endpoint exhaustiveness.

**Why:** Several high-value failures only appear when request handling, auth, serializers, and response shapes interact together. Integration coverage is needed, but the scope must stay bounded.

**Alternative considered:** Limit the change to unit-style coverage only. Rejected because that would miss request/response regressions in the most important runtime paths.

### Decision: Separate advisory and deferred E2E flows explicitly from the required baseline

The design will identify a stable advisory E2E baseline made of flows that are deterministic and locally reproducible, while leaving credential-dependent or unstable scenarios deferred until explicitly promoted.

**Why:** The repo already has phased E2E expectations. Making this distinction explicit prevents accidental CI gate inflation and makes the testing contract easier for contributors to follow.

**Alternative considered:** Keep E2E status implicit in CI configuration only. Rejected because contributors need the contract documented at the capability level, not inferred from workflow files.

### Decision: Align CI with the documented baseline instead of expanding CI first

CI quality gates for this change will mirror the documented required baseline. Documentation and local reproduction mapping are part of the design, not follow-up polish.

**Why:** CI only helps if contributors can tell what is required and reproduce failures locally. Documentation drift would weaken the value of the new regression baseline.

**Alternative considered:** Update CI behavior first and backfill documentation later. Rejected because it increases confusion and makes failures harder to interpret.

## Risks / Trade-offs

- **[Risk] Representative-path selection could miss an adjacent critical failure mode** → **Mitigation:** choose flows that sit near the center of current system value: workflow, chat, and knowledge. Treat uncovered areas as explicit follow-on work rather than hidden assumptions.
- **[Risk] The change could drift into a broad testing rewrite** → **Mitigation:** hold scope to baseline-definition work plus only the tests and docs needed to satisfy that baseline.
- **[Risk] E2E advisory/deferred boundaries may remain ambiguous in practice** → **Mitigation:** document the classification in specs and design, and ensure CI references the same distinction.
- **[Risk] Existing tests may be flaky or too shallow to serve as the baseline** → **Mitigation:** prefer stable, meaningful assertions over broad but brittle test additions.
- **[Trade-off] Narrow scope delivers protection faster but leaves broader coverage gaps in place** → **Mitigation:** use this change as the foundation for later testing expansion rather than pretending it completes the testing story.

## Migration Plan

1. Confirm the exact representative backend, integration, and user-visible flows that will compose the scoped regression baseline.
2. Add or upgrade backend tests in the existing Django test suite for the selected workflow, chat, and knowledge paths.
3. Add or upgrade integration coverage for the selected API-backed paths.
4. Clarify frontend/E2E required versus advisory or deferred flows in repository testing guidance and supporting specs.
5. Update CI or CI-facing documentation so required checks match the documented baseline.
6. Validate the resulting baseline with the repository-supported backend, frontend, and scoped E2E commands.

Rollback strategy:
- If a newly proposed required validation step proves unstable, revert that step to advisory/deferred status instead of weakening the whole baseline.
- If a selected path cannot be made stable within scope, replace it with another representative path in the same domain and document the follow-up gap.

## Open Questions

- Representative backend targets are expected to center on `Workflow` graph behavior in `apps/application/flow/common.py`, `VoteSerializer.vote()` behavior in `apps/chat/serializers/chat_record.py`, and `Status` encode/decode behavior in `apps/knowledge/models/knowledge.py`. Validate these choices during implementation against fixture cost and stability.
- The current expected advisory Playwright baseline includes `ui/e2e/login.spec.ts`, `ui/e2e/entry-routing.spec.ts`, `application.spec.ts`, `workspace.spec.ts`, `user-management.spec.ts`, and `knowledge.spec.ts`, while `chat.spec.ts` remains deferred because it depends on external credentials and remote-backed behavior.
- Should the scoped baseline be expressed only in OpenSpec and repository docs, or also summarized in CI job names or workflow comments for faster contributor discovery?

## Follow-up Gaps

- Broader API integration coverage outside the selected representative paths remains intentionally out of scope for this first change.
- Advisory Playwright CRUD flows (`application`, `workspace`, `user-management`, `knowledge`) still need a later promotion pass once they are proven stable enough for required CI treatment.
- The remote-backed chat Playwright scenario remains deferred because it depends on external credentials and non-deterministic remote model behavior.
