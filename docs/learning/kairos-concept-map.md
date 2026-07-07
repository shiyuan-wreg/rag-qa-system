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

## 1. 基础设施层

### 1.1 版本控制

#### Git

- [ ] 未掌握

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
  - 零基础入门：[docs/learning/git-basics.md](git-basics.md)

#### GitHub

### 1.2 容器化

#### Docker

- [ ] 未掌握

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
  - 零基础入门：[docs/learning/docker-basics.md](docker-basics.md)

#### Docker Compose

- [ ] 未掌握

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
  - 零基础入门：[docs/learning/docker-compose-basics.md](docker-compose-basics.md)

### 1.3 Web 服务器与代理

#### Nginx

- [ ] 未掌握

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
  - 零基础入门：[docs/learning/nginx-basics.md](nginx-basics.md)

### 1.4 服务器与运维

#### Linux / SSH / 域名与 SSL

## 2. 后端服务层

### 2.1 语言与运行时

#### Python

- [ ] 未掌握

- **一句话定义**：后端主要编程语言，解释型、动态类型，拥有丰富的 AI 与 Web 开发生态。
- **为什么存在**：语法简洁、库生态成熟，FastAPI、LangChain、Chroma 等 AI 工程组件都优先支持 Python，适合快速搭建 LLM 应用原型和生产服务。
- **Kairos 哪里用了**：
  - 所有 demo 后端（rag_app、fc_app、nexus_app、md_converter_app、iconforge_app）都基于 Python 实现
  - `backends/rag_app/main.py`、`backends/fc_app/main.py` 等业务入口均为 Python 文件
  - `core/agent.py`、`core/rag_tool.py`、`core/tools.py` 等共享核心模块也使用 Python
- **和相邻概念的关系**：
  - FastAPI 是 Python Web 框架，Uvicorn 是运行 FastAPI 的 ASGI 服务器
  - pip 是 Python 包管理器，`requirements.txt` 描述项目依赖
  - pytest 是 Python 测试框架，Kairos 中用于后端单元测试与评估
- **常见面试问法**：
  - "Python 的 GIL 是什么？它带来了什么限制？"
  - "Python 中异步编程怎么写？async/await 和线程有什么区别？"
  - "列表和元组的区别是什么？字典的底层实现是什么？"
- **我踩过的坑 / 注意点**：
  - Windows 本地开发与 Linux 生产环境的路径分隔、换行符、文件编码可能不一致，提交前注意 `.gitattributes`
  - 同步阻塞代码（如长时间计算、同步 HTTP 请求）会卡住整个服务，后端应尽量使用异步或放到线程池
  - 虚拟环境要隔离，不要把系统 Python 和项目依赖混用
- **推荐学习资源**：
  - Python 官方教程与标准库文档
  - 项目中的 `backends/rag_app/main.py`、`requirements.txt`
  - 零基础入门：[docs/learning/python-basics.md](python-basics.md)

#### Uvicorn

- [ ] 未掌握

- **一句话定义**：Python 的 ASGI 服务器，用于运行异步 Web 应用（如 FastAPI）。
- **为什么存在**：WSGI（如 Gunicorn 默认模式）不支持异步，而现代 Python Web 框架大量使用 async/await；Uvicorn 基于 uvloop 和 httptools，能高效处理并发连接。
- **Kairos 哪里用了**：
  - `backends/rag_app/Dockerfile` 中以 `uvicorn backends.rag_app.main:app --host 0.0.0.0 --port 8001 --workers 1` 启动服务
  - 本地开发命令：`venv/Scripts/python.exe -m uvicorn backends.rag_app.main:app --reload --port 8001`
  - 所有 FastAPI 后端的容器入口都使用 Uvicorn
- **和相邻概念的关系**：
  - ASGI 是 Uvicorn 实现的协议，FastAPI 是构建在 Starlette（ASGI 框架）之上的 Web 框架
  - WSGI 是上一代同步接口，Gunicorn 可通过 worker class 搭配 Uvicorn 运行 ASGI 应用
  - Uvicorn 负责监听端口、管理连接、把请求交给 FastAPI 应用处理
- **常见面试问法**：
  - "Uvicorn 和 Gunicorn 的区别是什么？"
  - "ASGI 和 WSGI 有什么区别？"
  - "生产环境如何部署 Uvicorn？"
