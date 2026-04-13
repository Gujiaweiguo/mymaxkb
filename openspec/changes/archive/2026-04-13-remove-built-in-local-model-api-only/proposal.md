## Why

当前仓库仍内置 `local_model` 运行时、启动分流、provider 概念与 torch 推理链路，即使系统已经支持通过外部 API 接入模型服务。这种内置模式扩大了主应用的启动复杂度、依赖面和故障半径，也让“本地模型”继续表现为仓库自带能力而不是外部服务能力。需要将内置 `local_model` 完整移除，明确 MaxKB 只与外部模型 API 集成。

## What Changes

- 移除内置 `local_model` 运行时、启动命令、`SERVER_NAME == 'local_model'` 分流、URL/WSGI/settings 分支与 provider 注册。
- 先将被 Ollama/Xinference 复用的 embedding/reranker 共享抽象迁移到 provider-neutral 位置，再删除 `local_model_provider`。
- 为遗留 `model_local_provider` 配置和数据实现显式 fail-fast，不做静默迁移或兼容壳。
- 删除前端对内置 local provider 的入口、元数据和提示，使 UI 仅暴露外部 API provider。
- 清理只为内置 local-model 运行时服务的 Python 依赖、安装脚本和 HF 本地模型假设。
- 增加自动化验证，证明支持的外部 provider 仍可用，且仓库中不再存在内置 local_model 概念。

## Capabilities

### Modified Capabilities
- `local-model-runtime-decoupling`: 从“可显式启停的内置 local_model”收敛为“仓库不再提供内置 local_model 运行时”。
- `model-provider-availability-signaling`: 从“提示内置 local_model provider 可用性”收敛为“对遗留 local-model 配置执行可操作的 fail-fast，并仅展示外部 provider”。
- `api-integration-testing`: 增加移除后的集成验证，证明受支持启动路径有效、遗留 local-model 状态按预期失败、并且移除符号在生产代码中缺失。

## Impact

- Affected code: `main.py`, `apps/common/management/commands/services/*`, `apps/maxkb/settings/*`, `apps/maxkb/urls/*`, `apps/maxkb/wsgi/*`, `apps/local_model/*`, `apps/models_provider/constants/model_provider_constants.py`, `apps/models_provider/impl/local_model_provider/*`, `apps/models_provider/impl/ollama_model_provider/*`, `apps/models_provider/impl/xinference_model_provider/*`, `ui/src/components/dynamics-form/items/model/provider-data.ts`, `ui/src/views/model/component/Provider.vue`, `pyproject.toml`.
- Runtime behavior: `local_model` 不再是受支持启动模式；系统只支持外部 API model provider。
- Upgrade behavior: 旧的 `model_local_provider` 配置或数据不会被自动迁移；它们将以明确、可操作的错误路径 fail-fast。
- Dependency behavior: 主应用不再持有仅用于内置 local-model 推理的 torch/transformers 运行时依赖。
