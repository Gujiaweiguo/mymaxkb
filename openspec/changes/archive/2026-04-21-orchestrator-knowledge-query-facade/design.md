## Context

MaxKB 已有完整的知识问答链路：SIMPLE 应用类型通过 `BaseSearchDatasetStep -> BaseGenerateHumanMessageStep -> BaseChatStep` 完成「检索→生成」；`ChatInfo` 在 Redis 中缓存会话上下文 30 分钟；`ApplicationApiKey` 作为外部程序化访问凭证已在 MCP 通道中验证可行。但这些能力都被封装在匿名三段式 chat、OpenAI completions 或 MCP 协议内部，上游 Orchestrator 无法直接复用。

本变更新增一个薄 facade 层：外部暴露 `POST /api/knowledge/query` 稳定契约，内部调用现有 SIMPLE pipeline，通过 Redis 维护 `session_id -> chat_id` 绑定实现连续追问，管理端在现有应用集成页输出对接参数。

关键约束：
- 不新建第二套检索/生成管道
- 不泄露 chat_id、匿名 token、MCP 协议细节到外部契约
- preview 模式零副作用
- references 来自真实检索证据
- suggestions 非模板化，质量不足时返回空数组

## Goals / Non-Goals

**Goals:**
- 新增 `POST /api/knowledge/query` 面向 Orchestrator 的一发一收知识问答接口
- 用 `ApplicationApiKey` 鉴权，Redis 维护 session 连续性（含应用/身份绑定校验）
- 返回稳定外部契约：`text`、`references[]`、`suggestions[]`、`cards[]`、`meta`
- 支持 `params._param_preview=true` 返回参数 schema，零副作用
- 管理端在现有应用集成/API key 页面输出 Orchestrator 对接参数（含复制）
- TDD 覆盖全部契约路径

**Non-Goals:**
- 构建通用外部知识服务平台抽象
- 意图识别、capability 路由、UnifiedEnvelope 封装
- 前端 UI 渲染（由上游 Orchestrator 负责）
- 新建独立 Orchestrator 管理面板

## Decisions

### 1. 复用现有 SIMPLE chat pipeline 作为唯一回答生成路径

Facade adapter 将 Orchestrator 请求转换为 SIMPLE pipeline 调用，不创建第二套检索/生成实现。

**Why:** 保持行为一致性，避免回答漂移和双倍维护成本。

**Alternatives considered:**
- 直接调用底层 `VectorStore.query()` + 独立生成 → 会产生与 chat 产品不同的回答质量，且绕过应用发布/模型验证流程。

### 2. 用 ApplicationApiKey 作为外部 Orchestrator 鉴权凭证

**Why:** 已有 MCP 通道验证了 API key 作为程序化访问凭证的可行性；管理端已有创建/管理 API key 的完整 UI。

**Alternatives considered:**
- 用 `ApplicationAccessToken` → 更偏 chat/open 访问配置，语义不符。
- 新建专属 Token → 成本高，首版不需要。

### 3. Redis-first session 绑定，存储 richer object

缓存 `session_id -> {chat_id, application_id, api_key_fingerprint, user_binding_hash, created_at, last_seen_at}`，绑定校验防止跨应用/身份复用。TTL 30 分钟，仅正常回答请求刷新。

**Why:** 裸 `chat_id` 太薄，无法做安全校验和问题排查。

**Alternatives considered:**
- 仅内存 → 多实例不稳。
- Redis + 内存降级 → 增加复杂度，首版不需要。

### 4. references 来自真实检索证据

从 `BaseSearchDatasetStep` 执行产物提取，每条至少包含 `title` + `snippet`，按可用性补充 `url`、`confidence`、`document_id`、`paragraph_id`。

**Why:** 引用可信度是核心产品价值。

### 5. suggestions 采用 retrieval/answer-context 生成 + 空数组保守降级

**Why:** 坏建议比没建议更损害体验。

### 6. cards v1 固定空数组

当前 pipeline 不自然产生 card-like 输出，v1 不虚构。

### 7. 管理端放在现有应用集成/API key 页面

**Why:** 改动最小，与 API key 管理语义一致，已有复制交互模式可复用。

### 8. 错误码集合

标准化为 `INVALID_REQUEST`、`UNAUTHORIZED`、`SESSION_MISMATCH`、`KNOWLEDGE_SCOPE_INVALID`、`INTERNAL_ERROR`。

### 9. 无有效检索命中时沿用现有 no_references_setting 行为

仍返回稳定正式响应结构（`references: []`、`suggestions: []`、`cards: []`、`meta.hit_paragraph_count: 0`）。

### 10. 管理端无可用 API key 时自动生成

调用现有 API key 创建路径，返回新 secret。

## Risks / Trade-offs

- **[Risk] Facade 响应可能过于接近内部 chat 结构。** → Mitigation: 定义严格外部 DTO，禁止泄漏 chat_id/pipeline 内部字段。
- **[Risk] Session 跨租户泄漏。** → Mitigation: 绑定 application_id + auth identity，拒绝不匹配的 session_id 复用。
- **[Risk] Preview 模式产生副作用。** → Mitigation: 硬编码零副作用路径 + 独立测试覆盖 DB/cache 不变性。
- **[Risk] Suggestions 退化为模板。** → Mitigation: 定义显式相关性规则，低质量时返回空数组。
- **[Risk] 范围蔓延到通用平台抽象。** → Mitigation: 严格限定为 Orchestrator UX，不做 provider/plugin 抽象。

## Migration Plan

1. 实现 facade 路由、契约 DTO、鉴权和 session 绑定（Tasks 1-2）
2. 实现执行适配器、响应塑形和 preview 模式（Tasks 3-5）
3. 实现管理端后端输出和前端 UI（Tasks 6-7）
4. 端到端回归覆盖（Task 8）

**Rollback:** 移除 `POST /api/knowledge/query` 路由注册和 facade view/serializer，清理 Redis session 键前缀，移除管理端前端组件扩展。不影响现有 chat/MCP/OpenAI 接口。

## Open Questions

- 无（全部在规划阶段已解决）。
