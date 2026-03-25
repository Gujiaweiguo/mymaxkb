## 1. Integration scope definition

- [x] 1.1 Inventory the existing third-party channel surfaces already visible in application access and authentication-related UI
- [x] 1.2 Decide which external channels are mandatory for the first community-edition implementation pass
- [x] 1.3 Define the minimum readiness criteria for a configured integration to be considered usable

## 2. Feishu knowledge-source planning

- [x] 2.1 Map the existing Feishu/Lark document import surface against the `feishu-document-knowledge-sync` spec
- [x] 2.2 Define the first-pass import and synchronization behaviors required for Feishu-backed knowledge sources
- [x] 2.3 Identify the connector state, error, and resynchronization cases that implementation must handle

## 3. Implementation breakdown

- [x] 3.1 Break backend implementation into provider configuration, callback handling, and connector execution workstreams
- [x] 3.2 Break frontend implementation into channel-configuration and Feishu knowledge-source management workstreams
- [x] 3.3 Define verification scenarios for configured, partially configured, and unusable integration states

## 4. Cross-change handoff

- [x] 4.1 Reuse identity and delegated-access prerequisites from earlier changes instead of redefining them
- [x] 4.2 Record any configuration or credential-storage assumptions that later operational documentation must include
- [x] 4.3 Confirm that audit logging and system API governance remain outside this change

## 5. Execution slices

- [x] 5.1 Implement provider readiness backend contracts for system auth, chat-user auth, and application platform configuration using existing storage
- [x] 5.2 Implement readiness-aware UI states for WeCom, DingTalk, and Lark across existing auth and application access surfaces
- [x] 5.3 Verify the provider readiness slice with targeted Django tests, `manage.py check`, changed-file diagnostics, and repo-wide frontend signal review
- [x] 5.4 Implement workspace-only Feishu/Lark knowledge create, folder browse, and selected-document import backend contracts
- [x] 5.5 Verify the Feishu/Lark import-first slice with targeted Django tests and `manage.py check`
- [x] 5.6 Bind Lark folder browse and selected-document import to the saved knowledge root token instead of accepting arbitrary folder traversal
- [x] 5.7 Return per-item import outcomes for Lark import-first execution so manual retry visibility improves without implying sync
- [x] 5.8 Follow Lark folder-list pagination so large root trees remain fully browsable and importable within the saved subtree

### Closeout notes

- The verified first-pass Lark backend contract is workspace-only knowledge create/update, folder browse, and selected `docx` import. It does not imply sync, webhook refresh, delta sync, or automated retry.
- Closeout verification for the import-first slice included targeted Django tests (`knowledge.test_lark_import`), `apps/manage.py check`, and Oracle review after fixing credential leakage, truthful import-type support, and `allow_download` preservation.
- The next verified follow-up slice bound Lark browse/import to the saved `folder_token` subtree and added per-item `created` / `skipped` / `failed` outcomes so manual retry visibility improved without implying sync.
- The latest verified follow-up slice added Lark folder-list pagination support so large folders and subtrees are fully traversed during browse/import validation within the same import-first boundary.
