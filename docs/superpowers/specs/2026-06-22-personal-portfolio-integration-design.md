# 个人集成学习网站 — Web 项目整合设计文档

- **文档日期**：2026-06-22
- **项目代号**：个人集成学习网站（Portfolio Hub）
- **工作标题**：个人集成学习网站（可后续更名）
- **项目定位**：把现有多个独立 Web 项目整合为一个统一门户，部署到自有域名+云服务器，作为 AI/Agent 求职方向的作品集
- **当前状态**：设计阶段，待实现
- **整合方案**：方案 C（统一外壳 + iframe 嵌入），可逐步演进为方案 A（全栈重构）

---

## 1. 项目概述

把分散的多个 Web 项目整合成**一个统一的作品集门户站点**，跑在用户自有的云服务器（韩国首尔，免备案）和域名上，访客点开网址即可浏览全部作品。门户对外只有一个入口（Nginx），后面挂多个后端服务和静态站点。

### 1.1 整合前的项目清单

| 项目 | 原位置 | 技术栈 | 形态 |
|---|---|---|---|
| RAG 问答 | `ai-demos/app.py` | FastAPI + 内联 HTML | 单文件全栈 |
| Function Calling | `ai-demos/legacy/agent_app.py` | FastAPI + 内联 HTML | 单文件全栈 |
| Nexus 多智能体 | `ai-demos/core/agents/` | Python（仅命令行） | 无 Web 界面 |
| Nexus 学习站点 | `ai-demos/nexus-learning-web` | React + Vite + TS | 纯前端 SPA |
| cs-quiz-app 面试题库 | `桌面/cs-quiz-app` | React + Vite + Fastify + SQLite | 全栈 |

### 1.2 成功标准

1. **统一**：所有作品在同一域名、同一导航外壳下，访客感觉是"一个站"。
2. **能发链接**：面试时发一个网址，招聘方点开即可浏览、并真实交互试用 AI demo。
3. **可讲**：每个 AI demo 配技术说明面板，把"工具"变成"能讲的作品"。
4. **可复现**：本地与线上用同一份 docker-compose，部署即"搬迁"。
5. **可演进**：先用 iframe 嵌入快速上线，后续逐个把 demo 重写为原生 React，平滑升级到方案 A。

### 1.3 非目标（YAGNI）

- 博客功能：列入后续阶段（Phase 2），不进首期 MVP。
- 用户系统 / 登录：门户为公开展示站，无需登录。
- 本地大模型 / 本地 embedding：2G 内存不支持，一律走云端 API。

---

## 2. 总体架构

### 2.1 架构图

```
                    自有域名 (https)
                         │
                    ┌────▼────┐
                    │  Nginx  │   唯一对外入口 (80/443)，TLS 终止
                    └────┬────┘
        ┌────────────────┼─────────────────────────┐
        │ 静态文件         │ 反向代理 (/rag /fc /nexus /api/*)
        ▼                ▼                           ▼
  门户外壳(React)    FastAPI 后端进程              Node 后端
  /        首页+导航   127.0.0.1:8001 RAG          127.0.0.1:8004
  /learn   学习站      127.0.0.1:8002 Function     cs-quiz Fastify
  /quiz前端 刷题界面    127.0.0.1:8003 Nexus        + SQLite
  /me      个人页
```

### 2.2 路由与端口分配

| 访客路径 | 内容 | 后端 | 嵌入方式 |
|---|---|---|---|
| `/` | 门户首页 | 纯静态 | 门户外壳本体 |
| `/me` | 个人页 | 纯静态 | 门户外壳路由 |
| `/rag` | RAG 问答 demo | FastAPI :8001 | iframe 嵌入 |
| `/fc` | Function Calling demo | FastAPI :8002 | iframe 嵌入 |
| `/nexus` | Nexus 多智能体 demo | FastAPI :8003 | iframe 嵌入 |
| `/learn` | Nexus 学习站点 | 纯静态 | 子路径静态托管 |
| `/quiz` | cs-quiz 刷题 | Fastify :8004 + SQLite | 个人页链接进入 |

### 2.3 关键原则

