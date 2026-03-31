## Context

`ValidSerializer.valid()` enforces community-edition limits when `license_is_valid` is false: it rejects requests whose count does not match the supported application allowance, rejects requests after the application quota is exhausted, and otherwise returns `True`. When `license_is_valid` is true, the serializer bypasses CE enforcement and returns `True` immediately.

## Goals / Non-Goals

**Goals:**
- Verify the endpoint reports a CE validation failure for a non-matching application count
- Verify the endpoint reports a CE validation failure when the application quota is exhausted
- Verify a valid license bypasses CE application-limit enforcement

**Non-Goals:**
- No production serializer or view changes
- No expansion into `knowledge` / `user` validation branches in this slice
- No changes to the public login-auth tests already covered in the same module

## Decisions

1. Extend the existing `test_valid_and_public_auth.py` module so the new CE enforcement assertions live beside the original allowance and authentication tests.
2. Use endpoint-level tests through `APIClient` to preserve the existing request/response contract coverage.
3. Patch cache and queryset count only for the quota-exhausted and licensed-bypass branches to keep the slice deterministic and narrow.

## Risks / Trade-offs

- This slice focuses on the stable application-path CE rules, leaving the mismatched `knowledge`/`dataset` mapping untouched to avoid forcing production changes in the same pass.
