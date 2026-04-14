## Context

The repository already treats Playwright coverage as advisory in CI via `.github/workflows/ci.yml`, but the advisory signal is noisier than it should be. In the current E2E job, Django is started manually with `python apps/manage.py runserver 0.0.0.0:8080`, then a bespoke Python loop probes `http://127.0.0.1:8080/admin/api/user/profile` for up to 120 seconds and treats either `200` or `401` as proof of readiness. Only after that does Playwright run. When this wait step fails, the job exits before any browser test runs, so the advisory result reflects backend startup ambiguity rather than E2E coverage.

There is also a second source of noise: the workflow always tries to upload `ui/playwright-report/` even when the advisory job fails before Playwright has produced any report directory. That yields a secondary “No files were found” warning, which obscures the primary failure mode. Meanwhile `ui/playwright.config.ts` already defines HTML and JSON reporters under `playwright-report/`, and the E2E suite itself is scoped with `@advisory` tags and `--grep-invert @deferred`, so the instability is in the runtime envelope rather than in the test contract.

This change therefore sits across CI orchestration and E2E runtime assumptions. It should make the advisory job better at proving backend/server availability, surfacing startup failure details, and handling report artifacts intentionally, without promoting advisory E2E to a required gate.

## Goals / Non-Goals

**Goals:**
- Make the advisory E2E job distinguish backend-startup failure from Playwright test failure.
- Improve CI diagnostics so a failed readiness check leaves enough evidence to debug quickly.
- Ensure report upload logic behaves intentionally when Playwright never starts or produces no report directory.
- Keep advisory E2E non-blocking while making its signal more trustworthy.

**Non-Goals:**
- Promote advisory E2E to a required merge-blocking gate.
- Expand the E2E suite’s product coverage beyond readiness-related stabilization.
- Redesign frontend Playwright scenarios or broader backend startup architecture outside the advisory CI path.
- Replace Django’s development server with a production-grade process manager across the whole repository.

## Decisions

### 1. Keep the advisory job structure, but make backend readiness an explicit contract

The current CI shape is already reasonable: backend tests and frontend tests run first, then the advisory E2E job provisions its own database/Redis services, migrates the database, starts the backend, and runs Playwright. The design should preserve that structure instead of inventing a separate E2E orchestration system. The change is to make backend readiness explicit and diagnosable rather than implied by one polling loop.

Concretely, the readiness phase should:
- start the backend in a way that captures logs deterministically,
- poll a small number of known-good endpoints with explicit success criteria,
- emit backend logs and the final readiness failure reason before exiting.

**Why this approach:** it improves the weakest part of the current job without destabilizing the broader CI topology.

**Alternatives considered:**
- **Move all backend startup into Playwright `webServer`.** Rejected because the backend process lives outside `ui/` and the workflow already has backend-specific setup steps (venv, migrations, pgvector) that are clearer in GitHub Actions than in Playwright config.
- **Promote the wait loop into a repository-wide reusable service manager first.** Rejected because that is a larger infrastructure refactor than this stabilization change needs.

### 2. Readiness should probe a stable server-health signal, not only an authenticated business endpoint

The current health probe hits `/admin/api/user/profile` and treats `401` as acceptable. That works only if routing, middleware, and auth behavior all line up as expected during startup. The design should prefer a more stable readiness target where possible: either a lightweight public endpoint that proves Django routing is live, or a two-tier probe strategy that first proves server/process reachability and then confirms an expected application response.

The preferred direction is:
- first probe a public or unauthenticated endpoint that is expected to return `200`,
- if no suitable public endpoint exists, keep the current protected endpoint as a second-tier application check rather than the only signal,
- on timeout, print backend logs before failing.

**Why this approach:** it separates “the server is up” from “a protected API returned the expected auth behavior,” which makes failures more legible.

**Alternatives considered:**
- **Continue accepting only `200`/`401` on `/admin/api/user/profile`.** Rejected because it couples readiness too tightly to auth-layer behavior.
- **Use a raw TCP port-open check only.** Rejected because a listening socket does not prove the app is routing requests successfully.

