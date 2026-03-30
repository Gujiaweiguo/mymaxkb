## Why

`ResourceMappingView` is currently untested. It sits behind a non-trivial permission gate and uses raw SQL paging through `native_page_search`, which makes it a high-risk blind spot despite being adjacent to recently completed shared-resource and permission-management slices.

## What Changes

- Add integration coverage for `ResourceMappingView`
- Verify a workspace-manage actor can page mappings successfully
- Verify an unauthorized actor receives 403
- Verify the endpoint returns an empty page when no mappings exist

## Capabilities

### Modified Capabilities

- `shared-resources`: verify resource relationship paging behavior and authorization at the API layer

## Impact

- Extends `apps/system_manage/test_integration.py`
- Adds end-to-end evidence for the raw-SQL-backed resource mapping API
