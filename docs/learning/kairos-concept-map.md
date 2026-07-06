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

- **一句话定义**：分布式版本控制系统，在本地保存完整仓库历史，支持离线提交与多人协作。
- **为什么存在**：追踪代码每一次变更，便于回滚、审计和团队协作；避免“谁改了什么、为什么改”无从查起。
- **Kairos 哪里用了**：
  - 整个项目用 Git 管理，远程仓库为 `https://github.com/shiyuan-wreg/rag-qa-system.git`
  - `deploy/PRODUCTION.md` 中的增量部署流程依赖服务器执行 `git pull origin master`
  - 品牌重塑分支 `feat/kairos-rebrand` 已合并到 `master`，并通过 Git 历史保留演进过程
- **和相邻概念的关系**：
  - GitHub 是远程仓库托管平台，Git 是本地版本控制工具
  - commit 是一次快照，branch 是并行开发线，merge 把分支合并回主线
  - worktree 是 Git 的高级特性，可在同一仓库多个工作目录同时开发
- **常见面试问法**：
  - "git merge 和 rebase 的区别是什么？"
  - "如何解决代码冲突？"
  - "Git 工作流中 feature branch 怎么管理？"
- **我踩过的坑 / 注意点**：
  - worktree 是高级特性，新手容易和独立仓库混淆，建议先掌握 branch/merge 再用
  - 本地测试环境（Windows + Git Bash）与生产服务器（Ubuntu）的换行符、路径写法可能不一致，提交前确认 `.gitattributes`
- **推荐学习资源**：
  - Pro Git（官方中文版）
  - 项目 `.git/` 历史与 `deploy/PRODUCTION.md`

#### GitHub

### 1.2 容器化

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

#### Docker Compose

- **一句话定义**：用一个 YAML 文件定义和运行多个 Docker 容器，描述服务、网络、卷和依赖关系。
- **为什么存在**：单体应用拆成多个服务后，需要统一编排多容器启动顺序、共享网络和持久化存储，实现“一键启动整个系统”。
- **Kairos 哪里用了**：
  - 本地开发和生产部署都使用 `deploy/docker-compose.yml`
  - 定义了 rag、fc、nexus、md_converter、iconforge 五个后端服务，以及 nginx、certbot
  - 生产部署命令：`docker compose -f deploy/docker-compose.yml up -d --build`
- **和相邻概念的关系**：
  - Docker Compose 是 Docker 的上层编排工具，Docker 负责单个容器，Compose 负责多容器协作
  - service 对应一个容器/应用，network 让容器互相通信，volume 持久化数据
  - nginx 依赖所有后端服务（`depends_on`），通过 Compose 网络按服务名 DNS 解析
- **常见面试问法**：
  - "docker-compose 和 Dockerfile 的区别是什么？"
  - "docker compose up 和 docker compose up -d 有什么区别？"
  - "如何管理服务启动顺序？"
- **我踩过的坑 / 注意点**：
  - 容器 IP 变化可能导致 Nginx 反向代理出现 502；生产上通过 `resolver` + 变量上游缓解，但偶尔仍需 `docker compose restart nginx`
  - 修改 `docker-compose.yml` 后要注意端口冲突和 `.env` 文件路径，本地与生产挂载路径不同
- **推荐学习资源**：
  - Docker Compose 官方文档
  - 项目中的 `deploy/docker-compose.yml` 和 `deploy/PRODUCTION.md`

### 1.3 Web 服务器与代理

#### Nginx

- **一句话定义**：高性能 Web 服务器和反向代理，常用于统一入口、子路径路由、静态文件托管和 HTTPS 终止。
- **为什么存在**：把多个后端服务收敛到一个域名+端口下；对外提供静态页面，对内按路径转发到不同服务；同时承担 SSL/TLS 加解密，减轻后端压力。
- **Kairos 哪里用了**：
  - 门户静态文件由 `root /usr/share/nginx/html` 托管，并配置 SPA history 路由回退到 `index.html`
  - `/rag/`、`/fc/`、`/nexus/` 分别代理到后端同名服务
  - `/doctomd/`、`/iconforge/` 代理到 md_converter、iconforge 服务，并禁用缓存以避免 iframe 主题不同步
  - `/learn/` 挂载 Nexus 学习站点静态资源
  - 监听 80 并 301 跳转到 443 HTTPS，SSL 证书由 Let's Encrypt 提供
- **和相邻概念的关系**：
  - reverse proxy 是 Nginx 的核心能力，把外部请求转发给内部服务
  - upstream 指后端服务集群，本项目里通过服务名（如 `rag:8001`）动态解析
  - SSL/TLS 在 Nginx 层终止，后端容器只需处理 HTTP
  - location 块匹配 URI 路径，决定请求走静态文件还是反向代理
- **常见面试问法**：
  - "Nginx 反向代理的作用是什么？"
  - "如何解决跨域问题？"
  - "location 匹配优先级是怎样的？"
- **我踩过的坑 / 注意点**：
  - 后端容器重建后 IP 可能变化，需配置 `resolver 127.0.0.11 valid=30s` 并把 upstream 放在变量里，让 Nginx 运行时动态解析
  - iframe 嵌入的 demo 页面若被浏览器缓存，会导致主题不同步，需要在对应 location 加 `Cache-Control: no-cache`
- **推荐学习资源**：
  - Nginx 官方文档（Beginner’s Guide、Server names、Location matching）
  - 项目中的 `deploy/nginx/nginx.conf` 和 `deploy/docker-compose.yml`

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
