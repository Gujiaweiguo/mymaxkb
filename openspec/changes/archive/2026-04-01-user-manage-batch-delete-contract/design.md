## Context

`UserManage.BatchDelete.post()` delegates to `UserManageSerializer.BatchDelete.batch_delete()`, which rejects empty ID lists with `AppApiException(1004, "User IDs cannot be empty")` and otherwise deletes all listed users except the built-in admin. Existing coverage only verified that non-admin users receive 403 for this endpoint, leaving the success and validation branches untested.

## Goals / Non-Goals

**Goals:**
- Verify an admin can batch delete multiple system users through the endpoint
- Verify an empty ID list is rejected with the documented validation error

**Non-Goals:**
- No production changes to batch-delete behavior
- No expansion into admin built-in-user protection in this slice
- No frontend batch-delete tests

## Decisions

1. Extend the existing `UserManageCRUDIntegrationTests` class so batch-delete coverage stays beside the rest of the admin CRUD surface.
2. Use the real auth object from `get_auth(self.admin_user)` because this endpoint passes through the permission decorator and requires `role_list` / `permission_list` on `request.auth`.
3. Keep the assertions narrow to the stable contract: response code, success/error payload, and actual DB deletion side effects.

## Risks / Trade-offs

- This slice intentionally does not cover the built-in-admin exclusion rule to keep the diff minimal and aligned with the ranking recommendation.
