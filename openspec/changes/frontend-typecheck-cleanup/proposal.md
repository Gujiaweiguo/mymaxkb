## Why

The frontend currently has known TypeScript errors in a small set of files, which keeps `npm run type-check` from passing and makes future changes harder to validate safely. This change is needed now to restore a reliable frontend type-check baseline for the targeted error cluster without mixing in unrelated refactors.

## What Changes

- Fix the known TypeScript errors in the current failing frontend files only:
  - `ui/src/components/ai-chat/component/question-content/index.vue`
  - `ui/src/components/dynamics-form/constructor/items/ModelConstructor.vue`
  - `ui/src/views/trigger/component/ApplicationParameter.vue`
  - `ui/src/views/trigger/component/ToolParameter.vue`
  - `ui/src/workflow/plugins/dagre.ts`
- Align the affected code with existing repo typing patterns instead of introducing new architecture or broad normalization.
- Verify the targeted cleanup with `npm run type-check`, and run `npm run lint` if the touched files require lint-sensitive adjustments.

## Capabilities

### New Capabilities
- `frontend-typecheck-stability`: Define requirements for keeping targeted frontend modules type-check clean and safe to validate locally.

### Modified Capabilities
- None.

## Impact

- Affected code is limited to the five known frontend files currently failing TypeScript checks.
- No API contract, database schema, or backend service behavior is expected to change.
- Validation will rely on frontend static analysis signals, primarily `npm run type-check`, with lint verification as needed for touched files.
