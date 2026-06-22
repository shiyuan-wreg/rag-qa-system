# 基于 RAG + Function Calling 的智能文档任务 Agent

一个整合 **检索增强生成（RAG）** 与 **Function Calling** 的智能 Agent 系统，支持基于知识库的问答、代码执行、文件读取等多工具协同，并内置回答质量评估模块。

---

## 解决的问题

传统大模型应用存在三个痛点：

1. **知识滞后**：模型训练数据有截止日期，无法回答最新或私有领域知识
2. **幻觉问题**：模型可能编造不存在的信息
3. **无法行动**：模型只能生成文本，不能直接执行计算、读取文件等操作

本项目通过 **RAG 检索 + 工具调用 + 质量评估** 的组合，让 Agent 能够：
- 基于私有知识库回答问题
- 执行 Python 计算、读取文件、列出目录等真实操作
- 自动评估回答质量，形成"生成-评估-优化"闭环

---

## 系统架构

```
用户输入
    │
    ▼
┌─────────────┐
│  Agent 核心  │  ← 多轮对话 + 工具决策 + 错误恢复
│  (core/)    │
└──────┬──────┘
       │
       ▼
是否需要调用工具？ ──否──▶ 直接生成回答
       │
       是
       │
       ▼
┌─────────────────────────────────────┐
│  search_docs  │ execute_python     │
│  read_file    │ list_files         │
└─────────────────────────────────────┘
       │
       ▼
工具执行结果回传 → 模型再次推理 → 最终回答
       │
       ▼
┌─────────────┐
│  质量评估模块 │  ← 正确性、相关性、完整性、安全性
│  (eval/)    │
└─────────────┘
```

---

## 核心能力

### 1. RAG 知识检索

- 文档加载、文本分块、Embedding 向量化
- 基于 Chroma 向量数据库的语义检索
- 检索结果作为上下文注入 Prompt

### 2. Function Calling 工具调用

| 工具名 | 功能 | 说明 |
|---|---|---|
| `search_docs` | 检索知识库 | 原 RAG 能力封装为工具 |
| `execute_python` | 安全执行 Python 表达式 | 替换不安全的 `eval`，基于 AST 受限执行 |
| `read_file` | 读取文件内容 | 真实文件操作 |
| `list_files` | 列出目录内容 | 真实文件操作 |

### 3. Agent 核心循环

- 多轮对话上下文管理
- 自动判断是否需要调用工具
- 支持多步骤任务（一次输入触发多次工具调用）
- 最大循环次数保护，防止死循环
- 工具执行失败不影响整体流程

### 4. 回答质量评估

- **规则评估**：快速评估正确性、相关性、完整性、安全性
- **LLM-as-a-Judge**：使用更强的模型进行多维度评分
- **测试用例集**：固定问题自动跑分，输出平均得分

---

## 项目结构

```
ai-demos/
├── main.py                 # Nexus 多智能体命令行入口
├── requirements.txt
├── .env.example
├── backends/               # Web 后端(各自容器化)
│   ├── rag_app/main.py     # RAG 问答 FastAPI 服务
│   └── fc_app/main.py      # Function Calling FastAPI 服务
├── frontends/              # 前端
│   ├── portfolio/          # 统一门户外壳(React+Vite+TS+Tailwind)
│   └── nexus-learning-web/ # Nexus 交互式学习站
├── deploy/                 # 部署:docker-compose + nginx + 脚本
│   ├── docker-compose.yml
│   ├── nginx/nginx.conf
│   ├── build-frontends.sh
│   └── README.md           # 本地运行步骤
├── core/                   # Nexus 内核
│   ├── agents/             # Orchestrator/Planner/Retriever/Executor/Summarizer/Critic
│   ├── llm.py message_bus.py message.py session.py config.py
│   ├── agent.py tools.py rag_tool.py   # RAG demo 依赖的单体 Agent
├── rag/                    # RAG 模块(loader/splitter/vectorstore/retriever)
├── eval/                   # 回答质量评估
├── tests/                  # 单元测试
└── docs/                   # 文档(specs/plans/learning/career + 知识库)
```

> 说明:旧的 `app.py` 已迁入 `backends/rag_app/main.py`,旧 `legacy/` demo 已删除(保留在 git 历史)。本地一键启动见 `deploy/README.md`。

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

### 4. 运行命令行版

```bash
python main.py
```

支持的命令：
- `/clear` - 清空对话历史
- `/history` - 查看对话历史
- `/eval` - 运行测试用例评估
- `/quit` - 退出

### 5. 运行 Web 版

```bash
python -m uvicorn app:app --reload --port 8000
```

浏览器访问: http://127.0.0.1:8000

---

## 使用示例

### 知识库问答

```
你: Python 中列表和元组有什么区别？
Agent: 根据检索到的文档内容，列表（list）和元组（tuple）的主要区别是...
```

### 代码执行

```
你: 帮我算一下 (15 + 27) * 3
Agent: 调用 execute_python 工具...
      计算结果: 126
```

### 文件读取

```
你: 读取 docs/python_guide.txt 文件的前几行
Agent: 调用 read_file 工具...
      文件内容: ...
```

### 目录查看

```
你: 当前目录下有什么文件？
Agent: 调用 list_files 工具...
      目录 '.' 内容: ...
```

---

## API 接口

### 对话

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
     -d "query=Python 中列表和元组有什么区别"
```

### 清空历史

```bash
curl -X POST "http://127.0.0.1:8000/clear"
```

### 运行评估

```bash
curl -X POST "http://127.0.0.1:8000/eval"
```

---

## 运行测试

```bash
python tests/test_tools.py
python tests/test_agent.py
```

或使用 pytest：

```bash
pytest tests/
```

---

## 评估结果示例

```json
{
  "average_score": 0.72,
  "results": [
    {
      "query": "Python 中列表和元组有什么区别？",
      "answer": "根据检索结果，...",
      "scores": {
        "correctness": 0.8,
        "relevance": 0.9,
        "completeness": 0.7,
        "safety": 1.0,
        "overall": 0.85
      }
    }
  ]
}
```

---

## 未来扩展

- [ ] 支持多文档管理
- [ ] 接入 MOD 开发文档作为真实知识库
- [ ] 增加代码审查工具
- [ ] 增加执行脚本/命令的工具
- [ ] 支持多用户会话隔离
- [ ] 接入更多 Embedding 模型和向量数据库

---

## 技术栈

- **大模型**: 通义千问 (qwen-turbo)
- **Embedding**: text-embedding-v3
- **向量数据库**: Chroma
- **RAG 框架**: LangChain
- **Web 框架**: FastAPI
- **编程语言**: Python 3.10+

---

## 参考资源

- [LangChain RAG 官方教程](https://python.langchain.com/docs/tutorials/rag/)
- [通义千问 API 文档](https://help.aliyun.com/document_detail/611472.html)
- [OpenAI Function Calling 文档](https://platform.openai.com/docs/guides/function-calling)
- [Chroma 文档](https://docs.trychroma.com/)

## License

MIT