- **我踩过的坑 / 注意点**：
  - 开发时建议加 `--reload` 实现热重载，但生产环境要关闭 reload，并通过 `--workers` 或 Gunicorn+Uvicorn worker 提高并发
  - 容器内监听 `0.0.0.0`，本地开发常监听 `127.0.0.1`，直接复制命令可能访问不到
  - 异步函数里调用同步阻塞库（如某些数据库驱动）会拖垮整个事件循环
- **推荐学习资源**：
  - Uvicorn 官方文档
  - 项目中的 `backends/rag_app/Dockerfile`、`backends/fc_app/main.py` 底部 `uvicorn.run(...)`
  - 零基础入门：[docs/learning/uvicorn-basics.md](uvicorn-basics.md)

### 2.2 Web 框架

#### FastAPI

- [ ] 未掌握

- **一句话定义**：现代、高性能的 Python Web 框架，基于 Starlette 和 Pydantic，原生支持异步和自动生成 OpenAPI 文档。
- **为什么存在**：让开发者用少量代码快速构建类型安全的 REST API；自动校验请求参数、生成 Swagger UI，并把同步/异步路由性能做到极致。
- **Kairos 哪里用了**：
  - 所有 demo 后端的 `/chat`、`/clear` 等接口都用 FastAPI 定义，例如 `backends/rag_app/main.py` 中的 `@app.post("/chat")`
  - `backends/fc_app/main.py` 同样使用 FastAPI 提供 `/chat`、`/clear`、`/execute` 接口
  - 前端通过 `fetch('chat', { method: 'POST', body: form })` 调用 FastAPI 后端
- **和相邻概念的关系**：
  - ASGI 是 FastAPI 运行的协议基础，Uvicorn 是生产常用的 ASGI 服务器
  - Pydantic 负责请求/响应模型校验，`query: str = Form(...)` 是 Pydantic 风格的使用方式
  - Starlette 是 FastAPI 的底层 ASGI 工具包，提供路由、中间件、请求响应对象
- **常见面试问法**：
  - "FastAPI 和 Flask 的区别是什么？"
  - "FastAPI 的依赖注入怎么用？"
  - "路径参数、查询参数、请求体有什么区别？"
- **我踩过的坑 / 注意点**：
  - 同步阻塞代码会卡住整个服务：如果路由函数里执行长时间同步任务，所有并发请求都会被阻塞，应使用 `async def` 或 `run_in_threadpool`
  - 自动生成的 Swagger 文档很方便，但不要为了文档而暴露内部接口或敏感参数
  - `Form`、`Body`、`Query` 等参数类型用错会导致前端 422 错误
- **推荐学习资源**：
  - FastAPI 官方文档
  - 项目中的 `backends/rag_app/main.py`、`backends/fc_app/main.py`
  - 零基础入门：[docs/learning/fastapi-basics.md](fastapi-basics.md)

### 2.3 各 demo 后端

#### RAG

- [ ] 未掌握

- **一句话定义**：检索增强生成（Retrieval-Augmented Generation），先在外部知识库中检索相关文档片段，再把检索结果交给 LLM 生成回答。
- **为什么存在**：大模型训练数据有截止日期，对私有文档或最新信息容易幻觉；RAG 让 LLM 基于检索到的真实资料回答，提高准确性和可溯源性。
- **Kairos 哪里用了**：
  - `/rag/chat` 接口在 `backends/rag_app/main.py` 中实现，调用 `Agent(require_first_tool="search_docs")`
  - `core/rag_tool.py` 封装了 RAG 检索流程：`load_documents` → `split_documents` → `get_or_create_vectorstore` → `retrieve`
  - `core/agent.py` 通过 `require_first_tool="search_docs"` 强制第一轮必须调用检索工具，避免模型跳过检索直接自答
- **和相邻概念的关系**：
  - Embedding（Jina）把文本变成向量，向量数据库（Chroma）存储并相似度检索这些向量
  - LLM 负责根据检索结果生成最终回答
  - Function Calling 是触发 `search_docs` 工具的机制，RAG 是「检索+生成」的整体流程
- **常见面试问法**：
  - "RAG 和微调（Fine-tuning）的区别是什么？"
  - "检索不到相关内容时怎么办？"
  - "如何评估 RAG 的效果？"
