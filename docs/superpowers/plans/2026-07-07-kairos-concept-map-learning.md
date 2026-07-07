# Kairos 概念地图学习法实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建 `docs/learning/kairos-concept-map.md`，以 Kairos 项目为中心建立技术概念地图，完成 15 个核心节点的 7 字段填充，并配套学习决策树与面试问法汇总。

**Architecture:** 文档即交付物。概念地图采用"6 大层级 + 子分类"的树状结构；每个节点使用统一的 7 字段模板（定义/存在原因/项目使用位置/相邻关系/面试问法/坑点/资源）；学习方法决策树和面试问法汇总作为独立章节Append在最后。

**Tech Stack:** Markdown，无需代码依赖。

## Global Constraints

- 主文档路径固定为 `docs/learning/kairos-concept-map.md`
- 每个核心节点必须包含 7 个字段：一句话定义、为什么存在、Kairos 哪里用了、和相邻概念的关系、常见面试问法、我踩过的坑/注意点、推荐学习资源
- 15 个核心节点清单固定：Git、Docker、Docker Compose、Nginx、Python、FastAPI、Uvicorn、RAG、FC、React、Vite、TypeScript、TailwindCSS、LLM、Function Calling、HTTP/REST API
- 所有内容必须与 Kairos 项目实际代码/配置对应，禁止编造
- 历史学习文档保持原样，不修改
- 每次 task 完成后独立验证；最终验收以"用户能口头解释每个核心节点"为标准

---

## File Structure

- **Create**: `docs/learning/kairos-concept-map.md`
  - 负责：承载完整概念地图、7 字段节点、学习决策树、面试问法汇总
- **Read-only reference** (实施时需要查看):
  - `docs/superpowers/specs/2026-07-07-kairos-concept-map-learning-design.md`
  - `deploy/docker-compose.yml`
  - `frontends/portfolio/package.json`
  - `backends/*/Dockerfile` / `backends/*/main.py`
  - 其他项目文件用于确认概念在项目中的实际使用位置

---

## Task 1: 创建概念地图骨架

**Files:**
- Create: `docs/learning/kairos-concept-map.md`

**Interfaces:**
- Consumes: design doc 中的 6 大层 + 子分类结构
- Produces: 一个只有层级标题、无节点内容的空地图骨架

- [ ] **Step 1: 创建主文档并写入顶层标题与简介**

```markdown
# Kairos 技术概念地图

> 以 Kairos 项目为中心，按层级组织技术概念。每个概念统一使用 7 字段模板。  
> 使用方式：遇到新概念时，先判断它属于哪一层，再按模板补充。

## 使用决策树

```
1. 这个概念在 Kairos 里出现吗？
   ├── 是 → 放入地图对应层级
   └── 否 → 放入"待归档区"
2. 它是基础概念还是高级特性？
   ├── 基础概念 → 填完 7 个字段，能口头解释
   └── 高级特性 → 只填定义/原因/相关概念
3. 它影响项目运行吗？
   ├── 是 → 必须找到代码/配置中的实际使用位置
   └── 否 → 了解即可
4. 我现在能讲清楚吗？
   ├── 能 → 标记 ✅
   └── 不能 → 24 小时内再复习一次
