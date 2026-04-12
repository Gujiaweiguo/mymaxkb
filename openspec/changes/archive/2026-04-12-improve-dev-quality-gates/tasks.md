## 1. Runtime safety and CI baseline

- [x] 1.1 Replace unrestricted deploy-time host validation with an explicit allowed-hosts configuration contract for deployable runtime profiles.
- [x] 1.2 Remove silent exception swallowing from critical startup and orchestration helpers and emit actionable diagnostics for failure paths.
- [x] 1.3 Add the repository-supported deploy-oriented safety checks to CI for runtime/configuration-affecting changes.
- [x] 1.4 Align development and testing documentation with the required CI quality gates and their local reproduction steps.

## 2. Frontend shared-infrastructure cleanup

- [x] 2.1 Extract shared admin/chat bootstrap behavior into a maintained shared frontend bootstrap path.
- [x] 2.2 Isolate entry-specific router or mode wiring at the edge of the shared bootstrap path without duplicating the full initialization sequence.
- [x] 2.3 Split the shared frontend request layer into focused modules for core client behavior, streaming behavior, and download/export behavior.
- [x] 2.4 Run and fix repository-supported frontend static validation for the touched shared infrastructure files.

## 3. Regression coverage tightening

- [x] 3.1 Identify the minimum critical backend business paths for this phase and add meaningful Django-backed regression tests for them.
- [x] 3.2 Identify the stable frontend or end-to-end critical-flow baseline for this phase and add or promote the corresponding automated coverage.
  - Stable E2E baseline for this phase: advisory Playwright coverage under `ui/e2e/application.spec.ts`, `ui/e2e/entry-routing.spec.ts`, and credential-free navigation coverage in `ui/e2e/knowledge.spec.ts`, executed with `npx playwright test --grep-invert @deferred`.
  - Deferred E2E remains outside the baseline: `ui/e2e/chat.spec.ts` and credential-dependent knowledge upload scenarios.
  - Current environment note: the baseline is defined, but execution is blocked unless the backend proxy target on `127.0.0.1:3080` is running.
- [x] 3.3 Replace placeholder-only or nominal assertions in scoped critical test paths with repeatable behavior-focused assertions.

## 4. Local-model runtime isolation

- [x] 4.1 Define and implement the default runtime behavior so local-model-only expectations are not required in unsupported default web/task modes.
- [x] 4.2 Preserve explicitly enabled local-model startup behavior and validate that optional local-model mode still works through the supported runtime path.
- [x] 4.3 Document the resulting default-versus-optional runtime contract for local-model behavior and dependency expectations.

## 5. Final verification and change closeout

- [x] 5.1 Run the required backend and frontend validation commands introduced or affected by this change and resolve failures.
  - Required verification passed: `apps/manage.py test application.tests knowledge.tests test_runtime_safety`, `npm run test`, `npm run type-check`, `npm run lint`, `npm run build`, and `npm run build-chat`.
  - Advisory E2E remains environment-blocked in this session because the backend target at `127.0.0.1:3080` was not running while Playwright's Vite proxy attempted login flows.
- [x] 5.2 Verify that CI-required checks, local reproduction steps, and updated docs all reference the same supported commands.
- [x] 5.3 Review the final scope against the proposal, design, and specs to confirm the change remains a contract-tightening pass rather than an unrelated rewrite.