- **我踩过的坑 / 注意点**：
  - 模型可能跳过检索直接自答，已用 `require_first_tool="search_docs"` 强制首轮检索；若模型仍未调用，Agent 会自动替它调用一次
  - 检索片段过长会超出上下文窗口，需在 `format_retrieved` 中限制 `max_chars`
  - Jina API Key 未配置时 RAG 工具无法初始化，要给出明确错误提示而不是静默失败
- **推荐学习资源**：
  - 项目中的 `core/agent.py`、`core/rag_tool.py`、`backends/rag_app/main.py`
  - LangChain RAG 教程

#### FC

- [ ] 未掌握

- **一句话定义**：Function Calling（函数调用），让 LLM 根据用户意图决定调用哪个外部工具、传入什么参数。
- **为什么存在**：LLM 只能生成文本，无法获取实时信息或执行动作；FC 让模型不仅能"说话"，还能查天气、做计算、读文件、调用 API 等。
- **Kairos 哪里用了**：
  - `/fc/chat` 接口在 `backends/fc_app/main.py` 中实现，工具包括 `get_weather`、`calculate`、`set_reminder`
  - `core/tools.py` 定义了共享工具 `search_docs`、`safe_execute_python`、`read_file`、`list_files`，供 RAG 等后端使用
  - `core/agent.py` 中的 Agent 把 `TOOLS` schema 传给 LLM，并处理模型返回的 `tool_calls`
- **和相邻概念的关系**：
  - tool call 是 LLM 输出的一种结构化形式，schema（名称、描述、参数）定义了工具长什么样
  - Agent 是多轮对话 + 工具调用的整体系统，FC 是 Agent 做决策的关键能力
  - LLM 根据工具描述和对话上下文选择工具，与传统 API 调用由程序员硬编码不同
- **常见面试问法**：
  - "Function Calling 和传统 API 调用的区别是什么？"
  - "怎么保证模型生成的参数是正确的？"
  - "如果模型调用了不存在的工具怎么办？"
- **我踩过的坑 / 注意点**：
  - DeepSeek 等模型可能把 `calculate`/`safe_execute_python` 当成通用代码执行器使用（例如让它写示例代码、定义函数），已通过收紧工具描述和限制 AST 节点修复，只允许纯算术表达式
  - 缺少必填参数时不要猜测，应主动向用户反问；`backends/fc_app/main.py` 中用 `missing_required_args` 检查并提示
  - 工具执行失败要如实返回，不要让模型编造结果
- **推荐学习资源**：
  - 项目中的 `backends/fc_app/main.py`、`core/tools.py`
  - DeepSeek / OpenAI Function Calling 官方文档
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

- [ ] 未掌握

- **一句话定义**：JavaScript 的超集，增加静态类型，让变量、函数、组件在运行前就能被类型系统检查。
- **为什么存在**：大型前端项目里动态类型容易隐藏错误；TypeScript 把很多运行时 bug 提前到编译期发现，同时提升 IDE 补全、重构和可维护性。
- **Kairos 哪里用了**：
  - 门户所有前端代码使用 TypeScript，如 `frontends/portfolio/src/App.tsx`、`frontends/portfolio/src/components/NavBar.tsx`
  - `frontends/portfolio/tsconfig.json` 配置 `strict: true`、`moduleResolution: bundler`、`noEmit: true`
  - `frontends/portfolio/package.json` 中 `build` 脚本先执行 `tsc` 类型检查，再执行 `vite build`
  - 自定义 hook `useTheme` 用联合类型 `Theme` 约束可选主题，避免非法主题值被写入 localStorage
- **和相邻概念的关系**：
  - JavaScript 是 TypeScript 的运行时基础，TypeScript 编译后生成 JavaScript
  - `interface` 和 `type` 都用于定义类型，interface 更适合对象形状和继承，type 更适合联合类型、元组等
  - 泛型让组件和函数在保持类型安全的同时复用逻辑，如 `useState<Theme>(...)`
  - Vite 负责构建，TypeScript 负责类型检查，二者通过 `tsc && vite build` 串联
- **常见面试问法**：
  - "TypeScript 和 JavaScript 的区别是什么？"
  - "interface 和 type 的区别是什么？"
  - "泛型在什么时候使用？"
  - "`any` 和 `unknown` 有什么区别？"
