## 1. CI Baseline Definition

- [x] 1.1 Add GitHub Actions workflow definitions for the required CI baseline jobs
- [x] 1.2 Configure workflow triggers for pull requests and protected-branch updates covered by the CI baseline
- [x] 1.3 Decide whether CI should use a single workflow file with multiple jobs or separate workflow files for backend, frontend, and E2E reporting
- [x] 1.4 Configure backend CI execution to use the repository's documented PostgreSQL and Redis prerequisites
- [x] 1.5 Configure frontend CI execution to run `npm run type-check`, `npm run lint`, and `npm run test` with the repo-supported Node workflow
- [x] 1.6 Ensure required CI jobs report separately so backend, frontend static checks, and frontend tests fail independently

## 2. Backend Validation Gate

- [x] 2.1 Decide whether the initial backend CI baseline runs the full Django suite or an approved scoped variant
- [x] 2.2 Wire the supported backend Django test command into CI as a required validation step
- [x] 2.3 Fix or document any backend environment assumptions that prevent the CI test command from matching local-first execution
- [x] 2.4 Verify backend-impacting changes are covered by the required backend CI job contract

## 3. Frontend Validation Gate

- [x] 3.1 Wire `npm run type-check` into CI as a required frontend validation step
- [x] 3.2 Wire `npm run lint` into CI as a required frontend validation step
- [x] 3.3 Wire `npm run test` into CI as a required frontend validation step
- [x] 3.4 Verify frontend-impacting changes are covered by the required frontend CI job contract

## 4. E2E Phasing Policy

- [x] 4.1 Decide the initial required Playwright scope for CI promotion
- [x] 4.2 Classify existing Playwright scenarios into required, advisory, or deferred categories
- [x] 4.3 Configure CI so non-required Playwright scenarios can run without blocking the initial baseline rollout
- [x] 4.4 Document the initial required/advisory E2E scenario list and the promotion criteria for moving an advisory scenario into the required baseline

## 5. High-Value Coverage Gap Reduction

- [ ] 5.1 Identify the smallest missing backend or frontend test additions needed to protect core chat, workflow, or retrieval-backed flows
- [ ] 5.2 Implement the targeted high-value tests selected for the initial CI baseline
- [ ] 5.3 Confirm the added tests strengthen baseline confidence without expanding this change into a full coverage rewrite

## 6. Documentation and Developer Workflow Alignment

- [x] 6.1 Update README and/or DEVELOPMENT guidance so local validation steps match the CI baseline
- [x] 6.2 Document required environment prerequisites for reproducing backend and frontend CI failures locally
- [x] 6.3 Document the repository policy for required versus advisory validation signals

## 7. Validation and Rollout

- [x] 7.1 Run the full required backend and frontend validation commands locally before finalizing the change
- [x] 7.2 Verify the new CI workflows pass with the intended required baseline configuration
- [x] 7.3 Enable or document branch protection expectations for the required CI jobs
