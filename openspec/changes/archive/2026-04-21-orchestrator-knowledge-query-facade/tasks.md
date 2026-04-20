## Wave 1: Contract, Auth/Session, Execution, Response Shaping, Preview

### Task 1: Freeze the external Orchestrator contract and route the new facade

- [x] 1.1 Add `POST /api/knowledge/query` route in `apps/maxkb/urls/web.py` or a dedicated urls module, following the pattern at lines 32-50.
- [x] 1.2 Create facade view class with `@csrf_exempt` or DRF `APIView`, no authentication_classes set at view level (auth handled in Task 2).
- [x] 1.3 Define request serializer accepting: `question` (str, required), `session_id` (str, optional), `request_id` (str, optional), `trace_id` (str, optional), `context` (object, optional), `params` (object, optional with `_param_preview`, `top_n`, `similarity`, `kb_scope`).
- [x] 1.4 Define normal-mode response serializer always including: `text`, `references` (list), `suggestions` (list), `cards` (list), `meta` (object with `chat_id`, `tokens_used`, `hit_paragraph_count`). Use `references: []`, `suggestions: []`, `cards: []` as stable defaults.
- [x] 1.5 Define preview-mode response serializer returning only `param_schema`.
- [x] 1.6 Define structured error serializer with `error_code` and `message`. Standardize error codes: `INVALID_REQUEST`, `UNAUTHORIZED`, `SESSION_MISMATCH`, `KNOWLEDGE_SCOPE_INVALID`, `INTERNAL_ERROR`.
- [x] 1.7 Write TDD tests: `OrchestratorQueryContractTests.test_query_route_registered`, `test_invalid_request_returns_structured_error`, `test_preview_path_excludes_answer_fields`, `test_error_codes_are_stable_set`.
- [x] 1.8 Verify: `.venv/bin/python apps/manage.py test apps.knowledge.tests.OrchestratorQueryContractTests --verbosity=1 --noinput` passes.

**Depends on:** (none)
**Blocks:** 2, 3, 5, 6, 7, 8
**Commit:** `feat(knowledge): add orchestrator facade contract`

---

### Task 2: Implement Orchestrator auth binding and Redis-backed session continuity

- [x] 2.1 Add bearer-token extraction from `Authorization` header, validate against `ApplicationApiKey.secret_key`, resolve bound application (pattern: `apps/chat/views/mcp.py:21-22`).
- [x] 2.2 Reject invalid/disabled/revoked API keys with `UNAUTHORIZED` structured error.
- [x] 2.3 Create session-binding service: cache `session_id -> {chat_id, application_id, api_key_fingerprint, user_binding_hash, created_at, last_seen_at}` in Redis with 30-minute TTL.
- [x] 2.4 Compute `user_binding_hash` from `context.user_id`, `context.role_code`, `context.project_id`, `context.source`, normalized `kb_scope`.
- [x] 2.5 First normal-mode request with new `session_id`: create internal chat via existing `OpenChatSerializers` primitives, store binding.
- [x] 2.6 Subsequent request with same `session_id` + same binding: reuse same internal `chat_id`, refresh TTL.
- [x] 2.7 Reject session reuse when API key, application, or user_binding_hash differs → return `SESSION_MISMATCH` error.
- [x] 2.8 Preview-mode requests must NOT create or refresh session cache.
- [x] 2.9 Write TDD tests: `OrchestratorQuerySessionTests.test_same_session_reuses_chat_binding`, `test_session_reuse_across_different_binding_rejected`, `test_invalid_api_key_returns_unauthorized`, `test_preview_does_not_mutate_session`.
- [x] 2.10 Verify: `.venv/bin/python apps/manage.py test apps.knowledge.tests.OrchestratorQuerySessionTests --verbosity=1 --noinput` passes.

**Depends on:** 1
**Blocks:** 3, 8
**Commit:** `feat(knowledge): add orchestrator session binding`

---

### Task 3: Build the one-shot execution adapter over the existing SIMPLE chat pipeline

- [x] 3.1 Implement facade adapter that converts Orchestrator request into existing `ChatSerializers.chat_simple()` execution path (pattern: `apps/chat/serializers/chat.py:504-562`).
- [x] 3.2 For new `session_id`: create internal chat; for follow-up: reopen/reuse internal `chat_id`.
- [x] 3.3 Map `params.top_n` and `params.similarity` into pipeline params, defaulting from `application.knowledge_setting` when missing (pattern: `apps/application/serializers/common.py:220-258`).
- [x] 3.4 Map `context.kb_scope` into `knowledge_id_list`, restricted to application's mapped knowledge resources via `ResourceMapping` (pattern: `apps/application/serializers/common.py:152-165`). Reject invalid values with `KNOWLEDGE_SCOPE_INVALID`.
- [x] 3.5 When retrieval yields no hits, follow existing `no_references_setting` behavior; still return valid normal contract with `references: []`, `meta.hit_paragraph_count: 0`.
- [x] 3.6 Write TDD tests: `OrchestratorQueryExecutionTests.test_query_returns_answer_via_simple_pipeline`, `test_invalid_kb_scope_returns_structured_error`, `test_no_hits_returns_valid_normal_contract`.
- [ ] 3.7 Verify: `.venv/bin/python apps/manage.py test apps.knowledge.tests.OrchestratorQueryExecutionTests --verbosity=1 --noinput` passes.

**Depends on:** 1, 2
**Blocks:** 4, 8
**Commit:** `feat(knowledge): add orchestrator query execution adapter`

---

### Task 4: Shape trustworthy references, meta, suggestions, and cards from the answer path

