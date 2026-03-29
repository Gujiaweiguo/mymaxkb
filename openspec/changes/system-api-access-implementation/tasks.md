## 1. System API access exploration

- [x] 1.1 Review the existing system API key model, auth handler, middleware, and management views
- [x] 1.2 Identify the smallest missing runtime seam in the current system API access model

## 2. Minimal cross-domain enforcement slice

- [x] 2.1 Add backend tests for allowed and denied cross-domain behavior on valid system API keys
- [x] 2.2 Extend the cross-domain middleware to apply configured policy for `system-` API keys
- [x] 2.3 Run narrow system API key backend tests and fix any enforcement gaps discovered

## 3. Follow-up scope decision

- [x] 3.1 Evaluate whether broader endpoint authorization for system API keys belongs in this change or a follow-up
- [x] 3.2 Evaluate whether a dedicated system API key page is necessary or the existing dialog is sufficient

## 4. Packaging and verification

- [x] 4.1 Run full system API access-related backend tests
- [ ] 4.2 Package the change into atomic commits and create a PR