```

## 1. 基础设施层

### 1.1 版本控制

#### Git
#### GitHub

### 1.2 容器化

#### Docker
#### Docker Compose

### 1.3 Web 服务器与代理

#### Nginx

### 1.4 服务器与运维

#### Linux / SSH / 域名与 SSL

## 2. 后端服务层

### 2.1 语言与运行时

#### Python
#### Uvicorn

### 2.2 Web 框架

#### FastAPI

### 2.3 各 demo 后端

#### RAG
#### FC
#### Nexus
#### DocHub
#### IconForge

### 2.4 共享核心模块

#### core/agent.py
#### core/llm.py
#### core/rag_tool.py

## 3. 前端门户层

### 3.1 语言与类型

#### TypeScript
#### JavaScript（ES6+）

### 3.2 UI 框架

#### React

### 3.3 样式

#### TailwindCSS

### 3.4 构建与路由

#### Vite
#### React Router

### 3.5 门户与 demo 集成

#### iframe 嵌入机制

## 4. AI / Agent 能力层

### 4.1 大模型基础

#### LLM（DeepSeek）
#### Token / Prompt / Completion
#### 温度 / 上下文窗口

### 4.2 嵌入与检索

#### Embedding（Jina）
#### 向量数据库（Chroma）

### 4.3 Agent 模式

#### RAG 流程
#### Function Calling
#### Multi-Agent 协作

### 4.4 评估与监控

#### 测试用例 / eval

## 5. 数据与存储层

### 5.1 向量数据

#### Chroma

### 5.2 结构化数据

#### SQLite

### 5.3 文档数据

#### Markdown
#### HTML

### 5.4 静态资源

#### 图片 / 字体 / dist

## 6. 工具链与开发体验

### 6.1 包管理

#### npm
#### pip

### 6.2 测试

#### pytest

### 6.3 终端与脚本

#### Git Bash
#### shell 脚本

### 6.4 AI 辅助开发

#### Claude Code

## 面试问法汇总

（待 Task 8 填充）
```

- [ ] **Step 2: 验证骨架层级完整**

```bash
# 统计层级标题
grep -c "^### " docs/learning/kairos-concept-map.md
```

Expected: 至少 20 个 `### ` 三级标题（6 大层下的子分类 + 具体概念占位）。

- [ ] **Step 3: 提交**

```bash
git add docs/learning/kairos-concept-map.md
git commit -m "docs(learning): create Kairos concept map skeleton"
```

---

## Task 2: 写入 Docker 示例节点

**Files:**
- Modify: `docs/learning/kairos-concept-map.md`

**Interfaces:**
- Consumes: Task 1 创建的骨架
- Produces: 一个完整的 7 字段示例节点，作为后续 14 个节点的模板

- [ ] **Step 1: 打开文档并定位到 Docker 占位**

- [ ] **Step 2: 替换 Docker 占位为完整 7 字段节点**

```markdown
#### Docker

- **一句话定义**：把应用和运行环境打包成"容器"，保证在不同机器上运行结果一致。
- **为什么存在**：解决"在我机器上能跑，到你机器上跑不了"的环境不一致问题；让应用和依赖一起交付。
- **Kairos 哪里用了**：
  - 每个 demo 后端都有 Dockerfile（如 `backends/rag_app/Dockerfile`）
  - `deploy/docker-compose.yml` 把多个容器一起启动
  - 生产服务器 `/opt/kairos` 用 Docker 部署所有服务
- **和相邻概念的关系**：
  - 比虚拟机轻量，共享宿主机内核
  - Docker Compose 是管理多个 Docker 容器的工具
  - 镜像 ≈ 类，容器 ≈ 实例
- **常见面试问法**：
  - "Docker 和虚拟机有什么区别？"
  - "Docker 镜像和容器的区别是什么？"
  - "你们项目为什么用 Docker？"
- **我踩过的坑 / 注意点**：
  - 容器 IP 变化后，Nginx 反向代理需要重启
  - 中国大陆拉 Docker Hub 镜像可能超时，需要预缓存或配加速器
- **推荐学习资源**：
  - Docker 官方 Get Started
  - 项目中的 `deploy/docker-compose.yml`
```

- [ ] **Step 3: 验证格式正确**

检查该节点包含 7 个字段，且每个字段以 `- **` 开头。

- [ ] **Step 4: 提交**

```bash
git add docs/learning/kairos-concept-map.md
git commit -m "docs(learning): add Docker sample node with 7-field format"
```

---

## Task 3: 填充基础设施层节点

**Files:**
- Modify: `docs/learning/kairos-concept-map.md`

**Interfaces:**
- Consumes: Task 2 的 Docker 示例节点格式
- Produces: Git、Docker Compose、Nginx 三个完整节点

- [ ] **Step 1: 填充 Git 节点**

