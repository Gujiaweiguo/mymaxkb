## 1. Wave 1 — 基线与配置

- [ ] 1.1 T01 启动与运行态耦合清单冻结
  - Depends on: None
  - Risk: Medium
  - Input: `main.py`, `apps/common/management/commands/services/*`, `apps/maxkb/{settings,urls,wsgi}/*`
  - Output: 启动矩阵（命令 × SERVER_NAME × 期望服务）
  - Acceptance:
    - 覆盖 `python main.py dev web|celery|local_model` 与 `python apps/manage.py start web|task|all`
    - 每条记录包含“当前行为 + 目标行为 + 校验命令”
  - Rollback: 无代码回滚；删除矩阵草稿

- [ ] 1.2 T02 引入 local_model 显式启用开关（兼容默认）
  - Depends on: T01
  - Risk: High
  - Input: `apps/maxkb/conf.py` 与启动命令解析层
  - Output: `MAXKB_ENABLE_LOCAL_MODEL`（v1 默认 true）
  - Acceptance:
    - `MAXKB_ENABLE_LOCAL_MODEL=true|false` 可稳定读取
    - 未设置时默认行为与发布说明一致（默认 true）
    - 启动日志包含 `local_model=enabled|disabled`
  - Rollback: 恢复历史默认（强制 true）并保留变量兼容

- [ ] 1.3 T04 SERVER_NAME 分流路径一致性收敛与标记
  - Depends on: T01
  - Risk: Medium
  - Input: `apps/maxkb/settings/*/__init__.py`, `apps/maxkb/urls/__init__.py`, `apps/maxkb/wsgi/__init__.py`
  - Output: 分流规则与 marker 统一
  - Acceptance:
    - `SERVER_NAME=web|local_model` 均有明确运行态 marker
    - `SERVER_NAME` 缺失时稳定回落 web
  - Rollback: 删除 marker 增量，保留原分流逻辑

## 2. Wave 2 — 核心解耦

- [ ] 2.1 T03 解除 start web 对 local_model 的硬绑定
  - Depends on: T01, T02
  - Risk: High
  - Input: `apps/common/management/commands/services/command.py`, `services/local_model.py`, `main.py`
  - Output: web 启动按开关决定是否携带 local_model
  - Acceptance:
    - `MAXKB_ENABLE_LOCAL_MODEL=false` 时 `start web` 不拉起 local_model
    - `MAXKB_ENABLE_LOCAL_MODEL=true` 时行为符合配置策略
    - `dev local_model` 仍可独立启动
  - Rollback: 恢复 `web_services` 默认包含 local_model

- [ ] 2.2 T05 local_model provider 失败降级（主服务不崩）
  - Depends on: T02, T03
  - Risk: High
  - Input: `apps/models_provider/impl/local_model_provider/model/*/web.py`, `apps/models_provider/serializers/model_apply_serializers.py`
  - Output: local_model 不可达时受控错误与日志
  - Acceptance:
    - `LOCAL_MODEL_PORT=59999` 时 embedding/reranker 返回受控错误
    - web 进程保持存活
  - Rollback: 回退异常包装层

- [ ] 2.3 T06 保持 Ollama provider 不变并补充边界保护
  - Depends on: T03
  - Risk: Low
  - Input: `apps/models_provider/impl/ollama_model_provider/*`
  - Output: Ollama 行为回归证明
  - Acceptance:
    - provider 列表仍包含 `model_ollama_provider`
    - 凭据校验语义不变
  - Rollback: 回退附带改动，仅保留解耦主线

## 3. Wave 3 — 体验与文档

- [ ] 3.1 T07 UI 能力提示与分类一致性调整
  - Depends on: T04, T06
  - Risk: Medium
  - Input: `ui/src/views/model/component/Provider.vue`, `ui/src/components/dynamics-form/items/model/provider-data.ts`
  - Output: local provider 可用性提示
  - Acceptance:
    - UI 可区分在线 provider 与依赖本地服务 provider
    - local_model 关闭时入口给出清晰提示
  - Rollback: 回退前端提示层

- [ ] 3.2 T09 运维/发布迁移文档（含回滚手册）
  - Depends on: T07
  - Risk: Low
  - Input: 配置变更、启动矩阵、降级策略
  - Output: 升级与回滚文档
  - Acceptance:
    - 文档包含开关说明、默认值、示例命令、回滚命令
    - 命令可直接执行且无占位符
  - Rollback: 回退文档入口引用

## 4. Wave 4 — 收口门禁

- [ ] 4.1 T08 启动矩阵自动化验收脚本化
  - Depends on: T01, T03, T05
  - Risk: Medium
  - Input: 启动入口与日志 marker
  - Output: 一键验收命令清单/脚本
  - Acceptance:
    - `MAXKB_ENABLE_LOCAL_MODEL=false timeout 30s python main.py dev web` 命中 disabled marker
    - `MAXKB_ENABLE_LOCAL_MODEL=true timeout 30s python main.py dev web` 命中 enabled marker
    - 不可达场景命中 `local_model_unreachable` 且主服务可用
    - `python apps/manage.py check` 通过
  - Rollback: 标记脚本为历史版本并按 T03/T05 回滚

- [ ] 4.2 T10 集成收口与发布门禁
  - Depends on: T02, T07, T08, T09
  - Risk: Medium
  - Input: 全部证据与 DoD
  - Output: Go/No-Go 结论
  - Acceptance:
    - 高风险任务（T02/T03/T05）均有回滚演练记录
    - 门禁结论具备二元结果与触发条件
  - Rollback: No-Go 时恢复兼容默认绑定并撤回 UI 强提示
