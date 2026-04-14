## Overview

本次变更的目标是将 MaxKB 从“内置 local_model 运行时 + 本地推理依赖”的架构，收敛到“只对接外部模型 API”的架构。

设计上采用 **hard removal**，而不是兼容壳或灰度双轨：

- 不再保留内置 `local_model` 启动模式
- 不再保留 `LocalModelProvider` registry/provider 概念
- 不再保留仓库内 embedding/reranker 的 torch 本地推理链路
- 不对遗留 `model_local_provider` 数据做静默迁移，而是显式 fail-fast

这样做的核心收益是：

- 降低主应用启动复杂度与部署耦合
- 去掉只为本地模型运行时存在的依赖面与维护面
- 统一产品语义：MaxKB 只消费外部模型服务，不再拥有本地模型运行时

## Goals

1. 移除 built-in `local_model` runtime、startup、routing、settings、WSGI 分支。
2. 移除 built-in `model_local_provider` backend registry 和 frontend 暴露。
3. 移除 `apps/local_model/` 与 `apps/models_provider/impl/local_model_provider/` 的源码所有权。
4. 移除 `torch` / `langchain-huggingface` / `sentence-transformers` 等只为内置本地推理服务的依赖。
5. 为遗留 `model_local_provider` 状态建立单一、稳定、可操作的 fail-fast 语义。
6. 保持外部 provider（如 Ollama、Xinference、vLLM、Docker AI、云厂商 provider）继续可用。

## Non-Goals

- 不保留内置 local-model 的兼容开关或 fallback runtime
- 不自动把旧 `model_local_provider` 数据迁移到其他 provider
- 不重构所有 provider 抽象，只做为删除 local-model 所必需的最小改动
- 不解决与本次变更无关的既有 warnings（如现存 URL warnings、前端 eval warnings）

## Architecture

### Before

仓库中同时存在两类模型接入路径：

1. **外部 API provider**：如 OpenAI、Ollama、Xinference、vLLM 等
2. **内置 local_model runtime**：通过 `SERVER_NAME == 'local_model'` 分流、独立 service orchestration、`LocalModelProvider` registry、以及 torch/Hugging Face 本地推理代码实现

这导致以下耦合：

- `main.py` 和 services command 持有 `local_model` 启动模式
- settings/auth/urls/wsgi 通过 `.model` 分支切 profile
- `apps/local_model/` 承载本地模型服务相关视图与序列化逻辑
- `local_model_provider` 目录承载 embedding/reranker 本地执行实现
- `pyproject.toml` 持有本地推理依赖与 PyTorch 源配置

### After

变更后只保留 **external-API-only** 模式：

- 所有模型能力都通过外部 provider 消费
- 内置 `local_model` 启动模式被移除
- runtime profile 固定收敛到 supported web/task 路径
- local-model 相关 provider/app/runtime 源码被删除
- 遗留 `model_local_provider` 数据进入统一 fail-fast 路径

## Key Design Decisions

### 1. Legacy state uses fail-fast instead of silent migration

遗留 `provider='model_local_provider'` 不做自动迁移，因为：

- 自动映射到其他 provider 会引入语义猜测
- 会掩盖部署方未完成升级的真实状态
- 与“hard removal”目标冲突

因此在 `models_provider.tools.get_provider()` 建立单一边界：

- 如果 provider 是 `model_local_provider`
- 立即抛出显式 unsupported-provider 错误
- 所有关键调用点统一走这个 helper，避免删 registry 后退化成 `KeyError` / `ImportError`

### 2. Shared abstraction extraction precedes deletion

在删除 `local_model_provider` 之前，先处理 Ollama/Xinference 对旧类型的依赖。

实际代码中，外部 provider 并没有复用 local-model 的运行时实现，只在 credential 校验中引用了旧类型名。为避免删除时产生无效 import，先新增 provider-neutral capability protocol：

- `EmbeddingModel`
- `DownloadableEmbeddingModel`
- `RerankerModel`

这样可以在不迁移业务实现的前提下，解除对 `local_model_provider` 的类型层耦合。

### 3. Runtime/profile branches are flattened, not replaced

本次变更不再保留 `SERVER_NAME == 'local_model'` 分支，也不引入新的 profile 分支。

处理方式是直接收敛：

