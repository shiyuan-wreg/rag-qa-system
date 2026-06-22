# 项目状态与交接文档(PROJECT STATE)

> **重进会话先读这份。** 它告诉你:现在到哪了、分支状态、下一步做什么、关键路径、已定决策。
> 最近更新:2026-06-22(分支已合并入 master,清理收尾)

---

## 一句话现状

ai-demos 已重构为 monorepo,「个人集成学习网站」**Phase 1 已完成并在本地 docker-compose 跑通**;`feat/portfolio-phase1`(13 个提交,20 测试通过)**已合并入 `master`(线性历史,分支已删除)**。`master` 本地领先 `origin/master` 36 提交,**尚未推送**。

---

## 这个项目是什么

把多个分散的 Web 项目整合成一个统一作品集门户,部署到自有域名+云服务器,作为 **AI/Agent 求职方向**的代表作。整合方案 = **方案 C(统一 React 外壳 + iframe 嵌入各 demo)**。

- 设计文档(spec):`docs/superpowers/specs/2026-06-22-personal-portfolio-integration-design.md`
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
2. **删 agent-console-ai 残留目录**:`ai-demos/agent-console-ai` 现已是**空目录**(内容已清),但目录节点仍被某进程(疑似 DevEco Studio)句柄锁定,`rm`/`Remove-Item` 均报 busy。未被 git 跟踪,无功能影响。**重启一次即可 `rm -rf` 清除**。桌面独立副本(`C:/Users/hzs17/Desktop/agent-console-ai`,commit d02f65d,1515 文件)已完整。
3. **Phase 2**:Nexus Web 后端(FastAPI + SSE 多智能体可视化)→ `backends/nexus_app`,门户加 `/nexus`。
4. **Phase 3**:cs-quiz-app 完整集成(Fastify+SQLite 容器 + `/quiz` 静态前端);个人页目前只有占位链接。
5. **Phase 4**:部署到首尔服务器(Ubuntu + swap + Docker + 域名 A 记录 + Let's Encrypt HTTPS)。
6. **后续**:博客;把 demo 由 iframe 逐个重写为原生 React(演进到方案 A)。

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
- **远程**:`origin` = github `shiyuan-wreg/rag-qa-system.git`;**本地已提交但未推送**(到 2026-06-22 为止)——需要时再 `git push`(对外动作,需用户确认)。
- **docker stack 当前已关闭**(2026-06-22 存档时 `compose down`);恢复运行见 `deploy/README.md`(build-frontends + compose up)。

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
