# 更新日志

## [v2.1.0] - 2026-06-22

### 新增

- **个人集成学习网站(作品集门户)Phase 1**
  - 整合多个 Web 项目为统一门户,方案 C(统一 React 外壳 + iframe 嵌入)
  - monorepo 重组:`backends/`(rag_app, fc_app)、`frontends/`(portfolio, nexus-learning-web)、`deploy/`
  - `frontends/portfolio`:React+Vite+TS+Tailwind 门户外壳(首页/导航/AI 作品 iframe 页/学习跳转/个人页)
  - `deploy/`:Dockerfile(rag/fc)+ nginx 反向代理 + docker-compose 编排 + 前端构建脚本
  - 本地 `docker compose up` 一键跑通,Nginx 8080 统一入口反代各后端
  - 设计文档、实现计划、配套学习文档、本地运行指南

### 架构调整

- 旧 `app.py` → `backends/rag_app/main.py`;旧 `legacy/agent_app.py` → `backends/fc_app/main.py`
- 删除 `legacy/`(保留在 git 历史);抽离 `agent-console-ai`(独立课程设计项目)
- RAG/FC 内联前端改用相对 fetch 路径以适配子路径反代
- 新增 `.gitattributes` 强制 shell/Dockerfile/conf 用 LF;`.gitignore` 增加前端构建产物安全网

### 技术栈扩展

- Nginx + Docker + docker-compose;React Router

---

## [v2.0.0] - 2026-06-18

### 新增

- **Nexus Multi-Agent 内核（Phase 1）**
  - `core/llm.py`：统一 LLM Client，默认通义千问，预留 Kimi/DeepSeek/OpenAI 兼容接口
  - `core/message_bus.py`：内存异步消息总线，支持发布/订阅、send-and-wait、超时控制
  - `core/message.py`：标准化 Message 数据结构
  - `core/session.py`：任务状态跟踪
  - `core/agents/base.py`：Agent 基类与消息循环
  - `core/agents/orchestrator.py`：Orchestrator 协调器，串联完整工作流
  - `core/agents/planner.py`：Planner 规划器，将用户需求拆解为执行步骤
  - `core/agents/retriever.py`：Retriever 检索器（Phase 1 mock）
  - `core/agents/executor.py`：Executor 执行器（Phase 1 mock）
  - `core/agents/summarizer.py`：Summarizer 总结器
  - `core/agents/critic.py`：Critic 评估器，多维度回答质量评分
  - `main.py`：命令行入口，启动所有 Agent 并交互
  - 完整的 pytest 测试覆盖（14 个新测试）

### 架构调整

- 将原有 RAG + Function Calling 两个独立 demo 重构为 Nexus Agent 系统的基础模块
- 旧 demo 代码迁移至 `legacy/` 目录备份
- 新增 `docs/superpowers/specs/` 设计文档和 `docs/superpowers/plans/` 实现计划

### 技术栈扩展

- Python 3.12 + LangChain + 通义千问 API + Chroma + FastAPI
- asyncio 异步消息总线
- pytest + pytest-asyncio 测试框架

---

## [v1.1.0] - 2026-06-05

### 新增

- **Function Calling 智能任务 Agent**
  - `agent.py`：命令行交互版 Agent，支持天气查询、数学计算、设置提醒
  - `agent_app.py`：FastAPI Web 版，提供对话界面和工具调用可视化
  - `step1_tools.py`：工具定义学习脚本，讲解 JSON Schema 格式
  - `step2_agent_loop.py`：核心对话循环学习脚本，展示 Function Calling 完整流程
  - 支持多轮对话上下文管理
  - 支持单工具 / 多步骤任务（如"查天气，如果下雨提醒我带伞"）
  - 单个工具失败不影响整体（异常隔离）

### 修改

- `README.md`：重构为双项目说明，新增 Agent 项目的技术栈、运行方式、API 接口

---

## [v1.0.0] - 2026-06-05

### 新增

- **RAG 智能文档问答系统**
  - `app.py`：FastAPI Web 服务，支持文件上传 + 对话问答 + 前端界面
  - `rag.py`：命令行交互版完整 RAG 流程
  - `step1_load_docs.py`：文档加载学习脚本
  - `step2_split_text.py`：文本分块学习脚本（RecursiveCharacterTextSplitter）
  - `step3_build_vectorstore.py`：向量化 + Chroma 建库学习脚本
  - `step4_rag_qa.py`：检索 + 问答学习脚本
  - `test_api.py`：API 连通性测试脚本
  - 支持 TXT / PDF 文档上传与解析
  - 支持向量相似度检索（余弦相似度）
  - 支持基于检索结果的 Prompt 拼接与大模型回答生成
  - 前端支持拖拽上传、对话式交互、参考片段展示
  - `.env` + `.gitignore` 配置，API Key 安全存储

### 技术栈

- Python 3.12 + LangChain + 通义千问 API + Chroma + FastAPI
