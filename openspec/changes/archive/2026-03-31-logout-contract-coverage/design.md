## Context

`apps/users/views/login.py:Logout` removes the current token from the cache using the bearer token extracted from the request header, then returns `result.success(True)`. Existing tests covered login success and login failures, but not the logout contract or the token invalidation side effect.

## Goals / Non-Goals

**Goals:**
- Verify authenticated logout returns a success envelope
- Verify logout deletes the cached token entry for the current bearer token
- Verify unauthenticated logout returns HTTP 401

**Non-Goals:**
- No production changes to token handling
- No assertions about downstream reuse of an invalidated token beyond cache deletion
- No expansion into captcha or password-reset flows

## Decisions

1. Extend `LoginContractIntegrationTests` so login and logout remain in the same contract-focused test class.
2. Use a real login request to obtain the bearer token rather than `force_authenticate`, because the logout view reads the token from the raw `Authorization` header.
3. Assert both the success envelope and the cache side effect to keep the slice grounded in the endpoint’s actual behavior.

## Risks / Trade-offs

- This slice verifies token invalidation at the cache layer, which is the stable behavior directly implemented by the view today.
