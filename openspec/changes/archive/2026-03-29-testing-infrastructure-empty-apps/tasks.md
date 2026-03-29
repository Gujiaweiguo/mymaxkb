## Tasks

- [x] Write oss/tests.py - SSRF protection, audio types, MIME types (25 tests)
- [x] Write tools/tests.py - encryption, to_dict, RestrictedUnpickler (11 tests)
- [x] Write models_provider/tests.py - Status enum, providers, model params, unique constraint (16 tests)
- [x] Write trigger/tests.py - trigger setting validation, enums (31 tests)
- [x] Run all new tests and verify they pass (83/83 OK)

### Notes

- local_model is not in INSTALLED_APPS (separate service), tests skipped
- All tests are pure unit tests (no external service dependencies)