### 3. Backend startup and readiness diagnostics should be first-class workflow steps

The workflow should explicitly surface backend logs on readiness failure instead of making contributors infer the cause from a timeout. The design should add a failure-path diagnostic step that always prints or uploads the server log captured from `runserver`, and should keep readiness logic compact enough that the failure mode is obvious from one job page.

This includes:
- using a stable log file path,
- dumping the last relevant portion of the log when readiness fails,
- optionally preserving the log as an artifact for advisory job failures.

**Why this approach:** advisory checks are only useful if failures are cheap to interpret.

**Alternatives considered:**
- **Leave diagnostics entirely to manual reruns.** Rejected because the current advisory noise already costs too much time to interpret.

### 4. Playwright artifact upload should be conditional on actual artifact existence

The workflow currently uses `if: always()` for the Playwright report upload, which is good for failed test runs but noisy when Playwright never starts. The design should keep “upload on failure/success when artifacts exist” behavior while making missing-report cases intentional, either by checking for the directory before upload or by ensuring the report directory is created predictably before execution.

The preferred direction is to gate artifact upload on the existence of `ui/playwright-report/` rather than treating a missing directory as a warning-worthy event.

**Why this approach:** it preserves useful debugging artifacts without burying the primary failure reason under secondary warnings.

**Alternatives considered:**
- **Always create an empty report directory up front.** Acceptable but less expressive than explicitly conditioning upload on existence.
- **Remove report upload entirely.** Rejected because report artifacts are valuable when Playwright actually runs and fails.

### 5. Keep Playwright config focused on frontend servers; do not overload it with backend lifecycle concerns

`ui/playwright.config.ts` already manages the frontend web servers for `admin.html` and `chat.html`. The design should keep that responsibility scoped to frontend bootstrapping. Any backend-specific readiness refinement should stay in CI or a dedicated helper script invoked by CI, rather than teaching Playwright config to manage a Python process it does not own well.

**Why this approach:** it maintains a clean separation between frontend test harness concerns and backend runtime provisioning.

**Alternatives considered:**
- **Add backend server startup to Playwright `webServer`.** Rejected because it mixes Python environment setup and frontend test harness configuration in a way that is harder to debug in CI.

## Risks / Trade-offs

- **[Risk] A public readiness endpoint might prove HTTP reachability without proving all advisory E2E prerequisites are ready.** → Mitigation: use a layered readiness check that can combine a public health signal with a lightweight application-level response check.
- **[Risk] Adding too much diagnostic output could make CI logs noisy.** → Mitigation: emit detailed backend logs only on failure or in a bounded tail section.
- **[Risk] Keeping backend startup outside Playwright means the workflow still owns more orchestration logic.** → Mitigation: isolate readiness logic into a small helper script or clearly bounded workflow step instead of spreading it across many steps.
- **[Risk] Conditional artifact upload may hide useful evidence if the report path changes unexpectedly.** → Mitigation: keep the report path centralized and explicit in both the workflow and Playwright config.

## Migration Plan

1. Update the CI workflow and/or supporting helper logic so advisory E2E backend startup captures logs and uses a more explicit readiness contract.
2. Adjust artifact upload behavior so missing Playwright output is handled intentionally.
3. Run the advisory E2E job in CI to confirm that startup failures, if any remain, now produce actionable diagnostics rather than ambiguous timeouts.

**Deployment / rollout:** No application deployment migration is required. The rollout is limited to CI and E2E runtime behavior.

**Rollback:** Revert the workflow/helper changes to restore the prior advisory job behavior if the new readiness logic proves too strict or too permissive.

## Open Questions

- Is there an existing public admin-facing endpoint we should standardize on for Django readiness, or should this change introduce a minimal CI-safe health check target?
- Should backend startup diagnostics be printed inline in the job log, uploaded as a separate artifact, or both?
- Is the cleanest implementation a shell/Python helper under the repository, or a more verbose but self-contained inline workflow step?
