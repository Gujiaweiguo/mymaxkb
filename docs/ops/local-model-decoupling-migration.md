# local_model 解耦迁移与回滚手册

## 概述

这次变更把 `local_model` 从默认捆绑启动改为可选启动。

以前的版本中，运行 `start web` 或 `start all` 时会自动拉起 `local_model` 子服务（Ollama 本地推理进程）。对于不使用本地模型的部署来说，这个进程白白占用内存和端口，还会拖慢启动速度。

现在加了一个开关 `MAXKB_ENABLE_LOCAL_MODEL`。默认值是 `true`，所以不设这个变量的话，行为跟以前完全一样。把它设成 `false`，`local_model` 就不会跟着 web 一起启动了。

### 改了什么

- `start web` 和 `start all` 不再硬编码包含 `local_model`
- 新增环境变量 `MAXKB_ENABLE_LOCAL_MODEL`，默认 `true`（向后兼容）
- `local_model` 不可达时，web 进程不再崩溃，而是返回受控错误并打日志
- UI 上对依赖本地服务的 provider 添加了提示标签
- 启动时打印 `local_model=enabled` 或 `local_model=disabled` 日志标记

### 不影响什么

- `python main.py dev local_model` 独立启动入口不受影响，不管开关状态如何都能用
- Ollama provider 的外部 API 调用逻辑没有改动
- 数据库 schema 没有变更
- 业务流程引擎没有改动

---

## 配置说明

| 配置方式 | 键名 | 默认值 | 可选值 |
|---------|------|--------|--------|
| 环境变量 | `MAXKB_ENABLE_LOCAL_MODEL` | `true` | `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off` |
| YAML 配置文件 | `ENABLE_LOCAL_MODEL` | `true` | 同上 |

环境变量优先级高于 YAML 配置文件。环境变量名前缀 `MAXKB_` 会被自动去掉，所以 `MAXKB_ENABLE_LOCAL_MODEL=false` 等同于设置 `ENABLE_LOCAL_MODEL=false`。

### 生效范围

开关控制以下命令是否启动 `local_model` 子服务：

- `python apps/manage.py start web`
- `python apps/manage.py start all`
- `python main.py dev web`（dev 模式下的 web 启动）

不受影响的命令：

- `python main.py dev local_model`（始终可用，独立启动）
- `python apps/manage.py start task`（celery，与 local_model 无关）
- `python main.py dev celery`（同上）

---

## Docker 部署迁移

### 场景：不想使用本地模型，减少资源占用

在 `.env` 文件中添加一行：

```bash
MAXKB_ENABLE_LOCAL_MODEL=false
```

或者直接在 `docker-compose.yml` 的 environment 段中设置：

```yaml
services:
  maxkb:
    environment:
      - MAXKB_ENABLE_LOCAL_MODEL=false
```

改完之后重启容器：

```bash
docker compose up -d
```

查看日志确认开关生效：

```bash
docker compose logs maxkb 2>&1 | grep "local_model="
```

应该能看到 `local_model=disabled`。如果看到的是 `local_model=enabled`，说明环境变量没生效，检查 `.env` 文件是否被正确加载。

### 场景：继续使用本地模型（什么都不用改）

默认就是 `true`，不设这个变量跟以前的行为一模一样。

---

## 本地开发迁移

### 关掉 local_model 启动 web

```bash
MAXKB_ENABLE_LOCAL_MODEL=false python main.py dev web
```

启动后检查日志中是否有 `local_model=disabled`。

### 开着 local_model 启动 web（默认行为）

```bash
python main.py dev web
```

日志中会出现 `local_model=enabled`。

### 单独启动 local_model（不受开关影响）

```bash
python main.py dev local_model
```

这个命令在任何时候都能用，跟 `MAXKB_ENABLE_LOCAL_MODEL` 的值无关。

### 验证开关是否生效

```bash
MAXKB_ENABLE_LOCAL_MODEL=false python -c "
from maxkb.const import CONFIG
print(CONFIG.get_enable_local_model())
"
```

输出 `False` 说明开关生效。不加环境变量时输出 `True`。

---

## 生产环境迁移

推荐的迁移节奏分三步走。

### 第一步：部署新版本，保持默认行为

先部署新代码，不设 `MAXKB_ENABLE_LOCAL_MODEL`。默认值是 `true`，所有行为跟老版本一致。

部署后确认两点：

```bash
# 1. 启动日志包含 runtime_profile 标记
grep "runtime_profile=" /path/to/maxkb/logs/*.log

# 2. local_model 子服务正常启动
grep "local_model=enabled" /path/to/maxkb/logs/*.log
```

确认无误后观察 1 到 2 天，确保没有引入回归问题。

### 第二步：灰度关闭 local_model

选一台节点，在它的环境变量中设置 `MAXKB_ENABLE_LOCAL_MODEL=false`，重启该节点的 web 服务。

重启后确认：

```bash
# local_model 不再跟随 web 启动
grep "local_model=disabled" /path/to/maxkb/logs/*.log

# web 进程正常运行，runtime_profile 是 web
grep "runtime_profile=web" /path/to/maxkb/logs/*.log
```

