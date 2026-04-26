<p align="center"><img src= "https://github.com/1Panel-dev/maxkb/assets/52996290/c0694996-0eed-40d8-b369-322bf2a380bf" alt="MaxKB" width="300" /></p>
<h3 align="center">Open-source platform for building enterprise-grade agents</h3>
<h3 align="center">强大易用的企业级智能体平台</h3>
<p align="center"><a href="https://trendshift.io/repositories/9113" target="_blank"><img src="https://trendshift.io/api/badge/repositories/9113" alt="1Panel-dev%2FMaxKB | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a></p>
<p align="center">
  <a href="https://www.gnu.org/licenses/gpl-3.0.html#license-text"><img src="https://img.shields.io/github/license/1Panel-dev/maxkb?color=%231890FF" alt="License: GPL v3"></a>
  <a href="https://github.com/1Panel-dev/maxkb/releases/latest"><img src="https://img.shields.io/github/v/release/1Panel-dev/maxkb" alt="Latest release"></a>
  <a href="https://github.com/1Panel-dev/maxkb"><img src="https://img.shields.io/github/stars/1Panel-dev/maxkb?color=%231890FF&style=flat-square" alt="Stars"></a>    
  <a href="https://hub.docker.com/r/1panel/maxkb"><img src="https://img.shields.io/docker/pulls/1panel/maxkb?label=downloads" alt="Download"></a><br/>
 [<a href="/README_CN.md">中文(简体)</a>] | [<a href="/README.md">English</a>] 
</p>
<hr/>

MaxKB = Max Knowledge Brain, it is an open-source platform for building enterprise-grade agents. MaxKB integrates Retrieval-Augmented Generation (RAG) pipelines, supports robust workflows, and provides advanced MCP tool-use capabilities. MaxKB is widely applied in scenarios such as intelligent customer service, corporate internal knowledge bases, academic research, and education.

- **RAG Pipeline**: Supports direct uploading of documents / automatic crawling of online documents, with features for automatic text splitting, vectorization. This effectively reduces hallucinations in large models, providing a superior smart Q&A interaction experience.
- **Agentic Workflow**: Equipped with a powerful workflow engine, function library and MCP tool-use, enabling the orchestration of AI processes to meet the needs of complex business scenarios.
- **Seamless Integration**: Facilitates zero-coding rapid integration into third-party business systems, quickly equipping existing systems with intelligent Q&A capabilities to enhance user satisfaction.
- **Model-Agnostic**: Supports various large models, including private models (such as DeepSeek, Llama, Qwen, etc.) and public models (like OpenAI, Claude, Gemini, etc.).
- **Multi Modal**: Native support for input and output text, image, audio and video.

## Quick start

### Option 1: Docker (Simple)

Execute the script below to start a MaxKB container using Docker:

```bash
docker run -d --name=maxkb --restart=always -p 18080:8080 -v ~/.maxkb:/opt/maxkb 1panel/maxkb
```

### Option 2: Docker Compose (Recommended for Local Services and Integration)

```bash
# 1. Copy and configure environment
cp .env.example .env
# Edit .env and set MAXKB_DEFAULT_PASSWORD (required!)

# 2. Initialize database
docker compose --profile init up --abort-on-container-exit --exit-code-from maxkb-init maxkb-init

# 3. Start services
docker compose up -d
```

### Configuration

**Required before first startup:**

Set a bootstrap admin password through `MAXKB_DEFAULT_PASSWORD` in your environment or `.env` file. There is **no default password** - you must set one explicitly.

**Access URLs:**

| Service | URL |
|---------|-----|
| Admin UI | `http://your_server_ip:18080/admin/` |
| Chat UI | `http://your_server_ip:18080/chat/` |

**Login credentials:**

- username: `admin`
- password: the bootstrap password you configured in `MAXKB_DEFAULT_PASSWORD`

The bootstrap password is intended for first use only. MaxKB will require the administrator to change it after the first login.

### Important: Port Selection

**Use port 18080 (default) or standard ports like 80, 443, 8080.**