- [ ] 4.1 Extract references from actual retrieval artifacts produced by `BaseSearchDatasetStep` (pattern: `base_search_dataset_step.py:76-150`). Each reference: at minimum `title` + `snippet`; add `url`, `confidence`, `document_id`, `paragraph_id` when available.
- [ ] 4.2 Populate `meta` deterministically: `chat_id`, `tokens_used` (from usage data or deterministic fallback), `hit_paragraph_count` (actual count of returned paragraph hits).
- [ ] 4.3 `cards` always present as `[]` in v1.
- [ ] 4.4 Implement suggestion generation: retrieval-grounded answer-context strategy; fallback to `[]` when relevance quality insufficient.
- [ ] 4.5 Write TDD tests: `OrchestratorQueryResponseTests.test_response_includes_grounded_references_and_meta`, `test_low_confidence_returns_empty_suggestions_not_templates`, `test_cards_always_empty_array_v1`.
- [ ] 4.6 Verify: `.venv/bin/python apps/manage.py test apps.knowledge.tests.OrchestratorQueryResponseTests --verbosity=1 --noinput` passes.

**Depends on:** 3
**Blocks:** 8
**Parallel with:** 5
**Commit:** `feat(knowledge): shape references suggestions and meta`

---

### Task 5: Add `_param_preview` schema generation with strict no-side-effect behavior

- [ ] 5.1 Implement preview-mode branch: `params._param_preview=true` returns only `param_schema`, excludes all normal answer fields.
- [ ] 5.2 Generate `kb_scope` control with `options` from application's mapped knowledge resources (pattern: `apps/application/serializers/common.py:152-165`).
- [ ] 5.3 Generate `top_n` control with defaults, min=1, max=20, from application `knowledge_setting.top_n`.
- [ ] 5.4 Generate `similarity` control with defaults, min=0, max=1, step=0.05, from application `knowledge_setting.similarity`.
- [ ] 5.5 Preview mode authenticates and resolves application but does NOT create chat, mutate Redis session, invoke LLM, or consume conversation history.
- [ ] 5.6 Write TDD tests: `OrchestratorParamPreviewTests.test_preview_returns_param_schema_only`, `test_preview_mode_does_not_create_chat_or_cache_binding`, `test_kb_scope_options_match_application_knowledge`.
- [ ] 5.7 Verify: `.venv/bin/python apps/manage.py test apps.knowledge.tests.OrchestratorParamPreviewTests --verbosity=1 --noinput` passes.

**Depends on:** 1
**Blocks:** 6, 7, 8
**Parallel with:** 4
**Commit:** `feat(knowledge): add orchestrator param preview`

---

## Wave 2: Admin Integration, UI, Hardening

### Task 6: Expose Orchestrator integration parameters from the existing application integration backend surface

- [ ] 6.1 Add admin endpoint that returns Orchestrator integration payload: `endpoint_url` (base path `/api/knowledge`), `auth_token` (from `ApplicationApiKey`), `default_params` (`kb_scope`, `top_n`, `similarity`).
- [ ] 6.2 If no active API key exists, generate one via existing `ApplicationKeySerializer.generate()` path and return the new secret.
- [ ] 6.3 `default_params` must be consistent with preview-schema defaults and application knowledge mapping.
- [ ] 6.4 Place the endpoint within the existing application admin URL surface (pattern: `apps/application/views/application_api_key.py`).
- [ ] 6.5 Write TDD tests: `OrchestratorIntegrationConfigTests.test_returns_endpoint_token_and_default_params`, `test_missing_api_key_auto_generates_and_returns`.
- [ ] 6.6 Verify: `.venv/bin/python apps/manage.py test apps.application.tests.OrchestratorIntegrationConfigTests --verbosity=1 --noinput` passes.

**Depends on:** 1, 5
**Blocks:** 7, 8
**Parallel with:** (none in this wave initially; can run alongside 4 if Wave 1 overlap)
**Commit:** `feat(application): expose orchestrator integration config`

---

### Task 7: Add admin-side UI output and copy flow on the existing application integration/API-key surface

- [ ] 7.1 Extend the existing application overview/integration UI to display Orchestrator integration payload from Task 6 backend.
- [ ] 7.2 Add copy action for the full integration JSON payload (pattern: existing API key dialog copy at `ui/src/views/application-overview/component/APIKeyDialog.vue` and test at `application-overview-api-key-dialog.test.ts`).
- [ ] 7.3 Preserve existing masked/unmasked API key copy behavior unchanged.
- [ ] 7.4 Write Vitest test: `application-overview-orchestrator-config.test.ts` asserting rendered payload and copy invocation.
- [ ] 7.5 Verify: `cd ui && npm run type-check && npm run lint && npm run test` passes including existing `application-overview-api-key-dialog.test.ts`.

**Depends on:** 5, 6
**Blocks:** 8
**Commit:** `feat(ui): add orchestrator integration output panel`

---

### Task 8: Close the loop with end-to-end contract hardening and regression coverage

- [ ] 8.1 Add backend regression tests: success path, preview isolation, invalid request, invalid API key, session mismatch, invalid kb_scope, grounded references, conservative suggestions fallback, admin integration output.
- [ ] 8.2 Add frontend regression tests: Orchestrator config rendering/copy, existing API key behavior preserved.
- [ ] 8.3 Ensure all new tests use narrow deterministic fixtures, no external model provider dependencies. Use targeted mocking around model invocation.
- [ ] 8.4 Run full backend regression: `.venv/bin/python apps/manage.py test apps.application apps.chat apps.knowledge --verbosity=1 --noinput` exits 0.
- [ ] 8.5 Run full frontend regression: `cd ui && npm run type-check && npm run lint && npm run test` exits 0.

**Depends on:** 1, 2, 3, 4, 5, 6, 7
**Commit:** `test(orchestrator): harden query facade regressions`