参考项目：`.git/`、`README.md` 中的 clone URL、最近的 commit 历史。

关键内容：
- 一句话定义：分布式版本控制系统
- 为什么存在：追踪代码变更、支持多人协作、回退历史
- Kairos 哪里用了：仓库管理、`deploy/PRODUCTION.md` 中的部署流程、分支 `feat/kairos-rebrand` 合并到 `master`
- 相关概念：GitHub、commit、branch、merge、worktree
- 常见面试问法："git merge 和 rebase 的区别"、"如何解决冲突"
- 坑点：worktree 是高级特性、本地测试环境问题

- [ ] **Step 2: 填充 Docker Compose 节点**

参考项目：`deploy/docker-compose.yml`

关键内容：
- 一句话定义：用一个 YAML 文件定义和运行多个 Docker 容器
- 为什么存在：管理多服务依赖，一键启动整个系统
- Kairos 哪里用了：本地开发、生产部署都靠 `docker compose up`
- 相关概念：Docker、service、network、volume
- 常见面试问法："docker-compose 和 Dockerfile 的区别"
- 坑点：容器 IP 变化导致 Nginx 502

- [ ] **Step 3: 填充 Nginx 节点**

参考项目：`deploy/nginx.conf`

关键内容：
- 一句话定义：高性能 Web 服务器和反向代理
- 为什么存在：统一入口、子路径路由、静态文件托管、HTTPS 终止
- Kairos 哪里用了：门户静态文件、`/rag/` `/fc/` 等后端代理
- 相关概念：reverse proxy、upstream、SSL、location
- 常见面试问法："Nginx 反向代理的作用"、"如何解决跨域"
- 坑点：后端容器 IP 变化后需重启 Nginx

- [ ] **Step 4: 验证三个节点都包含 7 字段**

- [ ] **Step 5: 提交**

```bash
git add docs/learning/kairos-concept-map.md
git commit -m "docs(learning): fill infrastructure layer nodes (Git, Docker Compose, Nginx)"
```

---

## Task 4: 填充后端服务层节点

**Files:**
- Modify: `docs/learning/kairos-concept-map.md`

**Interfaces:**
- Consumes: Task 2 的 Docker 示例节点格式
- Produces: Python、FastAPI、Uvicorn、RAG、FC 五个完整节点

- [ ] **Step 1: 填充 Python 节点**

- 一句话定义：后端主要编程语言
- 为什么存在：生态丰富，FastAPI、AI 库成熟
- Kairos 哪里用了：所有后端服务都基于 Python
- 相关概念：FastAPI、Uvicorn、pip、pytest
- 常见面试问法："Python 的 GIL 是什么"、"异步编程怎么写"

- [ ] **Step 2: 填充 FastAPI 节点**

参考项目：`backends/rag_app/main.py`、`backends/fc_app/main.py`

- 一句话定义：现代、高性能 Python Web 框架
- 为什么存在：快速构建 API，自动生成 OpenAPI 文档
- Kairos 哪里用了：所有 demo 后端的 `/chat` `/clear` 等接口
- 相关概念：ASGI、Pydantic、Uvicorn、Starlette
- 常见面试问法："FastAPI 和 Flask 的区别"、"依赖注入怎么用"
- 坑点：同步阻塞代码会卡住整个服务

- [ ] **Step 3: 填充 Uvicorn 节点**

- 一句话定义：Python 的 ASGI 服务器
- 为什么存在：运行 FastAPI 应用，支持异步
- Kairos 哪里用了：`Dockerfile` 中 `uvicorn backends.rag_app.main:app`
- 相关概念：ASGI、WSGI、Gunicorn、FastAPI
- 常见面试问法："Uvicorn 和 Gunicorn 的区别"

- [ ] **Step 4: 填充 RAG 节点**

参考项目：`core/agent.py`、`core/rag_tool.py`、`backends/rag_app/main.py`

