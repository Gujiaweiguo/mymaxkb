## 1. Advisory E2E backend startup contract

- [x] 1.1 Update the advisory E2E workflow in `.github/workflows/ci.yml` so backend startup writes to a stable log path and readiness failure surfaces actionable diagnostics.
- [x] 1.2 Replace or refine the current backend wait step so it uses an explicit readiness contract that can distinguish backend startup failure from later Playwright test failure.
- [x] 1.3 If needed, extract the readiness logic into a small helper script or clearly bounded workflow step so the CI behavior stays readable and repeatable.

## 2. Advisory artifact and runtime behavior

- [x] 2.1 Update advisory Playwright report handling so upload only runs when report output actually exists, avoiding secondary missing-artifact noise.
- [x] 2.2 Verify `ui/playwright.config.ts` and the CI workflow remain aligned on frontend startup assumptions, report paths, and advisory execution scope.
- [x] 2.3 Ensure advisory E2E failure output makes it obvious whether the job failed during backend startup/readiness or during browser execution.

## 3. Validation and regression proof

- [ ] 3.1 Re-run the advisory E2E CI path and confirm backend-startup failures, if any remain, produce explicit diagnostics rather than ambiguous readiness timeouts.
- [ ] 3.2 Verify that successful advisory Playwright runs still upload usable report artifacts and that pre-Playwright failures no longer emit misleading missing-report warnings.
- [ ] 3.3 Update any related testing or contributor guidance if the local/CI reproduction path changes as part of the readiness stabilization.
