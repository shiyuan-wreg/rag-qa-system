# 项目状态与交接文档(PROJECT STATE)

> **重进会话先读这份。** 它告诉你:现在到哪了、分支状态、下一步做什么、关键路径、已定决策。
> 最近更新:2026-06-26(**修复 Nexus retriever 的 httpx async bug;LLM 出口整体切到 DeepSeek 聊天 + Jina embedding,已部署服务器并三 demo 实测通过**;HEAD `36e9c56`)

---

## 一句话现状

ai-demos 已重构为 monorepo,「个人集成学习网站」**Phase 1 已完成并在本地 docker-compose 跑通**;`feat/portfolio-phase1`(13 个提交,20 测试通过)**已合并入 `master`**。**Nexus Phase 2 已完成并合并入 `master`**(14 个提交,39 测试通过),新增 `/nexus/` Multi-Agent 工作流助手(FastAPI + SSE + 通义千问)。**DocHub 已完成并合并入 `master`**(19 个提交,59 测试通过),新增 `/doctomd/` Markdown 转 HTML 文档站(上传/路径转换/在线浏览/密码保护/CLI)。**Phase 4 服务器部署已完成**:项目已部署到韩国首尔阿里云轻量服务器(Ubuntu 24.04 LTS + Docker),通过 `https://www.shiyuan-wreg.cloud` 对外提供统一门户,Let's Encrypt SSL 证书已生效,所有子路径(`/rag/`、`/fc/`、`/nexus/`、`/doctomd/`、`/learn/`)及后端代理均验证通过。`master` **已推送**到 GitHub `origin/master`。

**新增:门户「黑白科技风」重构 + IconForge 图标净化器(第 6 个 demo)** 已完成、合并入 `master`,**并于 2026-06-25 部署到首尔生产服务器(HEAD `ee8ff6e`)**。生产 `https://www.shiyuan-wreg.cloud` 全 8 路由 HTTPS 200 验证通过。门户改版:默认主题 `mono-light`,科技 hero(glitch 标题/打字机/假终端)、用户提供的 SVG logo 与 5 个 demo 图标、WorkCard 纯黑白四特效选中态、全局网格/噪点质感、等宽元信息字体。IconForge(`/iconforge/`):无状态 FastAPI 服务(端口 8005,照搬 DocHub 接线),三操作自选(位图转矢量 Pillow+potrace / 去白边 / 彩色转黑),原生 JS 单页 UI(亮暗双预览/下载/复制)。本地起栈用 `docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml up -d --build`。

**部署中修复的两个 bug(已提交推送):**
- `2099d78` fix(portfolio): 补 `/iconforge` SPA 路由(App.tsx 漏了,点卡片空白页)。
- `ee8ff6e` fix(portfolio): 把 `@fontsource/inter` + `@fontsource/jetbrains-mono` 写进 package.json(原先靠用户主目录幽灵 node_modules,服务器干净 clone 构建失败)。

**已知待改进(2026-06-26 更新):**
1. IconForge 工具体验差(用户反馈),后续迭代净化效果。
2. **~~生产 RAG/LLM 出口~~ ✅ 已解决(2026-06-26)**:LLM 出口从大陆 dashscope 整体切到 **DeepSeek(聊天,OpenAI 兼容)+ Jina(RAG embedding)**,两者从首尔均可达、已实测有效。聊天统一走 `core/llm.py` 的 `LLMClient.from_config()`(provider=openai/model=deepseek-chat/base_url=api.deepseek.com);embedding 走 `rag/vectorstore.py` 里手写的最小 Jina 客户端。服务器 `.env` 用 `LLM_PROVIDER/LLM_MODEL/LLM_BASE_URL/LLM_API_KEY/JINA_API_KEY`(旧 `DASHSCOPE_*` 留作回退)。三 demo 生产实测:FC 工具调用、RAG Jina 检索作答、Nexus SSE 均通过。**切 DeepSeek 时暴露并修了一个老 bug**:`safe_execute_python` 是受限算术计算器,但描述像通用执行器,DeepSeek 会发整段程序导致 `/rag/` 死循环——已改描述/报错/system prompt 修正。
3. **~~Nexus retriever pre-existing async bug~~ ✅ 已修复(2026-06-26,HEAD `36e9c56`)**:根因是 httpx 的 `Response.raise_for_status()`/`json()` 在 `AsyncClient` 下仍是**同步**方法(只有 `aread()`/`aclose()` 是协程),原代码对它们误用 `await` → `object Response can't be used in 'await' expression`。改为同步调用并移除多余 `aread()`。**漏测原因**:旧测试用 `AsyncMock` 模拟这两个方法,让错误的 await 假通过;已改 `MagicMock` 反映真实行为。nexus 核心 17 测试通过。
4. RAG `chroma_db` 未挂卷,每次重建容器重新调 Jina 建库(7 块,快,可接受);`init_rag_tool` 仍在 import 路径同步执行。