- 一句话定义：检索增强生成，先查文档再让 LLM 回答
- 为什么存在：让 LLM 基于私有知识回答，减少幻觉
- Kairos 哪里用了：`/rag/chat` 接口，`require_first_tool="search_docs"`
- 相关概念：Embedding、向量数据库、Chroma、LLM、Jina
- 常见面试问法："RAG 和微调的区别"、"检索不到怎么办"
- 坑点：模型可能跳过检索直接自答，已用 must-retrieve 强制

- [ ] **Step 5: 填充 FC 节点**

参考项目：`backends/fc_app/main.py`、`core/tools.py`

- 一句话定义：Function Calling，让 LLM 决定调用外部工具
- 为什么存在：让 LLM 不仅能说话，还能执行动作（查天气、算式子等）
- Kairos 哪里用了：`/fc/chat` 接口，工具包括 `get_weather`、`safe_execute_python`
- 相关概念：tool call、schema、LLM、Agent
- 常见面试问法："Function Calling 和传统 API 调用的区别"、"怎么保证参数正确"
- 坑点：DeepSeek 可能把 `safe_execute_python` 当通用执行器用，已修复描述

- [ ] **Step 6: 验证五个节点都包含 7 字段**

- [ ] **Step 7: 提交**

```bash
git add docs/learning/kairos-concept-map.md
git commit -m "docs(learning): fill backend service layer nodes"
```

---

## Task 5: 填充前端门户层节点

**Files:**
- Modify: `docs/learning/kairos-concept-map.md`

**Interfaces:**
- Consumes: Task 2 的 Docker 示例节点格式
- Produces: React、Vite、TypeScript、TailwindCSS 四个完整节点

- [ ] **Step 1: 填充 React 节点**

参考项目：`frontends/portfolio/src/App.tsx`

- 一句话定义：用于构建用户界面的 JavaScript 库
- 为什么存在：组件化开发，状态驱动 UI
- Kairos 哪里用了：门户首页、Demo 页面、导航、Hero、主题切换
- 相关概念：组件、props、state、hooks、JSX
- 常见面试问法："useEffect 什么时候执行"、"React 渲染优化"

- [ ] **Step 2: 填充 Vite 节点**

参考项目：`frontends/portfolio/vite.config.ts`、`frontends/portfolio/package.json`

- 一句话定义：现代前端构建工具
- 为什么存在：启动快、热更新快、配置简单
- Kairos 哪里用了：前端开发和生产构建
- 相关概念：esbuild、HMR、rollup、bundle
- 常见面试问法："Vite 和 Webpack 的区别"

- [ ] **Step 3: 填充 TypeScript 节点**

- 一句话定义：JavaScript 的超集，增加静态类型
- 为什么存在：提前发现类型错误，提升大型项目可维护性
- Kairos 哪里用了：前端门户代码
- 相关概念：interface、type、泛型、编译
- 常见面试问法："TypeScript 和 JavaScript 的区别"、"interface 和 type 的区别"

- [ ] **Step 4: 填充 TailwindCSS 节点**

参考项目：`frontends/portfolio/src/styles/`、`tailwind.config.js`

- 一句话定义：实用类优先的 CSS 框架
- 为什么存在：不用写自定义 CSS，直接用类名组合样式
- Kairos 哪里用了：门户所有组件的样式
- 相关概念：utility-first、responsive、dark mode
- 常见面试问法："Tailwind 和传统 CSS 框架的区别"

- [ ] **Step 5: 验证四个节点都包含 7 字段**

- [ ] **Step 6: 提交**

```bash
git add docs/learning/kairos-concept-map.md
git commit -m "docs(learning): fill frontend portal layer nodes"
```

---

## Task 6: 填充 AI / Agent + 通用节点

**Files:**
- Modify: `docs/learning/kairos-concept-map.md`

**Interfaces:**
- Consumes: Task 2 的 Docker 示例节点格式
- Produces: LLM、Function Calling、HTTP/REST API 三个完整节点

- [ ] **Step 1: 填充 LLM 节点**

参考项目：`core/llm.py`、`.env`

