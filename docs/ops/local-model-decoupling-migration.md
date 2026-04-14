# Built-in local_model Removal Migration Guide

## Overview

MaxKB no longer bundles or starts a built-in `local_model` service.

After this change:

- `local_model` is not a supported startup mode
- `MAXKB_ENABLE_LOCAL_MODEL` / `ENABLE_LOCAL_MODEL` are no longer used
- built-in local embedding and reranker execution are removed from the repository
- all local-model usage must come from external API providers such as Ollama, Xinference, vLLM, or other remote model services

## What operators need to change

1. Remove any obsolete local-model startup scripts or service units that call:
   - `python main.py dev local_model`
   - `python apps/manage.py start local_model`
2. Remove obsolete environment variables if present:
   - `MAXKB_ENABLE_LOCAL_MODEL`
   - `ENABLE_LOCAL_MODEL`
   - local-model-only host/port/protocol overrides from older deployments
3. Reconfigure any workflows that previously depended on the built-in local-model provider to use an external API provider instead.

## Legacy behavior

Persisted records using `provider='model_local_provider'` are not auto-migrated.

They now fail fast with an actionable backend error indicating that the provider is no longer supported and that an external API provider must be configured instead.

## Supported runtime commands

The supported `main.py` commands remain:

```bash
python main.py dev web
python main.py dev celery
python main.py start all
python main.py start web
python main.py start task
python main.py upgrade_db
python main.py collect_static
```

## Verification after upgrade

Use these checks after deployment:

```bash
python apps/manage.py check
cd ui && npm run type-check && npm run lint && npm run test
```

Then verify that model configuration UI only exposes supported external providers.

## Rollback

There is no runtime flag to re-enable the removed built-in `local_model` path.

If you must restore that behavior, the rollback is to deploy an older application version that still included the built-in local-model runtime.