---

## 这个项目是什么

把多个分散的 Web 项目整合成一个统一作品集门户,部署到自有域名+云服务器,作为 **AI/Agent 求职方向**的代表作。整合方案 = **方案 C(统一 React 外壳 + iframe 嵌入各 demo)**。

- 设计文档(spec):`docs/superpowers/specs/2026-06-22-personal-portfolio-integration-design.md`
- Phase 2 设计(spec):`docs/superpowers/specs/2026-06-23-nexus-phase2-design.md`
- DocHub 设计(spec):`docs/superpowers/specs/2026-06-23-dochub-design.md`
- 实现计划(plan):`docs/superpowers/plans/2026-06-22-portfolio-phase1-monorepo-and-shell.md`
- 配套学习文档:`docs/learning/portfolio-integration-guide.md`(+ .docx)
- 本地运行步骤:`deploy/README.md`

---

## Phase 1 交付内容(已完成)

- monorepo 重组:`backends/`(rag_app, fc_app)、`frontends/`(portfolio, nexus-learning-web)、`deploy/`
- 清理:抽离 `agent-console-ai`(独立到桌面)、删除 `legacy/`
- React 门户外壳:首页作品网格 + 导航 + iframe demo 页(技术说明面板)+ 学习跳转 + 个人页
- docker-compose:nginx(8080)反代 rag(8001)/fc(8002)+ 托管静态门户与学习站
- 本地验证:`/ /me /rag/ /fc/ /learn/` 全 200;子路径反代验证通过(POST /rag/clear、/fc/clear 命中后端)

### 当前如何跑起来
1. Docker Desktop 要先启动
2. 仓库根有 `.env`(现在含 `LLM_PROVIDER=openai` / `LLM_MODEL=deepseek-chat` / `LLM_BASE_URL=https://api.deepseek.com` / `LLM_API_KEY=<deepseek>` / `JINA_API_KEY=<jina>`;旧 `DASHSCOPE_API_KEY` 留作回退)
3. `bash deploy/build-frontends.sh`
4. 本地起栈(带 local 覆盖,端口 8080):
   `docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml up -d --build`
5. 访问 http://127.0.0.1:8080
6. **注意**:中国大陆本机直连 `api.jina.ai` 不通(超时),但 Docker 容器内能连;首尔服务器两者都通。所以本地 RAG 检索由容器跑,没问题。

---

## 待处理 / 下一步(按优先级)

0. **~~修 Nexus retriever 的 async bug~~ ✅ 已完成**(2026-06-26,HEAD `36e9c56`):见上文「已知待改进 #3」。本地 nexus 核心 17 测试通过;`tests/fc/test_execute.py` 仍因本机 venv 未装 `openai` 包(容器内有)收集失败,与本修复无关。**待补**:Docker 起栈后跑一条真实 Nexus 流程,确认 retriever 的 `tool_result` 不再是「检索失败」;服务器同验。
1. **~~决定分支去向~~ ✅ 已完成**:`feat/portfolio-phase1` 已合并入 `master`(线性历史/快进,分支已删)。
2. **~~删 agent-console-ai 残留目录~~ ✅ 已解决**:目录已删除,无残留。
3. **~~Phase 2 / DocHub / Phase 4 部署 / 黑白改版+IconForge~~ ✅ 均已完成并部署**(详见上文与 dev-log)。
4. **~~LLM 出口切 DeepSeek + Jina~~ ✅ 已完成并部署**(2026-06-26,HEAD `a73e769`,三 demo 生产实测通过)。
5. **Phase 3**:cs-quiz-app 完整集成(Fastify+SQLite 容器 + `/quiz` 静态前端);个人页目前只有占位链接。
6. **后续**:IconForge 净化效果迭代;博客;把 demo 由 iframe 逐个重写为原生 React(演进到方案 A);RAG `chroma_db` 持久化挂卷 + `init_rag_tool` 挪出 import 路径。

