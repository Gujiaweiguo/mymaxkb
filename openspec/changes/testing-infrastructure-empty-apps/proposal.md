## Why

Five Django apps had empty test stubs (oss, tools, models_provider, trigger), contributing zero test coverage. The `testing-infrastructure` spec requires integration tests for API endpoints, unit tests for serializers/services, and E2E tests for critical flows.

## What Changes

- `apps/oss/tests.py`: 25 tests for SSRF protection (`is_private_ip`, `validate_url`), audio types, MIME types
- `apps/tools/tests.py`: 11 tests for `encryption()`, `to_dict()`, `RestrictedUnpickler`, `ALLOWED_CLASSES`
- `apps/models_provider/tests.py`: 16 tests for `Status` enum, `ProviderConstants`, `get_model_default_params()`, Model unique constraint
- `apps/trigger/tests.py`: 31 tests for trigger setting validation (time format, array, range, daily/weekly/monthly/interval/cron, event)
- `apps/local_model/tests.py`: unchanged (not in INSTALLED_APPS, cannot be tested via Django test runner)

## Impact

- Test count: +83 tests (from ~252 to ~335)
- Apps with zero coverage: reduced from 5 to 2 (local_model excluded, oss/tools/models_provider/trigger now have tests)
- No production code changes