观察该节点 1 到 3 天。如果业务侧没有调用本地模型的需求，或者本地模型调用已经全部走了外部 Ollama/Xinference/vLLM 实例，那灰度就通过了。

### 第三步：全量关闭

确认灰度没问题后，在所有节点统一设置：

```bash
MAXKB_ENABLE_LOCAL_MODEL=false
```

重启所有 web 节点，确认全部输出 `local_model=disabled`。

---

## 回滚手册

### 情况一：想恢复 local_model 捆绑启动

把环境变量改回 `true`，或者直接删掉这个变量（默认就是 `true`）：

```bash
# 方法一：显式设为 true
MAXKB_ENABLE_LOCAL_MODEL=true python apps/manage.py start web

# 方法二：不设这个变量，走默认值
python apps/manage.py start web
```

对于 Docker 部署，从 `.env` 或 `docker-compose.yml` 中删除 `MAXKB_ENABLE_LOCAL_MODEL` 那一行，然后：

```bash
docker compose up -d
```

### 情况二：回滚到旧版本代码

如果需要完全回退到这次变更之前的版本，直接切回旧代码即可。旧版本不存在 `MAXKB_ENABLE_LOCAL_MODEL` 这个变量，`local_model` 会照常跟随 web 启动。

```bash
# 把 v1.11.0 替换成你之前的版本 tag
git checkout v1.11.0
# 重新部署
```

### 情况三：local_model 启动后不可达

这不是代码回滚的问题，而是 local_model 进程本身出了故障。web 进程不会因此崩溃，调用本地模型相关接口时会返回错误，日志中会出现 `local_model_unreachable`。

排查步骤：

```bash
# 检查 local_model 进程是否存活
ps aux | grep local_model

# 检查端口是否在监听
ss -tlnp | grep 11636

# 查看 local_model 日志
grep "local_model" /path/to/maxkb/logs/*.log
```

如果是进程挂了，单独重启 local_model 即可，不需要重启 web：

```bash
python main.py dev local_model
```

生产环境用 `start` 命令：

```bash
python apps/manage.py start local_model
```

---

## 故障排查

### 启动后看不到 local_model 相关日志

检查环境变量是否正确设置：

```bash
echo $MAXKB_ENABLE_LOCAL_MODEL
```

如果输出为空，说明变量没加载。在 Docker 环境中检查 `.env` 文件是否在正确位置。在本地开发中，确保在启动命令前面加了环境变量。

### 日志中出现 local_model_unreachable

这是 web 进程尝试调用 local_model 服务但连接失败的标记。常见原因：

1. **local_model 没有启动**。开关是 `true` 但 local_model 进程没跑起来。检查进程状态。
2. **端口被占用或修改了**。默认端口是 `11636`，如果改过 `MAXKB_LOCAL_MODEL_PORT`，确认 local_model 监听的端口和 web 调用的端口一致。
3. **防火墙或网络问题**。在多节点部署中，web 和 local_model 可能不在同一台机器上，检查 `MAXKB_LOCAL_MODEL_HOST` 的指向是否正确。

查看具体错误信息：

```bash
grep "local_model_unreachable" /path/to/maxkb/logs/*.log
```

日志会打印出连接失败的具体异常（Connection refused、Timeout 等）。

### runtime_profile 日志标记说明

启动时每个进程会打印自己的 runtime_profile：

| 日志标记 | 含义 |
|---------|------|
| `runtime_profile=web` | web 进程（gunicorn） |
| `runtime_profile=local_model` | 本地模型推理进程 |
| `runtime_profile=web, fallback=true` | 没有设置 `SERVER_NAME`，默认回落到 web |

如果在不该出现的地方看到了 `runtime_profile=local_model`，检查 `SERVER_NAME` 环境变量是否被意外设置。

### 相关日志关键字速查

| 关键字 | 触发场景 |
|--------|---------|
| `local_model=enabled` | 启动时开关为 true |
| `local_model=disabled` | 启动时开关为 false |
| `local_model_unreachable` | web 调用 local_model 失败 |
| `runtime_profile=web` | web 运行态 |
| `runtime_profile=local_model` | local_model 运行态 |
| `service startup config: local_model=enabled` | start 命令中 local_model 加入服务编排 |
| `service startup config: local_model=disabled` | start 命令中 local_model 被排除 |

### 开关设了 false 但 local_model 还是在跑

确认你改的是正确的位置。Docker 环境中，`.env` 文件和 `docker-compose.yml` 里的 `environment` 都会生效，但后者可能覆盖前者。检查实际加载的值：

```bash
# 容器内检查
docker compose exec maxkb env | grep MAXKB_ENABLE_LOCAL_MODEL
```

本地开发中，确认你在启动命令前面加了环境变量：

```bash
# 内联写法（推荐，最不容易出错）
MAXKB_ENABLE_LOCAL_MODEL=false python main.py dev web

# export 写法也行，但要在同一个 shell 会话里执行
export MAXKB_ENABLE_LOCAL_MODEL=false
python main.py dev web
```
