# Nexus Personal AI Workflow Agent — 系统设计文档

- **文档日期**：2026-06-18
- **项目代号**：Nexus
- **项目定位**：面向个人使用、可扩展至团队的 Multi-Agent AI 工作流助手
- **核心目标**：不仅要能作为简历项目展示技术深度，更要让开发者本人每天愿意使用
- **当前状态**：设计阶段，待实现

---

## 1. 项目概述

Nexus 是一个基于 Multi-Agent 架构的个人 AI 工作流助手。它通过多个专业化 Agent 协作，帮助用户完成知识检索、任务规划、工具执行、结果总结等复杂工作流。项目强调**可扩展性**和**真实可用性**：第一阶段聚焦个人使用，后续可平滑扩展为团队 oncall agent。

### 1.1 核心能力

| 能力 | 说明 |
|---|---|
| Multi-Agent 协作 | Orchestrator、Planner、Retriever、Executor、Summarizer、Critic 等 Agent 通过消息总线协同工作 |
| RAG 知识检索 | 基于本地文件、第三方笔记平台、手动输入构建私有知识库 |
| 工具调用 | 统一 Tool Registry 支持本地工具、MCP 服务器、笔记平台 API |
| 流式交互 | Web UI 通过 SSE 实时展示 Agent 思考过程、工具调用和中间结果 |
| 长期记忆 | SQLite 持久化对话历史、Agent 思考链、工具调用记录和用户反馈 |
| 质量评估 | Critic Agent + 规则评估，对回答质量进行多维度打分 |

### 1.2 成功标准

1. **能用**：个人日常知识查询、代码辅助、文件操作能通过 Nexus 完成。
2. **好用**：SSE 实时反馈、多轮对话连贯、工具调用准确、错误恢复稳定。
3. **能展示**：代码结构清晰、架构有深度、技术栈覆盖全面，适合作为 agent 开发岗的核心项目。
4. **可扩展**：从个人版到团队版，架构上只需增加用户隔离、权限、外部消息中间件等模块。

---

## 2. 用户与场景

### 2.1 目标用户

- **第一阶段**：开发者本人（胡智明），作为个人效率工具。
- **第二阶段**：小团队，作为共享的知识库问答和 oncall 辅助工具。

### 2.2 典型使用场景

| 场景 | 示例 |
|---|---|
| 知识库问答 | "我笔记里关于 RAG 评估的方法有哪些？" |
| 代码辅助 | "帮我查一下饥荒 MOD 里处理贴图的脚本逻辑" |
| 文件操作 | "列出我桌面上最近修改的 Python 文件" |
| 网络搜索 | "搜索一下最新的 LangChain 0.3 更新内容" |
| 任务规划 | "帮我规划一下这周准备面试的计划" |
| 工具组合 | "查一下我的 Python 笔记，然后写一个示例代码并运行验证" |

---

## 3. 高层架构

### 3.1 架构图

```
用户 (浏览器)
    │
    ▼
┌─────────────────────────────────────┐
│  Web Gateway                        │
│  FastAPI + SSE Endpoint             │
└──────────────────┬──────────────────┘
                   │ 1. 用户请求
                   ▼
┌─────────────────────────────────────┐
│  Orchestrator Agent（协调器）        │
│  - 理解用户意图                       │
│  - 决定调用哪些 Agent                 │
│  - 聚合结果并返回                     │
└──────────────────┬──────────────────┘
                   │ 2. 发布任务消息
                   ▼
┌─────────────────────────────────────┐
│  Message Bus（内存异步消息总线）      │
│  - Agent 发布/订阅消息                │
│  - 支持同步等待和超时控制              │
└─────┬─────┬─────┬─────┬─────┬───────┘
      │     │     │     │     │
      ▼     ▼     ▼     ▼     ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│ Planner │ │Retriever│ │ Executor│ │Summarizer│ │ Critic  │
│ Agent   │ │ Agent   │ │ Agent   │ │ Agent   │ │ Agent   │
└────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
     │           │           │           │           │
     │           │           │           │           │
     └───────────┴─────┬─────┴───────────┴───────────┘
                       │
                       ▼
             ┌─────────────────┐
             │  Tool Registry  │
             │  工具注册中心    │
             └────────┬────────┘
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ Local Tools │ │ MCP Client  │ │ Note APIs   │
│ 本地文件/代码 │ │ MCP 服务器   │ │ Obsidian/   │
│ 执行         │ │             │ │ Notion/飞书 │
└─────────────┘ └─────────────┘ └─────────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Knowledge Base  │
             │ Chroma 向量库    │
             │ 多集合/来源追踪  │
             └─────────────────┘
                      │
                      ▼
             ┌─────────────────┐
             │  Memory Store   │
             │ SQLite 持久化    │
             │ 对话历史/偏好   │
             └─────────────────┘
```

