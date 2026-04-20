## Why

MaxKB 目前面向外部系统的知识问答入口只有匿名三段式 chat、OpenAI chat completions 和 MCP 三条路径，每条都要求上游感知 chat_id、匿名 token 或 MCP 协议细节。上游 Orchestrator 需要的是一个稳定的一发一收知识问答接口，不应该暴露内部会话机制。

## What Changes

- 新增 `POST /api/knowledge/query` facade，单请求完成知识问答，不走匿名三段式多步握手。
- 复用现有 SIMPLE chat/RAG pipeline 作为唯一回答生成路径，对外隐藏 chat_id、匿名 token、MCP 协议细节。
- 用 `ApplicationApiKey` 作为 Orchestrator 外部鉴权凭证，Redis 维护 `session_id -> chat_id` 连续性绑定（含应用/身份校验，防止跨租户泄漏）。
- 返回稳定契约：`text`、`references[]`（来自真实检索命中）、`suggestions[]`（非模板化）、`cards[]`（v1 固定空数组）、`meta`（确定性）。
- 支持 `params._param_preview=true` 返回 `param_schema` 供上游 UI 渲染参数控件，严格无副作用。
- 管理端在现有应用集成/API key 页面新增 Orchestrator 对接参数输出（`endpoint_url`、`auth_token`、`default_params`），支持一键复制。

## Capabilities

### New Capabilities

- `orchestrator-knowledge-query-facade`: 面向 Orchestrator 的高体验知识问答后端接口，包含完整请求/响应/错误契约、Redis 会话绑定、结构化引用、非模板化建议、参数预览和管理端对接参数输出。

### Modified Capabilities

- `api-integration-testing`: 扩展覆盖新增的 Orchestrator query facade 端点和 admin 集成参数端点。
- `secret-management-hardening`: `ApplicationApiKey` 新增面向 Orchestrator 的外部使用场景，但不改变现有密钥管理模型。

## Impact

- 新增后端路由和 facade view/serializer（`apps/knowledge/` 或新建模块）
- 复用 `apps/chat/serializers/chat.py` SIMPLE pipeline 执行路径
- 复用 `apps/application/serializers/common.py` ChatInfo 和应用知识映射
- 扩展 `apps/application/views/application_api_key.py` 管理端集成参数输出
- 扩展 `ui/src/views/application-overview/` 前端集成面板，新增 Orchestrator 配置展示和复制
- 新增后端和前端自动化测试

## Source Plan

`.sisyphus/plans/orchestrator-knowledge-query.md`
