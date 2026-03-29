## 1. Secret exposure exploration

- [x] 1.1 Review existing application API key backend serializers and list/create behavior
- [x] 1.2 Review frontend application API key dialog behavior for displaying and copying listed secret values

## 2. Minimal application API key masking slice

- [x] 2.1 Add backend tests proving create returns a full application API key once while list/read responses return a masked value
- [x] 2.2 Implement backend masking for application API key list/read responses using the existing system API key masking pattern
- [x] 2.3 Update the frontend application API key dialog to treat masked values as masked display-only secrets
- [x] 2.4 Run focused backend and frontend verification for the application API key flow

## 3. Follow-up redaction scope decision

- [x] 3.1 Evaluate whether email/password-like settings redaction belongs in this change or a follow-up
- [x] 3.2 Evaluate whether platform/provider secret redaction belongs in this change or a follow-up

## 4. Packaging and verification

- [x] 4.1 Run the full secret-hardening-related verification for the implemented slice
- [ ] 4.2 Package the change into atomic commits and create a PR
