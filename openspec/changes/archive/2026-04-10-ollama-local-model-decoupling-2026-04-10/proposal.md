## Why

当前项目中 `model_ollama_provider` 已是外部 API 模式，但 `local_model` 仍与 web 默认启动链路强耦合，导致运行复杂度与故障半径扩大。需要在不重写 Ollama provider 的前提下，将 local_model 变为显式可选能力，并保持可回滚兼容策略。

## What Changes

- 将 local_model 从默认 web 启动编排中解耦，改为由显式开关控制。
- 引入 `MAXKB_ENABLE_LOCAL_MODEL` 配置与统一运行态标记日志。
- 为 local_model 不可达场景提供受控降级，避免主服务崩溃。
- 保持 `model_ollama_provider` 行为不变，仅做边界回归保护。
- 前端增加 local provider 可用性提示，避免用户误判。
- 增加可自动执行的启动矩阵验收与运维迁移/回滚文档。

## Capabilities

### New Capabilities
- `local-model-runtime-decoupling`: local_model 生命周期与 web 进程解耦，支持显式启停与兼容默认。
- `model-provider-availability-signaling`: 对本地 provider 的可用性进行后端降级与前端可视化提示。

### Modified Capabilities
- `api-integration-testing`: 新增启动矩阵与故障路径自动化验收要求（local_model enabled/disabled/unreachable）。

## Impact

- Affected code: `main.py`, `apps/common/management/commands/services/*`, `apps/maxkb/{conf,settings,urls,wsgi}/*`, `apps/models_provider/impl/local_model_provider/*`, `ui/src/views/model/component/Provider.vue`.
- Runtime behavior: `start web` 默认行为调整为可配置；新增运行态 marker。
- API behavior: local_model 不可达时返回受控错误而非进程级失败。
- Ops/docs: 新增迁移策略、回滚开关与发布门禁。
