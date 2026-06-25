# 项目状态与交接文档(PROJECT STATE)

> **重进会话先读这份。** 它告诉你:现在到哪了、分支状态、下一步做什么、关键路径、已定决策。
> 最近更新:2026-06-25(门户「黑白科技风」重构 + 第 6 个 demo IconForge 图标净化器均已完成,**已合并入 `master` 并推送 `origin/master`**(HEAD `80cf289`);本地 Docker 全路由 200;**生产服务器尚未重新部署**,待用户触发)

---

## 一句话现状

ai-demos 已重构为 monorepo,「个人集成学习网站」**Phase 1 已完成并在本地 docker-compose 跑通**;`feat/portfolio-phase1`(13 个提交,20 测试通过)**已合并入 `master`**。**Nexus Phase 2 已完成并合并入 `master`**(14 个提交,39 测试通过),新增 `/nexus/` Multi-Agent 工作流助手(FastAPI + SSE + 通义千问)。**DocHub 已完成并合并入 `master`**(19 个提交,59 测试通过),新增 `/doctomd/` Markdown 转 HTML 文档站(上传/路径转换/在线浏览/密码保护/CLI)。**Phase 4 服务器部署已完成**:项目已部署到韩国首尔阿里云轻量服务器(Ubuntu 24.04 LTS + Docker),通过 `https://www.shiyuan-wreg.cloud` 对外提供统一门户,Let's Encrypt SSL 证书已生效,所有子路径(`/rag/`、`/fc/`、`/nexus/`、`/doctomd/`、`/learn/`)及后端代理均验证通过。`master` **已推送**到 GitHub `origin/master`。

**新增:门户「黑白科技风」重构 + IconForge 图标净化器(第 6 个 demo)** 已完成并 **合并入 `master`、推送 `origin/master`(HEAD `80cf289`,从 worktree `feat+portfolio-ui-redesign` 快进合并)**。门户改版:默认主题 `mono-light`,科技 hero(glitch 标题/打字机/假终端)、用户提供的 SVG logo 与 5 个 demo 图标、WorkCard 纯黑白四特效选中态、全局网格/噪点质感、等宽元信息字体。IconForge(`/iconforge/`):无状态 FastAPI 服务(端口 8005,照搬 DocHub 接线),三操作自选(位图转矢量 Pillow+potrace / 去白边 / 彩色转黑),原生 JS 单页 UI(亮暗双预览/下载/复制);容器内 27 测试全绿(含真实 potrace),本地全栈 9 路由 200。**生产服务器尚未重新部署**——待用户触发后,服务器 `git pull` + `build-frontends` + `compose up --build`(注意 iconforge 首次构建会 apt 装 potrace)。本地起栈用 `docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml up -d --build`。

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
2. 仓库根有 `.env`(含 `DASHSCOPE_API_KEY`)
3. `bash deploy/build-frontends.sh`
4. `docker compose -f deploy/docker-compose.yml up -d --build`
5. 访问 http://127.0.0.1:8080

---

## 待处理 / 下一步(按优先级)

1. **~~决定分支去向~~ ✅ 已完成**:`feat/portfolio-phase1` 已合并入 `master`(线性历史/快进,分支已删)。
2. **~~删 agent-console-ai 残留目录~~ ✅ 已解决**:目录已删除,无残留。
3. **~~Phase 2 实现计划已确认:Nexus Web 后端~~ ✅ 已完成**:Nexus Phase 2 已实现并合并入 `master`,包括 FastAPI SSE 后端、chat 前端、fc_app `/execute`、Docker/compose/nginx/portfolio 集成;本地测试 39 通过(除 rag 测试),Docker compose 验证待 Docker Desktop 启动。
4. **~~DocHub 实现计划已确认:Markdown 文档站~~ ✅ 已完成**:DocHub 已实现、合并入 `master` 并推送,包括上传/路径转换、全局索引、在线浏览、密码认证、CLI、Docker/compose/nginx/portfolio 集成;本地测试 59 通过(除 rag 测试)。
5. **~~Phase 4~~ ✅ 已完成**:已部署到韩国首尔阿里云轻量服务器(Ubuntu 24.04 LTS + Docker)，域名 `www.shiyuan-wreg.cloud`，全站 HTTPS，所有路径和后端代理验证通过。生产 `.env` 已上传到 `/opt/ai-demos/.env`；SSH 走本地代理 `127.0.0.1:7890`（见 `.claude/ssh_config`）。
6. **门户外壳「黑白高级感科技风」重构 + IconForge 第 6 个 demo ✅ 已完成(在 worktree,待合并)**:默认 `mono-light` 主题,科技 hero,纯黑白选中特效,已替换用户提供的 SVG logo 和 5 个 demo 图标,Lucide 可替换图标,等宽元信息字体,全局网格/噪点质感。新增 IconForge 图标净化器(`/iconforge/`,FastAPI+Pillow+potrace,无状态,三操作自选)。worktree 内 12 个任务全部完成并通过本地 Docker 验证,当前 HEAD `140a3bc`,待用户最终视觉确认后合并入 `master` 并重新部署首尔服务器。
7. **Phase 3**:cs-quiz-app 完整集成(Fastify+SQLite 容器 + `/quiz` 静态前端);个人页目前只有占位链接。
8. **后续**:博客;把 demo 由 iframe 逐个重写为原生 React(演进到方案 A)。

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