- `settings/*/__init__.py` → 固定导入 `.web`
- `urls/__init__.py` → 固定导入 `.web`
- `wsgi/__init__.py` → 固定导入 `.web`
- `main.py` / services command → 仅保留受支持的启动模式

这比“保留开关但默认关闭”更符合 hard-removal 目标，也降低维护成本。

### 4. Fresh-install behavior must not seed removed provider state

在最终 review 中发现 `apps/models_provider/migrations/0001_initial.py` 仍为 fresh install 写入 `provider='model_local_provider'` 的默认 embedding model。虽然运行时已经 fail-fast，但 fresh install 再写入已删除 provider 状态，和硬移除目标冲突。

因此设计上追加修复：

- 移除该 migration 中的 default embedding seed 逻辑
- 避免新环境初始化时写入已删除 provider 的历史配置

### 5. Installer/build surfaces must not reference deleted scripts

删除 local-model installer 脚本后，`installer/Dockerfile-vector-model` 仍引用已删脚本会造成构建失败。设计上采用最小修复：

- 不恢复旧 installer 脚本
- 直接在 Dockerfile 中内联 tokenizer 下载逻辑

这样既保留构建可用性，也不把已移除的 local-model 资产带回仓库。

## Implementation Structure

### Wave 1 — Foundation

- 抽离 provider-neutral capability protocol
- 建立 legacy local provider fail-fast 边界

### Wave 2 — Backend Hard Removal

- 删除 provider registry entry
- 删除 startup/service/settings/urls/wsgi 中的 local-model 分支
- 删除 `apps/local_model/` app 所有权

### Wave 3 — Frontend and Dependency Cleanup

- 删除 frontend provider 暴露
- 删除 `local_model_provider` 残余源码
- 删除本地推理依赖、config、installer residue
- 更新升级文档和仓库事实文档

### Wave 4 — Integrated Verification

- 后端 `manage.py check`
- legacy fail-fast 后端测试
- 前端 `type-check + lint + test + build`
- 最终 symbol audit 与归档前修正

## Rollback Boundaries

本次变更按 task cluster 设计 rollback 边界：

1. RLM-008/009
2. RLM-007
3. RLM-006
4. RLM-004/005
5. RLM-003
6. RLM-002
7. RLM-001

每个边界都要求在回滚后重新执行最近的验证命令，确保仓库回到一致状态。

## Verification Strategy

设计上的验证重点不是“是否还能跑 local_model”，而是：

1. **删除面验证**
   - 生产代码不再暴露 `LocalModelProvider`
   - 不再存在 `SERVER_NAME == 'local_model'`
   - 不再存在 built-in local-model startup/service wiring

2. **legacy contract 验证**
   - 旧 `model_local_provider` 状态稳定 fail-fast
   - 不退化为 `KeyError` / `ImportError`

3. **supported runtime 验证**
   - `python apps/manage.py check`
   - `cd ui && npm run type-check && npm run lint && npm run test`
   - `cd ui && npm run build`

4. **scope-fidelity 验证**
   - fresh install 不再 seed removed provider
   - build surfaces 不再引用已删脚本
   - 主 specs 与归档 change 语义一致

## Risks and Mitigations

### Risk: deleting shared code breaks external providers
Mitigation:
- 先做 RLM-001 capability extraction
- 只迁移类型/抽象层耦合，不迁移运行时实现

### Risk: registry deletion turns legacy rows into opaque runtime errors
Mitigation:
- 先做 RLM-002 fail-fast
- 再做 RLM-003 registry removal

### Risk: startup/profile cleanup leaves half-deleted runtime branches
Mitigation:
- 将 runtime 入口按组一起收敛：`main.py`、services、settings、urls、wsgi
- 验证 grep + `manage.py check`

### Risk: dependency removal breaks unrelated providers
Mitigation:
- 先确认 surviving external providers 不再引用 local-model 运行时代码
- 删除 `local_model_provider` 后再删依赖

### Risk: documentation/specs diverge from implemented behavior
Mitigation:
- 更新 migration guide 与 AGENTS 仓库事实
- 在 archive 前同步主 OpenSpec specs

## Resulting Contract

归档完成后，系统的新契约为：

- MaxKB **不再内置** local-model runtime
- MaxKB **只支持** 外部 API model provider
- 遗留 `model_local_provider` 状态会显式报错
- 主 specs、归档 change、执行证据和实现状态保持一致
