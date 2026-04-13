## 1. Wave 1 — Foundation and Legacy Contract

- [x] 1.1 RLM-001 Extract shared embedding/reranker abstractions out of `local_model_provider`
  - Depends on: None
  - Risk: High
  - Input:
    - `apps/models_provider/impl/local_model_provider/model/embedding/`
    - `apps/models_provider/impl/local_model_provider/model/reranker/`
    - `apps/models_provider/impl/ollama_model_provider/credential/embedding.py`
    - `apps/models_provider/impl/xinference_model_provider/credential/embedding.py`
  - Output:
    - Shared embedding/reranker helper classes moved to a provider-neutral module path under `apps/models_provider/`
    - Ollama/Xinference references updated to import only from provider-neutral locations
    - No external provider imports from `local_model_provider`
  - Acceptance:
    - Repository search returns zero production imports from external providers into `local_model_provider`:
      `grep -R "local_model_provider" apps/models_provider/impl/ollama_model_provider apps/models_provider/impl/xinference_model_provider`
    - `python apps/manage.py check` succeeds after extraction.
    - Evidence saved under `.sisyphus/evidence/remove-local-model-api-only/task-RLM-001-extraction.txt`.
  - Rollback: Revert only the abstraction relocation commit(s). Confirm Ollama/Xinference imports point back to pre-change modules before attempting any later-task rollback.

- [x] 1.2 RLM-002 Define and implement legacy-state fail-fast behavior for removed local-model provider
  - Depends on: None
  - Risk: High
  - Input:
    - Persisted `Model` rows and config values that may reference `provider='model_local_provider'`
    - Existing credential/decryption paths under `apps/local_model/`
    - Provider resolution paths in `apps/models_provider/tools.py`
  - Output:
    - Explicit unsupported-provider handling for legacy local-model references
    - Deterministic error message/code path documented in tests or assertions
    - Defined upgrade behavior for old environments after deploy
  - Acceptance:
    - A targeted backend test proves legacy `model_local_provider` state fails with the planned actionable error.
    - Repository docs/comments for upgrade behavior are updated where the runtime contract is defined.
    - Evidence saved under `.sisyphus/evidence/remove-local-model-api-only/task-RLM-002-legacy-failfast.txt`.
  - Rollback: Revert the explicit fail-fast behavior change only. Restore previous provider resolution behavior if later tasks are not yet applied.

## 2. Wave 2 — Backend Hard Removal

- [x] 2.1 RLM-003 Remove `LocalModelProvider` from backend provider registry and provider resolution surfaces
  - Depends on: RLM-001
  - Risk: High
  - Input:
    - `apps/models_provider/constants/model_provider_constants.py`
    - `apps/models_provider/tools.py`
    - any provider metadata helpers referencing local-model provider identity
  - Output:
    - No provider registry entry for built-in local model
    - No backend provider-resolution path that offers or expects `model_local_provider`
  - Acceptance:
    - Repository search returns zero production references to `LocalModelProvider` and `model_local_provider` in backend provider registry code.
    - `python apps/manage.py check` succeeds.
    - Evidence saved under `.sisyphus/evidence/remove-local-model-api-only/task-RLM-003-provider-registry.txt`.
  - Rollback: Restore registry entry and imports in a single revert. Re-run `python apps/manage.py check` before resuming execution.

- [x] 2.2 RLM-004 Remove built-in `local_model` startup/service/settings/URL/WSGI branches
  - Depends on: RLM-001, RLM-002
  - Risk: High
  - Input:
    - `main.py`
    - `apps/common/management/commands/services/command.py`
    - `apps/common/management/commands/services/services/local_model.py`
    - `apps/common/management/commands/services/services/__init__.py`
    - `apps/maxkb/settings/base/__init__.py`
    - `apps/maxkb/settings/auth/__init__.py`
    - `apps/maxkb/urls/__init__.py`
    - `apps/maxkb/wsgi/__init__.py`
    - any `model.py` variants used only for `SERVER_NAME == 'local_model'`
  - Output:
    - No supported `local_model` startup mode
    - No `SERVER_NAME == 'local_model'` branching in production runtime paths
    - No built-in `local_model` route inclusion
  - Acceptance:
    - Repository search returns zero production matches for `SERVER_NAME == 'local_model'` and zero startup/service references to `local_model` mode.
    - `python apps/manage.py check` succeeds in supported profile.
    - Supported startup commands remain documented and valid.
    - Evidence saved under `.sisyphus/evidence/remove-local-model-api-only/task-RLM-004-runtime-removal.txt`.
  - Rollback: Restore startup/service/settings branch files together as one atomic revert boundary. Confirm supported startup commands still run before retrying removal.