- **所有后端只监听 `127.0.0.1`**，不直接对公网暴露，统一由 Nginx 转发。API Key 安全地待在后端，绝不进浏览器。
- **后端进程用 docker-compose 编排**，开机自启 + 崩溃自动重启。
- **前端均构建为静态文件**，由 Nginx 直接托管，不单独占容器。

---

## 3. 仓库结构（monorepo）

在现有 `ai-demos` 仓库内扩展，顺势完成"整合"：

```
ai-demos/
├── core/ rag/ eval/              现有 Nexus 内核（不动）
├── backends/                     [新增] 所有后端进程归一处
│   ├── rag_app/                  ← 由 app.py 迁入
│   ├── fc_app/                   ← 由 legacy/agent_app.py 提升迁入
│   └── nexus_app/                ← [新建] Nexus 多智能体 Web 后端
├── frontends/                    [新增] 所有前端归一处
│   ├── portfolio/                ← [新建] React 门户外壳（首页/导航/个人页）
│   ├── nexus-learning-web/       ← 由现有位置迁入
│   └── cs-quiz-app/              ← 从桌面拷入（前端 + Fastify + SQLite）
├── deploy/                       [新增] nginx 配置 / docker-compose / 部署脚本
│   ├── docker-compose.yml
│   ├── nginx/                    nginx 配置文件
│   └── README.md                 部署步骤
└── docs/                         现有文档 + 本设计文档
```

约定：
- 现有 Python 内核（`core/` `rag/`）**原地不动**，只把 Web 后端集中到 `backends/`，降低改动风险。
- `cs-quiz-app` 从桌面**拷贝**进来（不做 git submodule，简单为主；代价是独立提交历史不带过来）。
- `deploy/` 集中管理部署相关文件，搬服务器全靠它。

---

## 4. 门户外壳与各页面

### 4.1 外壳技术栈

React + Vite + TS + Tailwind，与现有 `nexus-learning-web` 完全一致，视觉语言统一、组件可复用。路由用 React Router。

### 4.2 页面结构

```
门户外壳（顶部导航：首页 · AI作品 · 学习 · 个人）
│
├── /            首页
│                ├─ 站点标题「个人集成学习网站」+ 一句话说明（不含姓名/个人信息）
│                └─ 作品卡片网格：RAG / Function Calling / Nexus / 学习站
│
├── /rag /fc /nexus   每个 = 导航 + iframe 嵌入 demo + 技术说明面板
│
├── /learn       学习站点（nexus-learning-web）
│
└── /me（个人）  个人页：技能栈 / 方向、简历下载、项目列表（含 cs-quiz → /quiz）
                 （无姓名 Hero、无自我介绍、无头像、无学校 —— 保持普通网站形态）
```

### 4.3 AI demo 页 = iframe + 技术说明面板

每个 demo 页除了 iframe 嵌入的可交互界面，配一个**技术说明面板**：
- 这个 demo 解决什么问题
- 用了什么技术（RAG / Function Calling / 多智能体 / 通义千问 / Chroma）
- 作者在其中做了什么、难点是什么
- GitHub 源码链接

这一步把"一个能玩的工具"变成"一件能讲的作品"，是门户对求职最关键的部分。

---

## 5. 后端整合与 docker-compose 编排

### 5.1 容器划分

| 容器 | 内容 | 内部端口 | 持久化数据 |
|---|---|---|---|
| `nginx` | 唯一入口 + 静态托管 + 反代 | 80/443 对外 | — |
| `rag` | RAG 问答（由 app.py 迁入） | 8001 | Chroma 向量库（volume） |
| `fc` | Function Calling（由 legacy 迁入） | 8002 | — |
| `nexus` | Nexus 多智能体（新建） | 8003 | — |
| `quiz` | cs-quiz Fastify | 8004 | SQLite 文件（volume） |

前端（portfolio / nexus-learning-web / cs-quiz 前端）构建为静态文件，由 nginx 托管。

### 5.2 Nexus Web 后端（本次最大新增）

设计目标：让访客**直观看到多智能体协作过程**。

- 新建 FastAPI 应用，内部启动消息总线 + 现有 `core/agents`（Orchestrator/Planner/Retriever/Executor/Summarizer/Critic）。
- 提供聊天接口，用户输入问题后后端跑完整工作流。
- **用 SSE（Server-Sent Events，服务器推送）把中间步骤实时吐给前端**，前端逐步显示：
  `Planner 拆解中… → Retriever 检索… → Executor 执行… → Summarizer 汇总… → Critic 评分`。
