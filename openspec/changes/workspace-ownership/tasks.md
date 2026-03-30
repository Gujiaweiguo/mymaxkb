## 1. Workspace Deletion Constraint Tests

- [x] 1.1 Add test: workspace with application cannot be deleted (delete_check returns can_delete=False)
- [x] 1.2 Add test: workspace with application folder cannot be deleted
- [x] 1.3 Add test: workspace with knowledge cannot be deleted
- [x] 1.4 Add test: workspace with knowledge folder cannot be deleted
- [x] 1.5 Add test: workspace with knowledge workflow cannot be deleted
- [x] 1.6 Add test: workspace with tool cannot be deleted
- [x] 1.7 Add test: workspace with tool folder cannot be deleted
- [x] 1.8 Add test: workspace with model cannot be deleted
- [x] 1.9 Add test: workspace with trigger cannot be deleted
- [x] 1.10 Add test: workspace with resource permission cannot be deleted
- [x] 1.11 Add test: empty workspace can be deleted (delete_check returns can_delete=True, DELETE succeeds)

## 2. Default Workspace Immutability Tests

- [x] 2.1 Add test: default workspace rejects member add
- [x] 2.2 Add test: default workspace rejects member list (page)
- [x] 2.3 Add test: default workspace rejects member remove

## 3. Workspace Name Uniqueness Tests

- [x] 3.1 Add test: creating workspace with duplicate name fails
- [x] 3.2 Add test: updating workspace to existing name fails

## 4. Workspace Update Path Test

- [x] 4.1 Add test: POST with id field updates workspace name

## 5. Verification

- [x] 5.1 Run all new tests and verify they pass
- [x] 5.2 Run existing workspace tests and verify no regressions