### 3.2 组件说明

| 组件 | 职责 | 关键技术 |
|---|---|---|
| Web Gateway | 接收用户请求，通过 SSE 推送流式事件 | FastAPI, SSE |
| Orchestrator Agent | 理解意图、分配任务、聚合结果、决定终止条件 | LLM + 状态机 |
| Message Bus | Agent 间异步通信 | asyncio Queue |
| Planner Agent | 将复杂任务拆解为可执行步骤 | LLM + Plan-Execute 模式 |
| Retriever Agent | 从知识库检索相关文档 | RAG + Chroma |
| Executor Agent | 调用工具执行具体操作 | Tool Registry |
| Summarizer Agent | 综合各 Agent 输出，生成最终回答 | LLM |
| Critic Agent | 评估回答质量，必要时要求重试 | LLM-as-a-Judge + 规则 |
| Tool Registry | 统一注册和管理所有工具 | JSON Schema |
| Knowledge Base | 存储向量化文档，支持多集合 | Chroma + LangChain |
| Memory Store | 持久化对话历史和元数据 | SQLite |

---

## 4. Agent 详细设计

### 4.1 Orchestrator Agent

**职责**：系统的"总调度"。

**工作流程**：
1. 接收用户请求。
2. 判断任务类型：简单问答、多步骤任务、需要检索、需要执行工具等。
3. 向 Message Bus 发布任务消息。
4. 等待各 Agent 返回结果。
5. 判断任务是否完成，是否需要重试或补充信息。
6. 将最终结果返回给 Web Gateway。

**关键设计**：
- 维护一个任务状态机（pending → planning → retrieving → executing → summarizing → critiquing → done）。
- 每个任务有唯一 task_id 和超时时间。
- 支持循环：如果 Critic 认为回答质量不够，Orchestrator 可以要求补充检索或重新执行。

### 4.2 Planner Agent

**职责**：为复杂任务制定执行计划。

**触发条件**：Orchestrator 判断任务需要多个步骤时。

**输出示例**：
```json
{
  "steps": [
    {"step_id": 1, "agent": "retriever", "task": "检索知识库中关于 RAG 评估的内容"},
    {"step_id": 2, "agent": "executor", "task": "调用 execute_python 计算 BLEU 和 BERTScore 区别"},
    {"step_id": 3, "agent": "summarizer", "task": "总结检索结果和计算结果，生成最终回答"}
  ]
}
```

### 4.3 Retriever Agent

**职责**：从知识库检索与用户问题相关的文档片段。

**能力**：
- 根据 query 选择最合适的集合（collection）。
- 支持多集合联合检索。
- 返回带来源标识的文本片段。

### 4.4 Executor Agent

**职责**：调用具体工具执行操作。

**能力**：
- 从 Tool Registry 查询可用工具。
- 解析工具参数，调用工具函数。
- 处理工具执行异常，返回错误信息。

### 4.5 Summarizer Agent

**职责**：综合所有中间结果，生成面向用户的最终回答。

**输入**：原始问题、检索结果、工具执行结果、Planner 的计划。
**输出**：自然语言回答，可能包含引用来源和后续建议。

### 4.6 Critic Agent

**职责**：评估最终回答质量。

**评估维度**：
- 正确性：是否有事实错误。
- 相关性：是否回答了用户问题。
- 完整性：是否遗漏关键信息。
- 安全性：是否有害或敏感内容。

**行为**：
- 如果得分低于阈值，向 Orchestrator 反馈需要重试。
- 如果得分达标，任务结束。

---

## 5. Message Bus 设计

### 5.1 消息格式

```python
class Message:
    task_id: str
    sender: str       # Agent 名称或 "orchestrator"
    recipient: str    # Agent 名称或 "broadcast"
    message_type: str # "task", "result", "plan", "tool_call", "critique"
    payload: dict
    timestamp: float
```

