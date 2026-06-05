# AI Agent Demo 项目集

两个面向 AI Agent 岗位面试的 Demo 项目，基于通义千问大模型 API 构建。

---

## 项目一：RAG 智能文档问答系统

基于检索增强生成（Retrieval-Augmented Generation）技术的文档问答系统，支持上传 PDF/TXT 文档后通过自然语言提问获取精准回答。

### 解决的问题

传统大模型问答存在两个痛点：
1. **知识滞后**：模型训练数据有截止日期，无法回答最新信息
2. **幻觉问题**：对于专业领域内容，模型可能编造不存在的知识

RAG 通过将用户私有文档向量化存储，在问答时先检索相关片段再交给大模型生成答案，既解决了知识更新问题，又显著降低了幻觉风险。

### 技术栈

| 层级 | 技术 | 说明 |
|---|---|---|
| 大模型 | 通义千问 (qwen-turbo) | 阿里云百炼平台，免费额度充足 |
| 向量嵌入 | text-embedding-v3 | 通义千问 Embedding 模型，1024 维 |
| 向量数据库 | Chroma | 轻量级、纯 Python、本地持久化 |
| 文档加载 | LangChain (TextLoader / PyPDFLoader) | 支持 TXT / PDF 格式 |
| 文本分块 | RecursiveCharacterTextSplitter | 按语义边界递归切分 |
| Web 框架 | FastAPI | 高性能异步 Web 框架 |
| 前端 | 原生 HTML + CSS + JS | 拖拽上传、对话式交互 |

### 运行方式

```bash
# Web 服务（端口 8000）
python -m uvicorn app:app --reload

# 命令行交互版
python rag.py
```

浏览器访问: http://127.0.0.1:8000

### 学习脚本（按顺序阅读）

1. `step1_load_docs.py` — Document 对象和文档加载
2. `step2_split_text.py` — 文本分块原理（chunk_size / chunk_overlap）
3. `step3_build_vectorstore.py` — Embedding 和向量数据库
4. `step4_rag_qa.py` — 完整检索 + 生成流程

---

## 项目二：Function Calling 智能任务 Agent

基于大模型 Function Calling 能力的任务调度 Agent，能够解析用户自然语言指令，自动判断并调用相应工具完成任务。

### 解决的问题

大模型本身不能执行实际操作（如查实时天气、发邮件、精确计算），Function Calling 让模型具备了"决策 + 调用外部工具"的能力，实现了从"对话"到"行动"的跨越。

### 技术栈

| 层级 | 技术 | 说明 |
|---|---|---|
| 大模型 | 通义千问 (qwen-turbo) | 支持 Function Calling |
| 工具定义 | JSON Schema | 向模型描述工具的能力与参数 |
| 核心逻辑 | 对话循环 | 模型推理 → 工具执行 → 结果回传 → 再次推理 |
| Web 框架 | FastAPI | 提供 REST API 和前端界面 |
| 前端 | 原生 HTML + CSS + JS | 对话式交互，展示工具调用过程 |

### 支持的工具

| 工具 | 功能 | 状态 |
|---|---|---|
| `get_weather` | 查询指定城市天气 | Mock 数据 |
| `calculate` | 数学表达式计算 | 真实实现 |
| `set_reminder` | 设置提醒事项 | Mock 实现 |

### 运行方式

```bash
# Web 服务（端口 8001）
python -m uvicorn agent_app:app --reload --port 8001

# 命令行交互版
python agent.py
```

浏览器访问: http://127.0.0.1:8001

### 学习脚本（按顺序阅读）

1. `step1_tools.py` — 工具函数定义和 JSON Schema 格式
2. `step2_agent_loop.py` — Function Calling 核心对话循环

---

## 项目结构

```
ai-demos/
├── app.py                      # RAG: FastAPI Web 服务
├── rag.py                      # RAG: 命令行版完整流程
├── step1_load_docs.py          # RAG Step 1: 文档加载
├── step2_split_text.py         # RAG Step 2: 文本分块
├── step3_build_vectorstore.py  # RAG Step 3: 向量化 + 建库
├── step4_rag_qa.py             # RAG Step 4: 检索 + 问答
├── agent_app.py                # Agent: FastAPI Web 服务
├── agent.py                    # Agent: 命令行版完整流程
├── step1_tools.py              # Agent Step 1: 工具定义
├── step2_agent_loop.py         # Agent Step 2: 对话循环
├── test_api.py                 # API 连通性测试
├── sample_docs/                # 示例文档
│   └── python_guide.txt
├── .env.example                # 环境变量模板
├── .gitignore                  # Git 忽略规则
├── requirements.txt            # 依赖列表
└── README.md                   # 本文件
```

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/shiyuan-wreg/ai-demos.git
cd ai-demos
```

### 2. 配置环境

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置 API Key

```bash
cp .env.example .env
# 编辑 .env，填入你的通义千问 API Key
# 从阿里云百炼获取: https://bailian.console.aliyun.com/
```

### 4. 运行

**RAG 项目：**
```bash
python -m uvicorn app:app --reload --port 8000
```

**Agent 项目（另开终端）：**
```bash
python -m uvicorn agent_app:app --reload --port 8001
```

---

## RAG 核心流程

```
用户上传文档
    │
    ▼
Document Loader → Text Splitter → Embedding → Chroma Vector Store
                                                  │
用户提问 ──▶ 问题向量化 ──▶ 相似度检索 ────────┘
                                                  │
                                                  ▼
                                    相关文本片段 → Prompt 拼接
                                                  │
                                                  ▼
                                         LLM 生成最终答案
```

## Function Calling 核心流程

```
用户输入
    │
    ▼
模型推理（带 tools 参数）
    │
    ├──▶ 需要调用工具 ──▶ 执行工具函数 ──▶ 结果传回模型 ──▶ 再次推理
    │                                                              │
    │                                                              ▼
    │                                                       生成最终回答
    │
    └──▶ 不需要工具 ──▶ 直接生成回答
```

---

## API 接口

### RAG - 上传文档
```bash
curl -X POST "http://127.0.0.1:8000/upload" -F "file=@文档.pdf"
```

### RAG - 问答
```bash
curl -X POST "http://127.0.0.1:8000/chat" -d "query=Python异常处理怎么做"
```

### Agent - 对话
```bash
curl -X POST "http://127.0.0.1:8001/chat" -d "query=北京今天天气怎么样"
```

### Agent - 清空历史
```bash
curl -X POST "http://127.0.0.1:8001/clear"
```

---

## 演示截图

> 截图待补充：RAG 上传界面、RAG 问答界面、Agent 对话界面

---

## 参考资源

- [LangChain RAG 官方教程](https://python.langchain.com/docs/tutorials/rag/)
- [通义千问 API 文档](https://help.aliyun.com/document_detail/611472.html)
- [OpenAI Function Calling 文档](https://platform.openai.com/docs/guides/function-calling)
- [Chroma 文档](https://docs.trychroma.com/)

## License

MIT