- **我踩过的坑 / 注意点**：
  - `tsconfig.json` 开启 `strict: true` 后，隐式 any、空值、未使用变量都会报错，初期需要逐步修复
  - `allowImportingTsExtensions: true` 必须配合 `noEmit: true` 使用，否则编译器会拒绝输出 `.ts` 扩展名的导入
  - 自定义 hook 的返回类型和参数类型要显式声明，否则调用方失去类型保护
  - 不要滥用 `as` 类型断言，它会让 TypeScript 的静态检查失效
- **推荐学习资源**：
  - TypeScript 官方文档（TypeScript Handbook）
  - 项目中的 `frontends/portfolio/tsconfig.json`、`frontends/portfolio/src/hooks/useTheme.ts`

#### JavaScript（ES6+）

### 3.2 UI 框架

#### React

- [ ] 未掌握

- **一句话定义**：用于构建用户界面的 JavaScript 库，通过组件和声明式渲染把 UI 拆成可复用的模块。
- **为什么存在**：传统命令式 DOM 操作难以维护复杂页面；React 用组件化、状态驱动 UI 和虚拟 DOM，让界面开发更可预测、可复用。
- **Kairos 哪里用了**：
  - 门户入口 `frontends/portfolio/src/main.tsx` 用 `ReactDOM.createRoot` 挂载应用
  - `frontends/portfolio/src/App.tsx` 用 `react-router-dom` 定义首页、RAG、FC、Nexus、Learn、Me、Changelog 等路由
  - `frontends/portfolio/src/components/NavBar.tsx`、`Hero.tsx`、`ThemeToggle.tsx` 等均为 React 组件
  - 主题切换、视差滚动、页面过渡动画都通过 React state 和 hook 实现
- **和相邻概念的关系**：
  - JSX 是 React 的语法扩展，让 JS 中写 HTML 结构
  - props 是父组件传给子组件的数据，state 是组件内部可变的状态
  - hooks（如 `useState`、`useEffect`、`useLocation`）让函数组件拥有状态和副作用能力
  - React Router 是 React 生态的路由库，Vite 是构建工具，TypeScript 提供类型支持
- **常见面试问法**：
  - "useEffect 什么时候执行？依赖数组的作用是什么？"
  - "React 渲染优化有哪些手段？"
  - "props 和 state 的区别是什么？"
  - "React 18 的并发特性你了解吗？"
- **我踩过的坑 / 注意点**：
  - 列表渲染必须提供稳定且唯一的 `key`，例如 NavBar 中用 `key={it.to}`，不要用数组索引
  - `useEffect` 依赖数组要完整，遗漏依赖会导致闭包陷阱或状态不同步
  - 路由切换动画依赖 `key={pathname}` 触发 `PageTransition` 重新挂载，否则动画不会播放
  - `React.StrictMode` 会故意双重调用某些函数，开发时要注意副作用是否可重复执行
- **推荐学习资源**：
  - React 官方文档（React.dev）
  - 项目中的 `frontends/portfolio/src/App.tsx`、`frontends/portfolio/src/components/NavBar.tsx`

### 3.3 样式

#### TailwindCSS

- [ ] 未掌握

- **一句话定义**：实用类优先（utility-first）的 CSS 框架，通过组合大量细粒度类名来构建界面样式。
- **为什么存在**：传统手写 CSS 容易出现命名冲突、样式冗余和文件分散；Tailwind 把常见样式封装成类名，让开发者直接在 HTML/JSX 中组合，提高开发效率和一致性。
- **Kairos 哪里用了**：
  - 门户几乎所有组件都使用 Tailwind 类名，如 `frontends/portfolio/src/components/NavBar.tsx` 中的 `sticky top-0 z-50 bg-surface/90 backdrop-blur`
  - `frontends/portfolio/tailwind.config.js` 把设计系统变量（颜色、阴影、圆角、字体等）映射为 Tailwind 主题扩展
  - `frontends/portfolio/src/styles/theme.css` 定义 CSS 变量，Tailwind 配置中通过 `var(--bg-base)` 等方式引用
  - 响应式布局通过 `sm:`、`md:`、`lg:` 前缀实现，移动端优先