### 5.2 通信模式

1. **点对点**：Orchestrator → Planner
2. **广播**：Orchestrator 发布任务，所有订阅 Agent 都能收到
3. **结果回传**：各 Agent → Orchestrator

### 5.3 实现方式

- 使用 Python `asyncio.Queue` 实现内存消息总线。
- 每个 Agent 有一个输入队列。
- Orchestrator 通过 `await` 等待关键结果，支持超时。

**优点**：零部署、代码清晰、适合个人使用和简历演示。
**缺点**：不支持分布式。团队版后续可替换为 Redis/RabbitMQ。

---

## 6. Tool Registry 设计

### 6.1 工具接口

```python
class Tool:
    name: str
    description: str
    parameters: dict  # JSON Schema
    handler: Callable  # 实际执行函数
    source: str       # "local", "mcp", "note_api"
```

### 6.2 工具分类

| 类别 | 示例工具 | 来源 |
|---|---|---|
| 本地工具 | read_file, list_files, execute_python, search_local | local |
| 网络工具 | web_search, fetch_url | local |
| MCP 工具 | 通过 MCP 协议接入的各种服务器工具 | mcp |
| 笔记平台 | obsidian_search, notion_query | note_api |

### 6.3 MCP 集成

- 实现一个轻量级 MCP Client。
- 通过 stdio 或 SSE 连接 MCP Server。
- 将 MCP Server 提供的工具注册到 Tool Registry。

### 6.4 安全考虑

- `execute_python` 必须基于 AST 做受限执行，禁止 `__import__`、`open`、网络请求等危险操作。
- 文件读取限制在指定工作目录内，防止越权访问。
- MCP 工具需要有明确的权限控制。

---

## 7. RAG 与知识库设计

### 7.1 多集合支持

知识库按来源和用途分为不同集合：

| 集合名 | 用途 | 来源 |
|---|---|---|
| `notes` | 个人笔记 | Obsidian / Notion / 本地 Markdown |
| `code_docs` | 代码项目文档 | 本地代码仓库 README / 注释 |
| `web_articles` | 收藏的网页文章 | 手动导入或浏览器插件 |
| `manual` | 手动粘贴的知识 | 用户输入 |

### 7.2 文档处理流程

```
文档加载 → 文本分块 → Embedding 向量化 → 存入 Chroma 集合
                                          ↓
用户提问 → 问题向量化 → 相似度检索 → 返回 Top-K 片段 + 来源
```

### 7.3 来源追踪

每个检索结果包含 metadata：
- `source`: 文件路径或 URL
- `collection`: 所属集合
- `chunk_index`: 块编号

最终回答中展示引用来源，便于用户验证。

---

## 8. Web UI + SSE 设计

### 8.1 后端接口

| 接口 | 方法 | 说明 |
|---|---|---|
| `/chat` | POST | 发起对话，返回 SSE 流 |
| `/sessions` | GET/POST | 获取/创建会话 |
| `/sessions/{id}/messages` | GET | 获取历史消息 |
| `/knowledge/upload` | POST | 上传文档到知识库 |
| `/knowledge/collections` | GET | 获取知识库集合列表 |
| `/tools` | GET | 获取可用工具列表 |

### 8.2 SSE 事件类型

```
event: agent_thought
data: {"agent": "planner", "content": "需要检索知识库并执行代码"}

event: tool_call
data: {"tool": "search_docs", "arguments": {"query": "RAG 评估"}}

event: tool_result
data: {"tool": "search_docs", "result": "..."}

event: final_answer
data: {"content": "...", "sources": [...]}

event: error
data: {"message": "..."}
```

### 8.3 前端设计

- 左侧：会话列表 + 知识库管理
- 中间：对话区域，展示 Agent 思考过程、工具调用、最终回答
- 右侧：工具状态 / 来源引用

---

## 9. Memory Store 设计

### 9.1 数据表

| 表名 | 字段 | 用途 |
|---|---|---|
| `sessions` | id, title, created_at, updated_at | 会话管理 |
| `messages` | id, session_id, role, content, created_at | 消息历史 |
| `agent_traces` | id, message_id, agent, thought, tool_calls, result | Agent 思考链 |
| `feedback` | id, message_id, rating, comment | 用户反馈 |
| `preferences` | key, value | 用户偏好 |

