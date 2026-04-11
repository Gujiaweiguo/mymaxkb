## Context

The repository already exposes a usable validation surface: backend Django tests through `apps/manage.py test`, frontend static checks through `npm run type-check` and `npm run lint`, frontend unit/component tests through `npm run test`, and Playwright coverage under `ui/e2e/`. The current gap is not the absence of commands, but the absence of a repository-level contract that runs them consistently in CI and makes failures visible before merge.

The project also follows a local-first workflow with PostgreSQL and Redis for realistic backend execution. That means the CI design must preserve parity with local development instead of inventing a separate validation model that only works in GitHub Actions. At the same time, the existing Playwright suite includes scenarios that are slower and in some cases credential-dependent, so the initial CI contract must distinguish between the required baseline and later-stage or advisory end-to-end checks.

## Goals / Non-Goals

**Goals:**
- Define a required CI baseline that runs the repository's supported backend and frontend validation commands.
- Keep local reproduction straightforward by aligning CI jobs with the documented local-first workflow.
- Separate mandatory validation from phased or advisory E2E coverage so the first rollout is stable.
- Create room to add a small number of high-value missing tests for core product paths without turning this change into a full testing overhaul.

**Non-Goals:**
- Achieving comprehensive repository-wide test coverage in this change.
- Replacing the current Django/Vitest/Playwright tooling with a different test stack.
- Making every Playwright scenario blocking on day one.
- Bundling unrelated lint rule tightening, dependency cleanup, or broad refactors into this change.

## Decisions

### Decision: Establish a layered CI baseline instead of a single monolithic validation job

The CI pipeline will be split into separately reported jobs for backend tests, frontend static checks, and frontend unit/component tests. This keeps failures diagnosable, allows selective evolution of individual layers, and avoids making one long-running job the only source of signal.

**Why this approach:**
- Faster diagnosis when only one validation layer fails.
- Easier to evolve one layer without destabilizing the others.
- Clearer branch protection and merge-readiness signals.

**Alternatives considered:**
- **Single all-in-one validation job:** simpler to author, but worse failure visibility and slower iteration.
- **Per-module matrix from day one:** more granular, but premature for the current maturity level and likely to add workflow complexity before the baseline is stable.

### Decision: Use repository-supported commands directly in CI

CI should call the same commands contributors are expected to run locally: backend via `apps/manage.py test`, frontend via `npm run type-check`, `npm run lint`, and `npm run test`.

**Why this approach:**
- Minimizes drift between local and CI behavior.
- Avoids introducing hidden wrappers that developers do not understand or reproduce locally.
- Keeps the contract grounded in commands already documented in the repository.

**Alternatives considered:**
- **Custom CI-only shell scripts:** can reduce YAML duplication, but tends to obscure what actually runs and creates another maintenance surface.
- **Different CI-only test entrypoints:** rejected because they would weaken local reproducibility.

### Decision: Treat backend tests, frontend static checks, and Vitest as the first required merge gates

The initial required baseline will consist of backend Django tests, frontend type-check, frontend lint, and frontend unit/component tests. These are the highest-value checks that already exist and are least likely to require unstable external setup beyond the repository's documented services.

**Why this approach:**
- It turns existing validation assets into immediate merge protection.
- It improves safety materially without waiting for the E2E suite to be production-grade in CI.
- It creates a stable contract that can be enforced quickly.

**Alternatives considered:**
- **Require Playwright from the first rollout:** higher confidence eventually, but higher flake and environment risk during baseline adoption.
- **Require only type-check and lint first:** cheaper to implement, but does not protect backend regressions or behavioral breakage well enough.

### Decision: Make Playwright phased, with explicit required vs advisory status

Playwright will be part of the design, but not all scenarios will be mandatory in the initial merge gate. The repository should explicitly classify which E2E checks are required, which are optional or advisory, and which remain gated on external credentials or further stabilization.

**Why this approach:**
- Preserves a stable baseline while still moving the project toward stronger end-to-end confidence.
- Avoids blocking merges on scenarios that depend on external credentials or brittle environment assumptions.
- Makes future promotion of critical E2E flows a policy decision rather than an ad hoc workflow change.

**Alternatives considered:**
- **Keep all E2E fully out of CI:** simpler, but loses visibility and delays maturity.
- **Make all E2E mandatory immediately:** too risky given current credential and stability constraints.

### Decision: Keep coverage additions narrowly targeted to core risk areas

Any new tests added under this change should focus on the highest-risk validation gaps that block confidence in the initial CI baseline, especially core product paths such as chat, workflow, and retrieval-backed flows.

**Why this approach:**
- Prevents scope explosion.
- Aligns with the proposal's goal of closing a small number of high-value gaps rather than rebuilding the full test pyramid.
- Keeps the change shippable and reviewable.

**Alternatives considered:**
- **Repository-wide coverage drive:** valuable, but too large for a single change centered on CI quality gates.

## Risks / Trade-offs

- **[CI runtime increases]** → Mitigation: split validation into independent jobs and keep the first required baseline limited to commands already in regular use.
- **[Backend tests may require service setup that differs across environments]** → Mitigation: follow the documented local-first PostgreSQL/Redis model in CI and document the same prerequisites for contributors.
- **[Playwright may remain flaky or credential-dependent]** → Mitigation: keep E2E classification explicit and promote only stable scenarios into the required baseline.
- **[Existing tests may surface latent failures once run consistently in CI]** → Mitigation: treat that as useful signal, roll out the baseline in a focused branch, and fix or quarantine invalid assumptions before enforcing branch protection broadly.
- **[Documentation drifts from actual CI commands]** → Mitigation: keep CI commands directly mapped to README/DEVELOPMENT guidance and update both together inside this change.

## Migration Plan

1. Add CI workflow definitions that run the required baseline jobs with the repository's documented environment prerequisites.
2. Verify the baseline commands pass in CI using current supported backend and frontend entrypoints.
3. Add or adjust a small number of high-value tests where the current baseline is too weak to protect critical flows.
4. Update contributor documentation so local reproduction mirrors CI behavior.
5. Enable required status checks for the baseline jobs.

**Rollback strategy:**
- If a newly required validation layer proves unstable, remove it from required status while keeping the workflow present as advisory signal.
- If a specific test cluster is flaky, narrow or quarantine that cluster rather than disabling the full validation layer.

## Open Questions

- Which Playwright scenarios are stable enough to be promoted first: login only, or login plus one administrative CRUD path?
- Should backend CI initially run the full Django suite on every relevant change, or should it allow scoped execution only after the baseline is proven stable?
- Do we want one workflow file with multiple jobs, or separate workflow files for backend, frontend, and E2E reporting?
