# 更新日志

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