### 9.2 使用方式

- 每次对话开始时加载历史消息作为上下文。
- Orchestrator 可参考历史会话中的用户偏好。
- 用户反馈用于后续评估模型调优。

---

## 10. 错误处理与监控

### 10.1 错误类型

| 错误类型 | 处理方式 |
|---|---|
| LLM API 异常 | 重试 3 次，失败后返回错误提示 |
| 工具执行失败 | 将错误信息返回给 Orchestrator，由其决定是否重试或换工具 |
| 检索无结果 | 提示用户补充文档或换个问法 |
| 超时 | Orchestrator 终止任务并返回超时提示 |
| 死循环 | max_turns 限制，防止无限循环 |

### 10.2 日志

- 所有 Agent 行为、工具调用、消息流转记录到日志。
- 支持日志级别：DEBUG、INFO、WARNING、ERROR。

---

## 11. 测试策略

### 11.1 单元测试

- `tests/test_agents.py`：测试各 Agent 基础行为。
- `tests/test_message_bus.py`：测试消息发布/订阅。
- `tests/test_tools.py`：测试工具函数。
- `tests/test_rag.py`：测试检索流程。

### 11.2 集成测试

- `tests/test_workflows.py`：测试完整工作流，如"检索 + 执行 + 总结"。

### 11.3 评估测试

- 维护一个 `test_cases.json`，包含标准问题和期望回答。
- 定期运行评估，记录准确率、相关性得分等指标。

---

## 12. 实现阶段规划

### 阶段 1：Multi-Agent 内核 + 消息总线（1-2 周）

- [ ] 实现 Message Bus
- [ ] 实现 Orchestrator Agent
- [ ] 实现 Planner / Retriever / Executor / Summarizer / Critic Agent 基础版本
- [ ] 实现 Agent 间基本协作流程
- [ ] 编写单元测试

**可展示成果**：一个能跑的多 Agent 协作 demo，命令行交互。

### 阶段 2：RAG + 工具系统（1-2 周）

- [ ] 重构现有 RAG 模块，支持多集合
- [ ] 实现 Tool Registry
- [ ] 实现本地工具（read_file, list_files, execute_python, search_local）
- [ ] 实现 MCP Client 基础版
- [ ] 将 RAG 接入 Retriever Agent
- [ ] 将工具接入 Executor Agent

**可展示成果**：Agent 能检索知识库、调用本地工具。

### 阶段 3：Web UI + SSE（1 周）

- [ ] 实现 FastAPI SSE 接口
- [ ] 实现前端页面
- [ ] 实时展示 Agent 思考过程和工具调用
- [ ] 会话管理

**可展示成果**：浏览器中可用的 Web 版 Agent。

### 阶段 4：记忆持久化 + 评估优化（1 周）

- [ ] 实现 SQLite Memory Store
- [ ] 持久化对话历史和 Agent Trace
- [ ] 增强 Critic Agent 评估能力
- [ ] 设计并运行测试用例集
- [ ] 收集评估指标

**可展示成果**：有长期记忆、有评估数据、能持续优化。

### 阶段 5：团队版扩展（未来）

- [ ] 用户认证与权限
- [ ] 共享知识库
- [ ] 外部消息中间件（Redis/RabbitMQ）
- [ ] oncall 工作流支持
- [ ] 告警接入与自动分派

---

## 13. 技术栈

| 层级 | 技术 |
|---|---|
| 编程语言 | Python 3.10+ |
| Web 框架 | FastAPI |
| 前端 | 原生 HTML + CSS + JS |
| 大模型 | 通义千问 / 其他兼容 OpenAI API 的模型 |
| Embedding | text-embedding-v3 / 其他 |
| 向量数据库 | Chroma |
| RAG 框架 | LangChain |
| 持久化 | SQLite |
| 消息总线 | asyncio Queue（未来可替换为 Redis） |
| MCP | 自定义 MCP Client |
| 测试 | pytest |

---

## 14. LLM Provider 抽象设计

为了支持灵活切换不同大模型提供商，项目将引入统一的 **LLM Client** 抽象层。

### 14.1 设计目标