- [x] 2.3 RLM-005 Remove backend `apps/local_model/` ownership and re-home any still-required shared data/utilities
  - Depends on: RLM-002
  - Risk: High
  - Input:
    - `apps/local_model/` app models, serializers, views, urls, migrations, RSA utilities
    - all backend imports pointing into `apps/local_model/`
  - Output:
    - No runtime dependency on `apps/local_model/`
    - Any still-needed shared ORM/utilities relocated to stable non-local ownership
    - `local_model` removed from Django app/runtime surfaces
  - Acceptance:
    - Repository search returns zero production imports from non-test code into `apps/local_model`.
    - `python apps/manage.py check` succeeds without `local_model` app participation.
    - Evidence saved under `.sisyphus/evidence/remove-local-model-api-only/task-RLM-005-app-removal.txt`.
  - Rollback: Restore relocated shared assets first, then restore deleted `apps/local_model/` files if needed. Do not partially roll back model ownership without restoring corresponding imports.

## 3. Wave 3 — Frontend and Dependency Cleanup

- [x] 3.1 RLM-006 Remove frontend exposure of built-in local-model provider and update UX for external-only provider model
  - Depends on: RLM-002, RLM-004
  - Risk: Medium
  - Input:
    - `ui/src/components/dynamics-form/items/model/provider-data.ts`
    - `ui/src/views/model/component/Provider.vue`
    - any other UI copy or grouping logic exposing local built-in provider
  - Output:
    - No local built-in provider in add-model UI or provider grouping
    - UX copy reflects external provider-only support
  - Acceptance:
    - Repository search returns zero production frontend references to `model_local_provider`.
    - `cd ui && npm run type-check && npm run lint && npm run test` succeeds.
    - Evidence saved under `.sisyphus/evidence/remove-local-model-api-only/task-RLM-006-frontend.txt`.
  - Rollback: Revert frontend provider metadata/grouping changes as a single unit. Re-run frontend quality gates before continuing.

- [x] 3.2 RLM-007 Remove built-in torch/transformers/sentence-transformers dependency ownership and local-model installer residue
  - Depends on: RLM-003, RLM-004, RLM-005
  - Risk: High
  - Input:
    - `pyproject.toml`
    - local-model-only installer scripts and HF-specific bootstrap residue
    - any environment/path assumptions such as `HF_HOME` that exist solely for removed runtime
  - Output:
    - Main app dependency manifest no longer pins built-in local inference stack unless still required by surviving external-provider integrations
    - No local-model-only installer/bootstrap code remains
  - Acceptance:
    - Repository search proves no remaining production import path requires built-in torch inference.
    - Dependency manifest no longer includes built-in local-model runtime dependencies removed by this plan.
    - `python apps/manage.py check` and `cd ui && npm run type-check && npm run lint && npm run test` succeed in the resulting environment.
    - Evidence saved under `.sisyphus/evidence/remove-local-model-api-only/task-RLM-007-dependencies.txt`.
  - Rollback: Restore dependency manifest and any deleted installer/bootstrap files in the same rollback step. Reinstall environment from restored manifest before running validation.

- [x] 3.3 RLM-008 Implement upgrade-path safeguards and repository-wide reference audit for removed local-model concept
  - Depends on: RLM-004, RLM-005, RLM-006
  - Risk: Medium
  - Input:
    - all remaining references to local-model provider IDs, env keys, routes, docs, and upgrade-sensitive runtime messages
  - Output:
    - Explicit upgrade notes or runtime messages for unsupported legacy state
    - Repository-wide audit proving the concept is removed from production surfaces
  - Acceptance:
    - Zero unexpected production matches remain for: `model_local_provider`, `LocalModelProvider`, `SERVER_NAME == 'local_model'`, `MAXKB_ENABLE_LOCAL_MODEL`, built-in local-model service names.
    - Legacy local-model state triggers the defined fail-fast behavior in automated verification.
    - Evidence saved under `.sisyphus/evidence/remove-local-model-api-only/task-RLM-008-audit.txt`.
  - Rollback: Restore removed upgrade notes/runtime messages if final audit reveals unsupported operator ambiguity. Re-run audit before moving forward.

## 4. Wave 4 — Integrated Verification

- [x] 4.1 RLM-009 Execute integrated backend/frontend verification and rollback rehearsal at task-boundary level
  - Depends on: RLM-007, RLM-008
  - Risk: Medium
  - Input:
    - all completed code/config/test changes from RLM-001 through RLM-008
  - Output:
    - Verified supported runtime
    - Verified unsupported legacy behavior
    - Verified rollback boundaries documented per task cluster
  - Acceptance:
    - `python apps/manage.py check` succeeds.
    - `cd ui && npm run type-check && npm run lint && npm run test` succeeds.
    - Final symbol-audit evidence confirms removal targets are absent from production code.
    - Evidence saved under `.sisyphus/evidence/remove-local-model-api-only/task-RLM-009-integration.txt`.
  - Rollback: Roll back by task cluster in reverse dependency order: `RLM-008/009 → RLM-007 → RLM-006 → RLM-004/005 → RLM-003 → RLM-002 → RLM-001`. After each rollback boundary, rerun the nearest relevant verification command before further rollback.
