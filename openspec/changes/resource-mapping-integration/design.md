## Context

`ResourceMappingView` is a read-only endpoint at `workspace/<workspace_id>/resource_mapping/<resource>/<resource_id>/<page>/<size>`. It relies on `ResourceMappingSerializer.page()`, which delegates to `native_page_search` over `list_resource_mapping.sql`, and it is guarded by a multi-branch permission decorator. There are no tests covering this view today.

## Goals / Non-Goals

**Goals:**
- Add integration tests for happy-path paging with a workspace-manage actor
- Add denied-path coverage for a regular unauthorized user
- Add empty-page coverage for an unmapped target resource

**Non-Goals:**
- No production view/serializer/SQL changes
- No exhaustive filter matrix (`resource_name`, `user_name`, `source_type`) in this first slice
- No write-path coverage because this endpoint is GET-only

## Decisions

1. Use the CE `default` workspace so `get_auth()` resolves workspace roles consistently.
2. Use an `ADMIN` actor with `get_auth()` for the happy path because CE `get_auth()` does not resolve workspace roles from `WorkspaceMember`; instead it synthesizes `WORKSPACE_MANAGE:/WORKSPACE/default` for ADMIN on the default workspace.
3. Use `Application -> Knowledge` resource mapping rows because the SQL CTE explicitly unions `application` and `knowledge` as source data.
4. Keep the initial slice to three tests: success, denied, and empty page.

## Risks / Trade-offs

- Raw SQL output shape is less ergonomic than serializer-only code, so assertions should stay focused on stable fields (`total`, `records`, `source_type`, `target_id`).
- The CE default-workspace assumption is intentional and aligned with recent permission slices.
