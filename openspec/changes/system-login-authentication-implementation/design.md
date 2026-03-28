## Context

The repository already contains a working administrative login stack. Backend LOCAL sign-in is implemented through `LoginSerializer.login()` and exposed at `POST /admin/api/user/login`. Community edition currently limits supported login methods to `LOCAL` through login-auth settings, while the frontend login page has a broader multi-method UI that filters rendered methods from server-provided configuration.

What is missing is not a blank implementation, but a completed OpenSpec-driven implementation slice that verifies the current authentication contract and then expands safely from the existing seams. The current frontend login test file is placeholder-only, while backend login tests cover only basic request validation and loose API smoke cases.

## Goals / Non-Goals

**Goals:**
- Capture `system-login-authentication` as an active implementation change
- Start with a small backend-first slice that verifies the current LOCAL admin login contract
- Sequence the next work so lockout, captcha, and frontend method visibility are added after the core backend login path is covered

**Non-Goals:**
- Rebuilding the full frontend login page in the first slice
- Introducing new authentication providers or changing PE/EE-only login methods
- Reworking token formats, encryption strategy, or user model design unless tests reveal a real defect

## Decisions

### 1. Start with backend LOCAL login tests before frontend login UI tests

**Why:** `LoginSerializer.login()` is the narrowest stable seam for the community-edition admin sign-in contract. It covers success and denial behavior without the complexity of the large Vue login page and its many non-CE auth modes.

**Alternative considered:** Start from `ui/src/views/login/index.vue`. Rejected because that page supports many methods and has placeholder tests today, so the setup cost is much higher for the first slice.

### 2. Treat lockout and captcha as follow-up slices, not part of the first implementation step

**Why:** The spec is broad enough to include them, but the minimal verifiable path is first proving that enabled LOCAL sign-in succeeds and unsupported/invalid attempts fail. Lockout and captcha build on top of that baseline.

**Alternative considered:** Implement all backend login behaviors in one pass. Rejected because it widens scope and increases the chance of mixing infrastructure issues with core contract testing.

### 3. Keep frontend work focused on method visibility once backend contract is covered

**Why:** The spec explicitly requires that disabled authentication methods are not available. The frontend already filters methods from public auth settings, so the next UI slice should verify rendering behavior rather than redesign the login page.

**Alternative considered:** Add end-to-end login UI coverage immediately. Rejected because a focused component-level slice is cheaper and aligns with the current repo’s sparse frontend test setup.

## Risks / Trade-offs

- **[Risk] Existing backend login tests may overlap with the new serializer-focused slice** → **Mitigation:** add only contract tests that close the current gaps: success, wrong password, and disabled user
- **[Risk] Frontend login page complexity may slow later slices** → **Mitigation:** defer frontend work until the backend contract is verified and then target visibility logic only
- **[Risk] Community-edition and paid-edition login modes may be conflated** → **Mitigation:** explicitly scope the first slice to CE-supported LOCAL admin login behavior

## Migration Plan

1. Add backend tests for the current LOCAL admin login contract
2. Verify the existing login API and serializer paths continue to pass
3. Add lockout/captcha tests as the next backend slice if needed
4. Add frontend login method visibility tests after backend coverage is stable

## Open Questions

- Should the next slice after LOCAL login focus on lockout first or captcha first?
- Is `require_password_change` enforcement part of this change’s intended contract, or should it be tracked separately as a password-lifecycle slice?