- **和相邻概念的关系**：
  - utility-first 是 Tailwind 的核心思想，用 `flex`、`p-4`、`text-primary` 等类直接描述样式
  - responsive 通过前缀控制不同断点，dark mode 可通过 `dark:` 变体或自定义主题变量实现
  - PostCSS 和 autoprefixer 是 Tailwind 构建链路的依赖，Vite 负责整体构建
  - 自定义 CSS（如 `machine-skin.css`、`texture.css`）与 Tailwind 互补，处理复杂背景和动画
- **常见面试问法**：
  - "Tailwind 和传统 CSS 框架（如 Bootstrap）的区别是什么？"
  - "Tailwind 如何实现主题切换？"
  - "如何避免 Tailwind 类名过长导致 JSX 可读性下降？"
  - "Tailwind 的 JIT 模式是什么？"
- **我踩过的坑 / 注意点**：
  - 主题通过 CSS 变量实现时，Tailwind 配置中的 colors 必须和 `theme.css` 中的变量名保持一致，否则颜色会失效
  - 自定义类名（如 `hero-ambient`、`hero-grid`）与 Tailwind 类混用时要职责分离，避免样式覆盖混乱
  - 响应式前缀是移动端优先，即不写前缀的样式默认作用于最小屏幕
  - 类名顺序不影响优先级，但 `!important` 变体和自定义 CSS 的加载顺序会影响最终渲染
- **推荐学习资源**：
  - TailwindCSS 官方文档
  - 项目中的 `frontends/portfolio/tailwind.config.js`、`frontends/portfolio/src/components/NavBar.tsx`

### 3.4 构建与路由

#### Vite

- [ ] 未掌握

- **一句话定义**：现代前端构建工具，基于原生 ES 模块和 esbuild/Rollup，提供极快的开发服务器和生产打包能力。
- **为什么存在**：传统 Webpack 项目配置复杂、冷启动慢、热更新慢；Vite 利用浏览器原生 ESM 实现秒级启动，并借助 esbuild 和 Rollup 兼顾开发与生产构建性能。
- **Kairos 哪里用了**：
  - `frontends/portfolio/vite.config.ts` 配置 React 插件、开发端口 5180、以及 demo iframe 的反向代理
  - `frontends/portfolio/package.json` 中 `dev`、`build`、`preview` 脚本都基于 Vite
  - 生产构建命令为 `tsc && vite build`，输出到 `dist/` 目录，再由 Nginx 托管
  - 本地开发时把 `/rag/`、`/fc/`、`/nexus/`、`/doctomd/`、`/iconforge/`、`/learn/` 代理到本地 Docker Nginx（:8080）
- **和相邻概念的关系**：
  - esbuild 负责 Vite 开发阶段的依赖预构建和转译，速度快
  - Rollup 负责 Vite 生产阶段的代码打包和 tree-shaking
  - HMR（热模块替换）让开发时修改代码后页面无刷新更新
  - bundle 是打包后的产物，Vite 生产构建会生成优化后的静态资源
  - React 是 Vite 服务的框架，TypeScript 类型检查在 Vite 构建前由 `tsc` 完成
- **常见面试问法**：
  - "Vite 和 Webpack 的区别是什么？"
  - "Vite 为什么启动快？"
  - "esbuild 和 Rollup 在 Vite 中分别负责什么？"
  - "Vite 如何处理环境变量？"
- **我踩过的坑 / 注意点**：
  - 开发代理配置要用尾斜杠键（如 `/rag/`），避免命中门户 SPA 路由（`/nexus` 无斜杠），配置已注释在 `vite.config.ts` 中
  - 生产构建由 `tsc && vite build` 完成，类型错误会阻止构建，CI 中要先跑类型检查
  - `base: '/'` 表示部署到域名根路径，若未来改到子路径需要同步调整 Nginx 配置
  - 静态资源引用建议使用相对路径或配置 alias，避免开发和生产路径不一致
- **推荐学习资源**：
  - Vite 官方文档
  - 项目中的 `frontends/portfolio/vite.config.ts`、`frontends/portfolio/package.json`

#### React Router

### 3.5 门户与 demo 集成

#### iframe 嵌入机制

## 4. AI / Agent 能力层

### 4.1 大模型基础

#### LLM（DeepSeek）

- [ ] 未掌握

