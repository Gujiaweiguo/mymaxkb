## 1. Scope the regression baseline

- [x] 1.1 Confirm the representative backend paths for this change: `apps/application/flow/common.py` `Workflow`, `apps/chat/serializers/chat_record.py` `VoteSerializer.vote()`, and `apps/knowledge/models/knowledge.py` `Status`
- [x] 1.2 Confirm the representative API-backed paths for this change: application publish flow in `apps/application/test_integration.py`, chat conversation/source-routing coverage in `apps/chat/test_integration.py`, and workspace knowledge CRUD coverage in `apps/knowledge/test_integration.py`
- [x] 1.3 Document the frontend and Playwright baseline buckets for this change: required = existing Vitest suite; advisory = `ui/e2e/login.spec.ts`, `ui/e2e/entry-routing.spec.ts`, `application.spec.ts`, `workspace.spec.ts`, `user-management.spec.ts`, `knowledge.spec.ts`; deferred = `chat.spec.ts`

## 2. Add backend critical-path regression coverage

- [x] 2.1 Add or upgrade Django tests for `apps/application/flow/common.py` `Workflow` graph construction and traversal behavior, preferably in a dedicated application test module
- [x] 2.2 Add or upgrade Django tests for `apps/chat/serializers/chat_record.py` `VoteSerializer.vote()` state transitions, including rejection and cancel paths
- [x] 2.3 Add or upgrade Django tests for `apps/knowledge/models/knowledge.py` `Status` encode/decode and mutation behavior
- [x] 2.4 Verify the selected backend regression paths pass through the repository-supported Django test workflow

## 3. Add focused API integration coverage

- [x] 3.1 Deepen workflow-related integration coverage around the publish application path in `apps/application/test_integration.py`, including publish state and versioning assertions
- [x] 3.2 Add or upgrade chat-related integration coverage in `apps/chat/test_integration.py` for conversation editing and source-routing behavior
- [x] 3.3 Deepen knowledge-related integration coverage in `apps/knowledge/test_integration.py` for workspace-scoped knowledge create/read/update/delete behavior
- [x] 3.4 Verify the scoped integration paths use meaningful request/response assertions rather than nominal test presence

## 4. Align frontend, E2E, and CI contracts

- [x] 4.1 Update repository testing guidance to document the stable required frontend baseline: `npm run type-check`, `npm run lint`, `npm run test`, plus the advisory Playwright classification used by the repository testing contract
- [x] 4.2 Document that `application.spec.ts`, `workspace.spec.ts`, `user-management.spec.ts`, and `knowledge.spec.ts` remain advisory, while `chat.spec.ts` remains deferred because it depends on external credentials and remote-backed behavior
- [x] 4.3 Update CI-facing validation documentation or workflow configuration so required checks match the scoped baseline without accidentally promoting advisory or deferred Playwright scenarios into merge-blocking gates
- [x] 4.4 Update `AGENTS.md` and any contributor-facing testing references so local reproduction commands and prerequisites match `README.md`, `DEVELOPMENT.md`, and `.github/workflows/ci.yml`

## 5. Validate the scoped baseline

- [x] 5.1 Run the repository-supported backend test command covering the scoped regression additions
- [x] 5.2 Run the required frontend validation commands for the scoped baseline
- [x] 5.3 Run the required safety checks and any advisory E2E checks intentionally included in the scoped baseline review
- [x] 5.4 Record any remaining follow-up gaps that are intentionally left outside this first regression-coverage change