- **厂商解耦**：Agent、RAG、Critic 等模块不直接依赖具体 LLM SDK。
- **配置驱动**：通过 `.env` 切换模型，无需修改业务代码。
- **默认低成本**：默认使用通义千问（qwen-turbo），利用免费/低成本额度。
- **未来可扩展**：后续可无缝切换为 Kimi、DeepSeek、OpenAI 等兼容 OpenAI API 的模型。

### 14.2 统一接口

```python
# core/llm.py
from typing import Any, Dict, List, Optional

class LLMClient:
    def __init__(self, provider: str, model: str, api_key: str, base_url: str = None):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.client = self._create_client()

    def _create_client(self):
        if self.provider in ("openai", "kimi", "deepseek"):
            from openai import OpenAI
            return OpenAI(api_key=self.api_key, base_url=self.base_url)
        elif self.provider == "qwen":
            import dashscope
            dashscope.api_key = self.api_key
            return dashscope.Generation
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def chat(self, messages: List[Dict], tools: Optional[List[Dict]] = None, stream: bool = False) -> Any:
        if self.provider == "qwen":
            return self.client.call(
                model=self.model,
                messages=messages,
                tools=tools,
                result_format="message",
            )
        else:
            return self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                stream=stream,
            )
```

### 14.3 环境变量配置

```bash
# .env.example（默认使用通义千问）
LLM_PROVIDER=qwen
LLM_MODEL=qwen-turbo
LLM_API_KEY=your-dashscope-api-key

# 切换到 Kimi 时只需修改以下几行
# LLM_PROVIDER=kimi
# LLM_MODEL=moonshot-v1-auto
# LLM_API_KEY=your-moonshot-api-key
# LLM_BASE_URL=https://api.moonshot.cn/v1

# 切换到 DeepSeek
# LLM_PROVIDER=deepseek
# LLM_MODEL=deepseek-chat
# LLM_API_KEY=your-deepseek-api-key
# LLM_BASE_URL=https://api.deepseek.com
```

### 14.4 对不同厂商的适配点

| 功能 | 通义千问 | Kimi / DeepSeek / OpenAI |
|---|---|---n      |
| 普通对话 | `dashscope.Generation.call` | `openai.ChatCompletion.create` |
| Function Calling | `tools` + `tool_calls` | `tools` + `tool_calls`（兼容） |
| 流式输出 | `stream=True` | `stream=True` |
| Embedding | `DashScopeEmbeddings` | `OpenAIEmbeddings`（或其他） |

**注意**：通义千问的 Function Calling 返回格式与 OpenAI 标准略有差异，LLM Client 需要统一封装，对外提供一致的 `tool_calls` 结构。

### 14.5 对项目的影响

- 所有 Agent 通过 `LLMClient.chat()` 调用模型。
- RAG 生成模块通过 `LLMClient.chat()` 调用模型。
- Critic Agent 通过 `LLMClient.chat()` 调用模型。
- 切换模型只需改 `.env`，业务代码零改动。

---

## 15. 风险与权衡

| 风险 | 影响 | 缓解措施 |
|---|---|---|
| Multi-Agent 复杂度导致开发周期过长 | 高 | 严格分阶段实现，每个阶段都有可运行版本 |
| LLM API 成本高 | 中 | 默认使用通义千问低成本模型，支持随时切换 |
| 工具安全风险 | 中 | execute_python 做 AST 受限执行，文件操作限制工作目录 |
| 知识库质量差导致回答不准 | 中 | Critic Agent 评估 + 用户反馈闭环 |
| 过度设计导致代码难以维护 | 高 | 每个 Agent 职责单一，接口清晰，保持小而美的模块 |

---

## 16. 与现有 ai-demos 的关系

本次设计是对现有 `ai-demos` 项目的重大升级：
- 保留并增强 RAG 模块（多集合、来源追踪）。
- 保留安全 Python 执行、文件操作等工具。
- 从单 Agent Function Calling 升级为 Multi-Agent 协作架构。
- 新增 Message Bus、Planner、Critic、Memory Store 等组件。
- 新增 Web SSE 流式交互。
- 新增 LLM Provider 抽象，支持通义千问 / Kimi / DeepSeek 等模型切换。

现有 ai-demos 中的代码将作为 Nexus 的基础模块被重构和复用。

---

## 17. 下一步

1. 用户审查并批准本设计文档。
2. 使用 `superpowers:writing-plans` 制定详细实现计划。
3. 按阶段 1 开始编码。