- **一句话定义**：大语言模型（Large Language Model），通过学习海量文本获得的概率模型，能够理解和生成自然语言文本。
- **为什么存在**：提供通用的语言理解、推理和生成能力，让应用无需自己训练模型就能处理开放域的问答、翻译、摘要、代码生成等任务。
- **Kairos 哪里用了**：
  - `core/llm.py` 封装了统一的 `LLMClient`，支持 Qwen 和 OpenAI 兼容接口（DeepSeek 使用 openai 客户端）
  - `.env` 中配置 `LLM_PROVIDER=openai`、`LLM_MODEL=deepseek-chat`、`LLM_BASE_URL=https://api.deepseek.com`
  - `core/config.py` 的 `Config` 类从环境变量读取 LLM 配置，向后兼容旧的 `DASHSCOPE_API_KEY`
  - RAG、FC、Nexus 等 demo 的聊天与推理都通过 `LLMClient.from_config()` 统一调用 DeepSeek
- **和相邻概念的关系**：
  - Prompt 是输入给模型的指令和上下文，Completion 是模型生成的输出
  - Token 是模型处理文本的最小单位，影响计费、上下文长度和生成速度
  - Temperature 控制生成结果的随机性，值越低越确定，值越高越创意
  - Function Calling 依赖 LLM 理解工具描述并输出结构化调用请求
- **常见面试问法**：
  - "你们为什么选 DeepSeek？"
  - "怎么处理模型幻觉？"
  - "LLM 的上下文窗口满了怎么办？"
  - "Temperature 和 Top-p 有什么区别？"
- **我踩过的坑 / 注意点**：
  - 从 DashScope 切换到 DeepSeek 时，由于 `LLMClient` 同时支持两种 provider，配置项命名和 base_url 容易写错，导致请求走到错误端点
  - DeepSeek 对工具描述非常敏感，描述过宽会让模型把 `calculate`/`safe_execute_python` 当成通用代码执行器使用，需要收紧描述和限制 AST 节点
  - 生产环境不要把 API Key 写死在代码里，统一通过 `.env` 注入，并避免把 `.env` 提交到仓库
- **推荐学习资源**：
  - DeepSeek 官方 API 文档
  - 项目中的 `core/llm.py`、`.env`、`core/config.py`

#### Token / Prompt / Completion
#### 温度 / 上下文窗口

### 4.2 嵌入与检索

#### Embedding（Jina）
#### 向量数据库（Chroma）

### 4.3 Agent 模式

#### RAG 流程
#### Function Calling

- [ ] 未掌握

- **一句话定义**：Function Calling（函数调用）是一种让大语言模型根据用户意图，输出结构化工具调用请求（工具名 + 参数）的能力。
- **为什么存在**：纯文本 LLM 无法获取实时信息、执行计算或操作外部系统；Function Calling 让模型能够"使用工具"，从而查天气、做计算、读文件、调用 API 等。
- **Kairos 哪里用了**：
  - FC demo 在 `backends/fc_app/main.py` 中定义了 `get_weather`、`calculate`、`set_reminder` 三个工具，模型根据对话选择调用
  - `core/tools.py` 定义了共享工具 `search_docs`、`safe_execute_python`、`read_file`、`list_files`，供 RAG 等后端复用
  - `core/agent.py` 将 `TOOLS` schema 传给 `LLMClient`，并解析模型返回的 `tool_calls`，形成"请求模型 -> 执行工具 -> 把结果返回给模型"的多轮循环
- **和相邻概念的关系**：
  - tool schema（名称、描述、参数 JSON Schema）定义了工具的输入格式和约束
  - LLM 负责阅读 schema 并决定是否调用、调用哪个、传入什么参数
  - Agent 是多轮对话 + 工具调用的整体系统，Function Calling 是 Agent 做决策的关键机制
  - 与传统 API 调用由程序员硬编码不同，Function Calling 由模型动态决定调用路径
- **常见面试问法**：
  - "Function Calling 和传统 API 调用的区别是什么？"
  - "Function Calling 怎么保证安全性？"
  - "参数错了或缺失必填参数怎么办？"
  - "如果模型调用了不存在的工具怎么办？"
- **我踩过的坑 / 注意点**：
  - 工具描述必须精确：`safe_execute_python` 曾因描述过宽被模型用来写示例代码、定义函数，已通过收紧描述和限制 AST 节点修复为仅允许纯算术表达式
  - 缺少必填参数时不要猜测，应主动向用户反问；`backends/fc_app/main.py` 用 `missing_required_args` 检查并提示
  - 工具执行失败要如实返回给模型，不要让模型编造结果
  - 工具权限要最小化，避免把文件系统、网络、代码执行等敏感能力无限制地暴露给模型