Avoid using port **10080** - it is blocked by Chromium-based browsers (Chrome, Edge, Brave) due to security reasons (NAT Slipstreaming vulnerability). If you must use a non-standard port, ensure it's not in the [browser's blocked port list](https://chromium.googlesource.com/chromium/src.git/+/refs/heads/master/net/base/port_util.cc).

中国用户如遇到 Docker 镜像 Pull 失败问题，请参照该 [离线安装文档](https://maxkb.cn/docs/v2/installation/offline_installtion/) 进行安装。

## Development Environment

This repository follows a local-first development workflow. The backend should use a repo-local `.venv` managed by `uv`, and the frontend should use the local Node.js toolchain under `ui/`. Start Docker Compose only when the task requires PostgreSQL / Redis behavior, frontend-backend integration, worker-flow validation, or container-specific debugging.

Default local development convention:

- start the full local stack with `./dev.sh`
- start PostgreSQL and Redis with `docker compose -f docker-compose.dev.yml up -d`
- copy `.env.local-dev.example` to `.env.local-dev` and load it before starting Django
- run backend locally from `.venv`
- run frontend locally from `ui/`
- run Playwright against the local app stack

For local-first development, the backend dev server defaults to `127.0.0.1:3080` (configurable via `MAXKB_DEV_HOST` / `MAXKB_DEV_PORT`). Frontend dev proxy should target the same backend (for example with `VITE_API_TARGET=http://127.0.0.1:3080`).

See `DEVELOPMENT.md` for the full workflow.

## Testing

### Local test workflow

Start PostgreSQL and Redis first:

```bash
docker compose -f docker-compose.dev.yml up -d
```

Load the local backend environment before Django commands:

```bash
set -a
source .env.local-dev
set +a
```

Backend tests:

```bash
.venv/bin/python apps/manage.py test --verbosity=1 --noinput
```

Frontend unit and component tests:

```bash
cd ui
npm run test
npm run type-check
npm run lint
```

E2E tests:

```bash
cd ui
npx playwright test
```

Note: the remote-backed chat Playwright scenario depends on SiliconCloud credentials in `.env.local-dev` via `SILICONCLOUD_API_KEY`. Without that credential, the chat-specific spec is skipped.

### CI test workflow

The repository CI is expected to run these layers:

- backend Django test suite via `python apps/manage.py test --verbosity=1 --noinput`
- frontend type-check via `npm run type-check`
- frontend lint via `npm run lint`
- frontend unit/component tests via `npm run test`
- advisory Playwright E2E via `npx playwright test --grep-invert @deferred`

CI uses `MAXKB_*` environment variables, PostgreSQL, and Redis, matching the local-first workflow instead of a separate `DATABASE_URL`-style configuration.

Current CI status policy:

- **Required baseline**: Backend Tests, Frontend Tests
- **Advisory**: `E2E Tests (Advisory)`
- **Deferred**: credential-dependent Playwright coverage tagged `@deferred`, currently the remote-backed chat scenario

## Screenshots

<table style="border-collapse: collapse; border: 1px solid black;">
  <tr>
    <td style="padding: 5px;background-color:#fff;"><img src= "https://github.com/user-attachments/assets/eb285512-a66a-4752-8941-c65ed1592238" alt="MaxKB Demo1"   /></td>
    <td style="padding: 5px;background-color:#fff;"><img src= "https://github.com/user-attachments/assets/f732f1f5-472c-4fd2-93c1-a277eda83d04" alt="MaxKB Demo2"   /></td>
  </tr>
  <tr>
    <td style="padding: 5px;background-color:#fff;"><img src= "https://github.com/user-attachments/assets/c927474a-9a23-4830-822f-5db26025c9b2" alt="MaxKB Demo3"   /></td>
    <td style="padding: 5px;background-color:#fff;"><img src= "https://github.com/user-attachments/assets/e6268996-a46d-4e58-9f30-31139df78ad2" alt="MaxKB Demo4"   /></td>
  </tr>
</table>

## Technical stack

- Frontend：[Vue.js](https://vuejs.org/)
- Backend：[Python / Django](https://www.djangoproject.com/)
- LLM Framework：[LangChain](https://www.langchain.com/)
- Database：[PostgreSQL + pgvector](https://www.postgresql.org/)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=1Panel-dev/MaxKB&type=Date)](https://star-history.com/#1Panel-dev/MaxKB&Date)

## License

Licensed under The GNU General Public License version 3 (GPLv3)  (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

<https://www.gnu.org/licenses/gpl-3.0.html>

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