## 当前可用路径(本地 Docker 启动后)

```bash
bash deploy/build-frontends.sh
docker compose -f deploy/docker-compose.yml up -d --build
```

访问 http://127.0.0.1:8080:

| 路径 | 服务 |
|---|---|
| `/` | 门户首页 |
| `/rag/` | RAG 文档问答 |
| `/fc/` | Function Calling Agent |
| `/nexus/` | Nexus Multi-Agent 工作流 |
| `/doctomd/` | DocHub Markdown 文档站 |
| `/learn/` | Nexus 交互式学习站 |
| `/iconforge/` | IconForge 图标净化器 |

## 当前状态

- `master` 已推送至 `origin/master`
- 无未合并 feature 分支
- **本地 Docker 验证已通过**（访问 http://127.0.0.1:8080，所有路径 200，后端代理正常）
- **服务器部署已完成**：`https://www.shiyuan-wreg.cloud` 已对外提供服务，SSL 证书有效，HTTP 自动跳转 HTTPS，所有子路径及后端代理正常
- **生产环境信息**：服务器 IP `8.213.145.110`（阿里云首尔），OS `Ubuntu 24.04 LTS`，部署目录 `/opt/ai-demos`，DocHub 密码见 `.env`

---

## 已定决策(不要重新讨论)

- **求职主方向 = AI/Agent 开发**;二进制安全降为副方向(2026-06-22 确认)。
- **整合方案 = C**(统一外壳 + iframe),可逐步演进到 A。
- **首页/个人页不放姓名、自我介绍、学校**(要"普通网站"观感);站点标题「个人集成学习网站」。
- **本地优先**:先本地 docker-compose 跑通,再部署服务器(服务器+域名已购,韩国首尔,免备案)。
- **系统镜像走纯净 Ubuntu + Docker**(不用宝塔),练部署硬技能。
- **agent-console-ai 是独立课程设计(鸿蒙前端),不并入 ai-demos**;如需 ai-demos 的 agent 问答能力,走 **HTTP API 调用沿用**(鸿蒙端指向 ai-demos 部署的 /rag 或 /fc 接口),不合并代码/仓库。对接契约文档:`docs/api-integration-for-harmonyos.md`(给鸿蒙端开发者/AI 阅读)。

---

## 关键环境事实

- 仓库:`C:/Users/hzs17/Desktop/ai-demos`,Windows + Git Bash。
- 工具:Node v20、npm v10、Docker 28 + Compose v2(Docker Desktop 需手动启动)。
- 国内拉 Docker Hub 镜像易超时:先 `docker pull nginx:1.27-alpine` 和 `python:3.12-slim` 预缓存,或配镜像加速器。
- LLM 用通义千问(dashscope),`DASHSCOPE_API_KEY` 在仓库根 `.env`(未跟踪)。
- SDD 进度账本:`.git/sdd/progress.md`。
- **远程**:`origin` = github `shiyuan-wreg/rag-qa-system.git`;**`master` 已推送**。
- **docker stack 当前已关闭**(2026-06-22 存档时 `compose down`);恢复运行见 `deploy/README.md`(build-frontends + compose up)。
- **所有 feature 分支已清理**:无未合并工作分支。

---

## 分支提交链(feat/portfolio-phase1)

```
b1ac9a2 docs: fix stale paths after reorg; harden gitignore; add rel=noopener
0551cd9 docs: add local run guide; Phase 1 portfolio runs via docker-compose
73ccad7 fix: relative fetch paths in RAG/FC demos for /rag/ /fc/ subpath proxy
dd9ba13 build: enforce LF for shell/Dockerfile/conf via .gitattributes
08e8715 build: add docker-compose orchestration and frontend build script
cbcdb77 build: add nginx reverse-proxy + static hosting config
b11d4a9 build: add Dockerfiles for rag_app and fc_app
98e242d feat: add portfolio shell (React+Vite+TS+Tailwind) with router, nav, pages
21c78d9 refactor: move nexus-learning-web into frontends/ with /learn base
2a30b8b chore: remove legacy demos (preserved in git history)
edbf7ff refactor: promote FC agent web to backends/fc_app
0fc7775 refactor: move RAG web app to backends/rag_app
0e074c6 chore: scaffold monorepo dirs (backends/ frontends/ deploy/)
79287b0 chore: remove agent-console-ai (extracted to standalone course project)
```
(起点 merge-base: fea1610)