- **推荐学习资源**：
  - DeepSeek / OpenAI Function Calling 官方文档
  - 项目中的 `backends/fc_app/main.py`、`core/tools.py`、`core/agent.py`

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

## 7. 通用协议层

### 7.1 通信协议

#### HTTP / REST API

- [ ] 未掌握

- **一句话定义**：HTTP 是互联网上应用最广泛的通信协议，REST API 是基于 HTTP 设计的一种资源导向、无状态的接口风格。
- **为什么存在**：统一前后端、服务与服务之间的通信方式；让不同语言、不同平台能够使用标准方法（GET/POST/PUT/DELETE）和统一资源标识符（URL）进行交互。
- **Kairos 哪里用了**：
  - 所有 demo 后端的入口都是 RESTful 风格的 HTTP 接口，例如 `backends/rag_app/main.py` 中的 `@app.post("/chat")`、`@app.post("/clear")`、`@app.post("/eval")`
  - `backends/fc_app/main.py` 同样提供 `@app.post("/chat")`、`@app.post("/clear")`、`@app.post("/execute")`
  - 前端门户通过 iframe 加载 demo 页面，页面内再用 `fetch('chat', { method: 'POST', body: form })` 调用后端 HTTP 接口
  - Nginx 在 `/rag/`、`/fc/` 等路径做反向代理，把外部 HTTPS 请求转发到对应后端容器
- **和相邻概念的关系**：
  - GET 用于获取资源，POST 用于提交数据或执行操作，PUT/PATCH 用于更新，DELETE 用于删除
  - JSON 是目前最常用的请求/响应数据格式，与 HTTP 的 `Content-Type: application/json` 配合使用
  - Status Code（如 200、400、401、500）表示请求处理结果，前端据此决定成功/失败/重试逻辑
  - Endpoint 是一个具体的 URL 路径，对应一个后端处理函数；FastAPI 通过装饰器把 endpoint 映射到 Python 函数
- **常见面试问法**：
  - "GET 和 POST 的区别是什么？"
  - "RESTful API 的设计原则是什么？"
  - "HTTP 状态码 401 和 403 有什么区别？"
  - "幂等性和安全性是什么意思？"
- **我踩过的坑 / 注意点**：
  - iframe 嵌入的 demo 页面要与父站点同源，否则 localStorage 主题同步和 fetch 请求会受跨域限制
  - 路径拼写和代理规则要一致：开发环境用 `/rag/`、`/fc/` 尾斜杠代理，无斜杠路径可能命中 SPA 路由而不是后端接口
  - FastAPI 中 `Form(...)` 和 `Body(...)` 用错会导致前端收到 422 错误，要前后端协商好 Content-Type
  - 后端返回错误时建议携带明确的 status code 和错误信息，不要统一返回 200 再在里面藏错误字段
- **推荐学习资源**：
  - MDN HTTP 文档
  - RESTful API 设计指南
  - 项目中的 `backends/rag_app/main.py`、`backends/fc_app/main.py`、`deploy/nginx/nginx.conf`

## 面试问法汇总

### 基础设施层

- Git：git merge 和 rebase 的区别是什么？
- Docker：Docker 和虚拟机有什么区别？
- Docker Compose：docker-compose 和 Dockerfile 的区别是什么？
- Nginx：Nginx 反向代理的作用是什么？

### 后端服务层

- Python：Python 的 GIL 是什么？它带来了什么限制？
- FastAPI：FastAPI 和 Flask 的区别是什么？
- Uvicorn：Uvicorn 和 Gunicorn 的区别是什么？
- RAG：RAG 和微调（Fine-tuning）的区别是什么？
- FC：怎么保证模型生成的参数是正确的？

### 前端门户层

- React：useEffect 什么时候执行？依赖数组的作用是什么？
- Vite：Vite 和 Webpack 的区别是什么？
- TypeScript：interface 和 type 的区别是什么？
- TailwindCSS：Tailwind 和传统 CSS 框架（如 Bootstrap）的区别是什么？

### AI / Agent 能力层

- LLM：怎么处理模型幻觉？
- Function Calling：Function Calling 怎么保证安全性？

### 通用

- HTTP / REST API：GET 和 POST 的区别是什么？
