## 1. Operation-log planning

- [x] 1.1 Inventory existing operation-log collection, filtering, export, and retention surfaces against the `operation-audit-log` spec
- [x] 1.2 Define the minimum administrative events and filter dimensions required for parity in the first implementation pass
- [x] 1.3 Confirm how retention configuration should be represented and validated in community edition

## 2. System API planning

- [x] 2.1 Inventory existing system API key and privileged access surfaces against the `system-api-access` spec
- [x] 2.2 Define the required lifecycle operations for system API credentials in the first implementation pass
- [x] 2.3 Confirm which privileged endpoints and system-profile surfaces are in scope for the first parity release

## 3. Implementation breakdown

- [x] 3.1 Break backend implementation into audit capture, audit retrieval/export, and system API credential governance workstreams
- [x] 3.2 Break frontend implementation into operation-log management and system API key management workstreams
- [x] 3.3 Define verification scenarios for log visibility, export behavior, credential validity, and credential denial cases

## 4. Cross-change handoff

- [x] 4.1 Reuse the authority model from earlier identity, workspace, and sharing changes instead of redefining it
- [x] 4.2 Record any documentation or operational rollout requirements that depend on final API-key behavior
- [x] 4.3 Confirm that third-party channel integration remains outside this change