- 一句话定义：大语言模型，能理解和生成自然语言
- 为什么存在：提供通用语言理解和生成能力
- Kairos 哪里用了：RAG、FC、Nexus 的聊天与推理都走 `LLMClient`
- 相关概念：Prompt、Token、Completion、Temperature
- 常见面试问法："你们为什么选 DeepSeek"、"怎么处理模型幻觉"
- 坑点：从 DashScope 切到 DeepSeek 时暴露的旧 bug

- [ ] **Step 2: 填充 Function Calling 节点**

（与 Task 4 的 FC 节点不同，这里更强调通用概念，Task 4 强调项目实现）

- 一句话定义：让大模型输出结构化工具调用请求
- 为什么存在：让 LLM 与外部系统交互
- Kairos 哪里用了：FC demo 的天气查询、算术计算
- 相关概念：tool schema、LLM、Agent
- 常见面试问法："Function Calling 怎么保证安全性"、"参数错了怎么办"

- [ ] **Step 3: 填充 HTTP / REST API 节点**

参考项目：所有 `backends/*/main.py` 中的 `@app.post("/chat")`

- 一句话定义：基于 HTTP 的 API 设计风格
- 为什么存在：统一前后端通信方式
- Kairos 哪里用了：前端通过 iframe/HTTP 调用后端 `/rag/chat` `/fc/chat` 等接口
- 相关概念：GET/POST、JSON、status code、endpoint
- 常见面试问法："GET 和 POST 的区别"、"RESTful API 的设计原则"

- [ ] **Step 4: 验证三个节点都包含 7 字段**

- [ ] **Step 5: 提交**

```bash
git add docs/learning/kairos-concept-map.md
git commit -m "docs(learning): fill AI/Agent and HTTP/REST API nodes"
```

---

## Task 7: 写入学习决策树与使用说明

**Files:**
- Modify: `docs/learning/kairos-concept-map.md`

**Interfaces:**
- Consumes: 前面所有 task 填充的节点
- Produces: 完整的"怎么用这张地图"指南

- [ ] **Step 1: 在文档开头补充详细使用说明**

在"## 使用决策树"后面追加：

```markdown
### 每日使用流程

1. 遇到新概念，先在地图里找它属于哪一层。
2. 如果找不到，放入"待归档区"，等项目里用到再迁移。
3. 按 7 字段模板补充该节点。
4. 判断是基础概念还是高级特性：
   - 基础概念：必须能口头讲出"是什么 + 为什么 + 哪里用"
   - 高级特性：知道定义和相关概念即可
5. 在节点标题旁标注状态：`- [ ]` 未掌握 / `- [x]` 已掌握

### 每周回顾

- 扫描所有 `- [ ]` 节点
- 选 3 个最常用或最模糊的，重新复习
- 用费曼法：不看文档，讲一遍这个概念

### 每月面试转化

- 从已掌握节点中挑选 5 个
- 把"常见面试问法"扩展成完整回答
- 写入 `docs/learning/kairos-interview-qa.md`
```

- [ ] **Step 2: 为每个核心节点标题添加掌握状态复选框**

例如：

```markdown
#### Docker

- [x] 已掌握
```

- [ ] **Step 3: 验证文档结构清晰**

```bash
# 检查是否有 15 个核心节点
grep -c "^#### " docs/learning/kairos-concept-map.md
```

Expected: 至少 15 个四级标题（核心概念节点）。

- [ ] **Step 4: 提交**

```bash
git add docs/learning/kairos-concept-map.md
git commit -m "docs(learning): add usage guide and mastery checkboxes"
```

---

## Task 8: 填充面试问法汇总

**Files:**
- Modify: `docs/learning/kairos-concept-map.md`

**Interfaces:**
- Consumes: 前面所有节点中的"常见面试问法"字段
- Produces: 一个按层级分组的面试问题清单

- [ ] **Step 1: 在"## 面试问法汇总"章节汇总所有问题**

按以下结构整理：

