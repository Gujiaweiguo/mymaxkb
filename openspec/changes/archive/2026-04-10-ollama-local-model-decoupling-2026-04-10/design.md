## Context

现状中 `web` 与 `local_model` 通过启动编排与 `SERVER_NAME` 运行态分流形成隐式耦合：
- `services.command.Services.web_services()` 默认包含 `local_model`
- `settings/urls/wsgi` 由 `SERVER_NAME` 切换
- `local_model_provider` 在 web 进程内通过 `LOCAL_MODEL_HOST/PORT` 回调本地服务

同时，`model_ollama_provider` 已是 `api_base` 驱动的外部 provider，不是主要耦合源。

## Goals / Non-Goals

**Goals:**
- 将 local_model 从 web 默认硬绑定中解耦，改为显式开关控制。
- 保持 Ollama provider 现有行为与接口语义不变。
- local_model 不可达时保证主服务可用并返回标准化错误。
- 提供机器可断言的启动矩阵与回滚路径。

**Non-Goals:**
- 不重写 provider 抽象与模型协议层。
- 不做 DB schema/migration 变更。
- 不做跨仓拆分或引入新的模型编排系统。

## Decisions

1. **引入配置开关 `MAXKB_ENABLE_LOCAL_MODEL`（v1 默认 true）**
   - Rationale: 保持存量部署兼容，降低升级风险。
   - Alternative: 默认 false（更激进），但会放大升级断裂面。

2. **启动解耦优先于 provider 重构**
   - Rationale: 主要问题是生命周期绑定，不是 Ollama 调用形态。
   - Alternative: 先做 provider 统一重构，成本高且超出需求。

3. **保留 `SERVER_NAME` 分流机制，但增加统一 marker 与默认回落语义**
   - Rationale: 最小改动原则下提升可观测性与可诊断性。
   - Alternative: 彻底移除双运行态，风险过高。

4. **local_model 调用失败采用受控降级**
   - Rationale: 主服务可用性优先，错误向调用方显式暴露。
   - Alternative: 维持现状（异常穿透），会导致不确定故障。

## Risks / Trade-offs

- [兼容风险] 默认行为变化理解不一致 → 通过文档与启动日志 marker 明确化。
- [灰度风险] local_model 关闭后部分能力不可用 → UI 提示与 API 受控错误。
- [实现风险] 多入口启动命令不一致 → 启动矩阵脚本化校验。
- [回滚风险] 回退不完整导致状态漂移 → 保留单开关回滚策略并演练高风险任务。

## Migration Plan

1. 引入开关与日志 marker（不改默认行为）。
2. 调整服务编排，使 local_model 受开关控制。
3. 增加降级与 UI 提示。
4. 执行启动矩阵验收与文档发布。

Rollback:
- 立即将 `MAXKB_ENABLE_LOCAL_MODEL=true` 并恢复 `web_services` 绑定策略。
- 回退 local_model 降级包装与 UI 提示改动。

## Open Questions

- v2 是否将默认值切换为 false（需依据线上观测与运维反馈决定）。
