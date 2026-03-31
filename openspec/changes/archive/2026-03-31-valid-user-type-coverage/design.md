## Context

`ValidSerializer.valid()` supports three configured CE types, but only `application` and `user` are safely reachable today. The `user` branch uses the same control flow as the already-covered application branch: exact-count allowance, wrong-count rejection, quota-exhausted rejection, and licensed bypass.

## Goals / Non-Goals

**Goals:**
- Verify `GET /admin/api/valid/user/2` reports success when the CE user count remains under the limit
- Verify the endpoint reports a CE validation failure for wrong-count and quota-exhausted user requests
- Verify a valid license bypasses the CE user-count limit

**Non-Goals:**
- No production fixes for the `dataset` / `knowledge` mismatch
- No changes to the existing application-path tests
- No expansion beyond the `user` branch of the `valid` endpoint

## Decisions

1. Extend the existing `test_valid_and_public_auth.py` module so application-path and user-path validation coverage stay together.
2. Patch cache and queryset count in the user happy-path and quota tests to keep the CE user-count branch deterministic.
3. Update the main spec by widening the CE validation scenarios from application-only to application-or-user, matching the implemented behavior under test.

## Risks / Trade-offs

- This slice intentionally leaves the dataset/knowledge mismatch alone so the diff remains test-only and does not mix in a production bug fix.
