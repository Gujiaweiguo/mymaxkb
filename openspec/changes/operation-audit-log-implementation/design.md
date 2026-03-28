## Context

The operation audit log feature is already production-complete for recording and review. The backend has a `Log` model, a `@log()` decorator that records administrative operations, APIs for paginated listing, filtering, Excel export, and clean-time CRUD, plus a frontend page that exposes those capabilities. The major missing behavior is lifecycle enforcement: `OperateLogCleanTimeView` stores retention settings in `SystemSetting(type=LOG)`, but no scheduled cleanup job currently reads that value or deletes expired log rows.

There are already two scheduler patterns in the repo — `clean_chat_job.py` and `clean_debug_file_job.py` — that use APScheduler plus a Redis lock and batched deletes. The safest first slice is to follow that existing pattern for operation logs rather than introducing a new scheduling mechanism.

## Goals / Non-Goals

**Goals:**
- Complete the operation-log retention lifecycle by adding a scheduled cleanup job
- Reuse the existing `clean_time` system setting instead of introducing a new configuration model
- Add focused backend coverage proving only expired log rows are removed

**Non-Goals:**
- Rebuilding the audit log page, filters, or export UI
- Redesigning the `@log()` decorator in the first slice
- Introducing long-term archive/export storage for historical logs beyond current retention semantics

## Decisions

### 1. Implement cleanup as a scheduled APScheduler job

**Why:** the repo already uses APScheduler job modules with Redis locking for periodic cleanup tasks. Matching that pattern keeps operational behavior consistent and lowers implementation risk.

**Alternative considered:** trigger deletion lazily inside log list/read paths. Rejected because retention cleanup is a background lifecycle concern and should not add latency or side effects to read endpoints.

### 2. Use the existing `SettingType.LOG.clean_time` value as the sole retention source

**Why:** the admin UI and backend API already store and retrieve this value. Reusing it closes the current gap without changing the configuration surface.

**Alternative considered:** add a separate cleanup-specific config source. Rejected because it duplicates an existing setting and makes the retention model harder to reason about.

### 3. Start with focused cleanup tests in `test_log_management.py`

**Why:** log management tests already cover retrieval, export, and clean-time persistence. Adding cleanup coverage there keeps the audit-log lifecycle contract in one place.

**Alternative considered:** add a new job-specific test module under `common/job`. Rejected for the first slice because the behavior is tightly coupled to operation-log settings and model semantics already covered by log-management tests.

## Risks / Trade-offs

- **[Risk] Large deletions could hold locks or load the database** → **Mitigation:** follow existing batched-delete patterns from other cleanup jobs
- **[Risk] Missing or malformed clean-time settings could block cleanup** → **Mitigation:** fall back to the current default retention behavior already exposed by serializer logic
- **[Risk] Cleanup timing could race with active log writes** → **Mitigation:** delete by age threshold only and keep the selection criteria simple and idempotent

## Migration Plan

1. Add the operation-log cleanup job module using the existing scheduler pattern
2. Register it alongside the current cleanup jobs
3. Add backend tests proving expired logs are deleted and recent logs are retained
4. Run the targeted log-management tests before considering any broader audit-log enhancements

## Open Questions

- Should the next slice after cleanup focus on `@log()` decorator regression coverage or on expanding which operations are logged?
- Do operation logs need a future archive/export-before-delete path, or is bounded retention enough for community edition?