- 前端页面延续其它 demo 的"内联 HTML"风格（与 rag/fc 一致，便于 iframe 嵌入）：左侧对话、右侧"智能体步骤流"。

这个"看得见的多智能体协作"是面试时最能讲故事的一幕。

### 5.3 安全与数据

- API Key 走 `.env` 文件 + docker 环境变量注入，**只在后端容器里，绝不进镜像、绝不进前端**。
- `.env` 已在 `.gitignore` 中；线上服务器单独放一份 `.env`。
- SQLite 与 Chroma 数据用 **named volume** 持久化，容器重建数据不丢。

### 5.4 资源应对（2G 内存）

- 每个 Python 服务**单 worker**、**懒加载重依赖**（langchain/embedding 用到才导入）。
- 服务器加 **2G swap**。
- RAG 的 Chroma 用小知识库，够演示即可。

---

## 6. 部署：服务器、域名、HTTPS

### 6.1 服务器准备（韩国首尔，纯净 Ubuntu 22.04）

1. 重装系统为纯净 Ubuntu 22.04（不用宝塔，走 Docker 路线）。
2. 创建 2G swap，防止内存瞬间打满。
3. 安装 Docker + docker-compose。
4. 云服务器安全组放行 80 / 443，SSH 端口建议改非默认值。

### 6.2 域名解析

- 在域名控制台加一条 **A 记录**，把域名指向服务器公网 IP。
- 等待 DNS 生效（通常几分钟到几十分钟）。

### 6.3 HTTPS

- 用 Let's Encrypt 免费证书（如 `certbot` 或 nginx 容器内的 acme 方案）。
- Nginx 配置 80 自动跳转 443。

### 6.4 部署流程

1. 服务器上 `git clone` 仓库（或 git pull 更新）。
2. 放好线上 `.env`。
3. `docker compose -f deploy/docker-compose.yml up -d --build`。
4. 访问域名验证。

---

## 7. 错误处理

| 场景 | 处理方式 |
|---|---|
| 某个后端容器崩溃 | docker-compose `restart: always` 自动重启 |
| 大模型 API 超时/报错 | 后端捕获异常，前端显示友好错误，不影响门户其它页面 |
| iframe 加载失败 | demo 页显示降级提示 + GitHub 链接 |
| 内存不足 | swap 兜底；必要时减少并发 worker |
| API Key 失效 | 后端日志记录，前端提示"服务暂不可用" |

各 demo 相互隔离：一个挂掉不影响其它页面和门户首页。

---

## 8. 测试策略

- **后端**：沿用现有 pytest，新增 Nexus Web 后端的接口测试（SSE 流、错误分支）。
- **前端**：门户外壳的路由/导航手动验证；构建产物 `npm run build` 必须无错。
- **集成**：本地 `docker compose up` 后逐路径验证（`/` `/rag` `/fc` `/nexus` `/learn` `/quiz` `/me`）。
- **部署冒烟**：线上访问每个路径，确认 demo 可实时交互、HTTPS 生效。

---

## 9. 实施阶段建议

| 阶段 | 内容 |
|---|---|
| Phase 1 | monorepo 重组（迁移 backends/ frontends/）+ 门户外壳 + iframe 集成，本地 docker-compose 跑通 |
| Phase 2 | Nexus Web 后端（SSE 多智能体可视化） |
| Phase 3 | 部署到首尔服务器 + 域名 + HTTPS |
| Phase 4（后续） | 博客功能；把 demo 从 iframe 逐个重写为原生 React（演进到方案 A） |

---

## 10. 风险与权衡

- **iframe 的局限**：高度自适应、样式隔离需处理；这是方案 C 为了快速上线接受的代价，后续演进可消除。
- **2G 内存偏紧**：靠单 worker + 懒加载 + swap 缓解；若后续作品增多需升配。
- **首尔节点调大陆 API 有额外延迟**：对 demo 体验影响小，可接受。
- **cs-quiz 拷入丢历史**：个人项目可接受。