```markdown
## 面试问法汇总

### 基础设施层

- Git：git merge 和 rebase 的区别？
- Docker：Docker 和虚拟机的区别？
- Docker Compose：为什么用 docker-compose 而不是手动 docker run？
- Nginx：反向代理和正向代理的区别？

### 后端服务层

- Python：GIL 是什么？
- FastAPI：FastAPI 和 Flask 的区别？
- Uvicorn：Uvicorn 和 Gunicorn 的区别？
- RAG：RAG 和微调的区别？
- FC：Function Calling 如何保证安全性？

### 前端门户层

- React：useEffect 什么时候执行？
- Vite：Vite 和 Webpack 的区别？
- TypeScript：interface 和 type 的区别？
- TailwindCSS：Tailwind 和传统 CSS 框架的区别？

### AI / Agent 能力层

- LLM：怎么处理模型幻觉？
- Function Calling：参数错了怎么办？

### 通用

- HTTP/REST：GET 和 POST 的区别？
```

- [ ] **Step 2: 验证每个核心节点至少贡献了一个面试问题**

- [ ] **Step 3: 提交**

```bash
git add docs/learning/kairos-concept-map.md
git commit -m "docs(learning): add interview question summary"
```

---

## Task 9: 最终验收与提交

**Files:**
- Modify: `docs/learning/kairos-concept-map.md`
- Modify: `docs/PROJECT-STATE.md`（可选，记录学习资产更新）

**Interfaces:**
- Consumes: 前面所有 task 的输出
- Produces: 可交付的完整概念地图

- [ ] **Step 1: 运行完整性检查**

```bash
# 检查 15 个核心节点是否都存在
for node in Git Docker "Docker Compose" Nginx Python FastAPI Uvicorn RAG FC React Vite TypeScript TailwindCSS LLM "Function Calling" "HTTP / REST API"; do
  grep -q "^#### $node" docs/learning/kairos-concept-map.md && echo "✅ $node" || echo "❌ $node missing"
done
```

Expected: 全部 15 个节点显示 ✅。

- [ ] **Step 2: 验证每个核心节点都有 7 字段**

抽查 3 个节点，确认包含：
- 一句话定义
- 为什么存在
- Kairos 哪里用了
- 和相邻概念的关系
- 常见面试问法
- 我踩过的坑 / 注意点
- 推荐学习资源

- [ ] **Step 3: 用户口头验收**

用户随机挑选 3 个节点，不看文档，口头解释：
- 是什么
- 为什么存在
- 项目里哪里用了

- [ ] **Step 4: 更新 PROJECT-STATE.md（可选）**

在"2026-07-06 品牌重命名"章节附近追加：

```markdown
## 2026-07-07 学习资产

新增 `docs/learning/kairos-concept-map.md`：以 Kairos 项目为中心的技术概念地图，覆盖 15 个核心节点，用于系统补齐技术基础。
```

- [ ] **Step 5: 最终提交并推送**

```bash
git add docs/learning/kairos-concept-map.md docs/PROJECT-STATE.md
git commit -m "docs(learning): complete Kairos concept map with 15 core nodes"
git push origin master
```

---

## Self-Review

### Spec Coverage

| Spec 要求 | 对应 Task |
|---|---|
| 创建 `docs/learning/kairos-concept-map.md` | Task 1 |
| 6 大层 + 子分类骨架 | Task 1 |
| Docker 7 字段示例节点 | Task 2 |
| 15 个核心节点填充 | Task 3-6 |
| 学习决策树与使用说明 | Task 7 |
| 面试问法汇总 | Task 8 |
| 最终验收 | Task 9 |

无遗漏。

### Placeholder Scan

- 无 "TBD" / "TODO" / "implement later"
- 所有节点内容均给出具体字段和参考项目位置
- 所有命令均给出预期输出

### Type Consistency

- 所有节点统一使用 7 字段格式
- 所有核心节点名称与 design doc 一致
- 文件路径统一使用 `docs/learning/kairos-concept-map.md`

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-07-07-kairos-concept-map-learning.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
