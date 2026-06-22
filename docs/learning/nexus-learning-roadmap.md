# Nexus 系统学习路线图：从 AI 基础到完整 Agent 产品

> 适用对象：胡智明（23 级软件工程本科）
> 对应项目：C:\Users\hzs17\Desktop\ai-demos（Nexus）
> 文档日期：2026-06-21
> 学习周期：建议 6 ~ 8 周
> 前置要求：Python 基础语法、HTTP 基础、了解 RESTful API

---

## 写在最前面：这份路线图怎么用

这份文档不是让你在一天内读完的。它是一个**分层递进的学习系统**，每一层建立在前一层之上。

建议你按这个节奏来：

- **第 1 ~ 2 周**：读完第一部分（前置基础），建立概念地基。
- **第 3 ~ 4 周**：读完第二部分（Nexus 架构），对照 ai-demos 代码逐章理解。
- **第 5 ~ 6 周**：读完第三部分（工程化与求职），同时动手做练习。
- **第 7 ~ 8 周**：把项目跑通，准备面试口述。

每一章后面都有"自测问题"和"动手练习"。如果你能独立回答自测问题并完成练习，说明这一层已经掌握。

学习过程中有一条主线贯穿始终：

> **从"AI 工具的使用者"成长为"AI 系统的设计者"。**

这意味着你不仅要会用 LangChain、会调 API，还要理解为什么这样设计、怎么评估效果、怎么改进系统。

---

# 第一部分：前置基础

## 第 1 章：大语言模型（LLM）基础

### 1.1 什么是大语言模型

大语言模型（Large Language Model，LLM）是一种经过海量文本训练的神经网络。它的核心能力是：**根据前文预测下一个词**。

比如你输入"今天天气很"，模型会计算接下来最可能出现的词："好"、"热"、"冷"、"糟糕"……然后按概率选一个输出。

这个能力看起来简单，但训练数据足够大、模型参数量足够多时，它会涌现出很多复杂能力：回答问题、写代码、翻译、总结、推理等。

### 1.2 Token 是什么

模型不是直接处理"字"或"词"，而是处理 **Token**。Token 是文本的最小处理单元，可能是一个字、一个词，也可能是一个词的一部分。

例如：

- "你好" 可能是 2 个 token
- "hello" 可能是 1 个 token
- "unbelievable" 可能被拆成 "un"、"believ"、"able" 等子词

**为什么要了解 token**：

- 模型的计费通常按 token 数量计算。
- 模型的上下文窗口（能处理的 token 数）是有限的。
- 提示词太长时，要么被截断，要么增加成本。

### 1.3 上下文窗口

上下文窗口（Context Window）是模型一次能看到的最大 token 数量。常见大小：

| 模型 | 上下文窗口 |
|---|---|
| GPT-3.5 | 16K |
| GPT-4 | 128K |
| 通义千问 qwen-turbo | 128K |
| Kimi moonshot-v1 | 200K |

**上下文窗口的限制意味着什么**：

- 不能一次性塞无限长的文档。
- RAG 的出现就是为了解决这个问题：先把长文档切成小块，只把相关的几块传给模型。
- Agent 的多轮对话会累积历史消息，太长时需要做上下文压缩或摘要。

### 1.4 温度参数（Temperature）

Temperature 控制模型输出的随机性。

- **Temperature = 0**：模型总是选择概率最高的词，输出稳定、确定。
- **Temperature = 1**：模型按原始概率采样，输出更有创意但可能不稳定。
- **Temperature > 1**：输出更随机，可能胡言乱语。

**使用建议**：

- 需要稳定结果时（如工具调用参数生成、JSON 输出）：用 0 ~ 0.3。
- 需要创意时（如写作、头脑风暴）：用 0.7 ~ 1.0。

### 1.5 提示词工程（Prompt Engineering）基础

提示词工程是指通过设计输入文本，引导模型产生更好的输出。常见技巧：

**1. 角色设定**

```
你是一位经验丰富的 Python 后端工程师。
```

**2. 任务描述清晰**

```
请解释 Python 中列表和元组的区别，并给出代码示例。
```

**3. 输出格式约束**

```
请只输出 JSON 格式，不要添加其他解释。
```

**4. 少样本示例（Few-shot）**

```
输入：苹果
输出：{"类别": "水果", "颜色": "红色"}

输入：汽车
输出：{"类别": "交通工具", "颜色": "多样"}

输入：猫
输出：
```

**5. 思维链（Chain of Thought, CoT）**

```
请一步一步思考，并展示推理过程。
```

### 自测问题

1. 为什么说 LLM 的核心能力是"预测下一个词"？
2. Token 和字有什么区别？为什么计费按 token？
3. 上下文窗口有限会带来什么问题？RAG 怎么解决？
4. Temperature 在什么场景下应该设低？
5. 举出三种提示词工程技巧。

### 动手练习

1. 打开通义千问或 Kimi 的网页版，分别用 Temperature 0 和 1 问同一个开放性问题，观察差异。
2. 写三个不同风格的 prompt，让模型用 JSON 输出同一类信息。

---

## 第 2 章：从 LLM 到 Agent

### 2.1 什么是 Agent

Agent（智能体）是指能够**感知环境、做出决策、执行行动**的系统。

普通 LLM 应用：用户输入 → 模型输出文本 → 结束。

Agent：用户输入 → 模型思考 → 决定调用工具 → 执行工具 → 观察结果 → 再思考 → 继续行动 → 直到完成目标。

关键区别：Agent 有**行动能力**和**循环能力**。

### 2.2 为什么需要 Agent

LLM 有两个明显短板：

1. **知识有截止日期**：模型不知道最新发生的事情。
2. **无法直接操作世界**：模型不能查数据库、不能执行代码、不能发邮件。

Agent 通过调用外部工具弥补这些短板：

- 用搜索引擎获取最新信息。
- 用代码执行工具做计算。
- 用数据库查询工具获取私有数据。

### 2.3 ReAct：思考与行动交替

ReAct 是 Agent 领域最经典的范式，全称是 **Reasoning + Acting**。

它的核心思想是：模型在回答问题时，不是一次性生成答案，而是交替进行"思考"和"行动"。

```
问题：2024 年诺贝尔物理学奖得主是谁？

思考：我需要搜索最新信息。
行动：调用 web_search(query="2024 Nobel Prize in Physics winner")
观察：John J. Hopfield 和 Geoffrey E. Hinton 获奖。

思考：我已经找到答案。
行动：输出最终回答。
```

ReAct 的优势：

- 把推理过程显式化，便于调试。
- 模型可以根据工具结果调整下一步行动。
- 减少幻觉，因为关键信息来自外部工具。

### 2.4 CoT、ToT、ReAct 的区别

| 范式 | 全称 | 核心思想 | 特点 |
|---|---|---|---|
| CoT | Chain of Thought | 让模型一步步推理 | 只推理，不调用工具 |
| ToT | Tree of Thought | 让模型探索多种推理路径 | 像树一样分支、评估、选择 |
| ReAct | Reasoning + Acting | 推理与行动交替 | 能调用外部工具 |

**Nexus 用的是 ReAct 思想的扩展版**：不是让单个模型自己 ReAct，而是把不同职责拆给不同 Agent（Orchestrator、Planner、Executor 等）。

### 2.5 Function Calling 是什么

Function Calling（函数调用）是 LLM 的一种能力：模型可以根据用户输入，判断是否需要调用某个预定义的函数，并生成正确的函数参数。

例子：

```python
工具定义：
{
  "name": "get_weather",
  "description": "查询指定城市的天气",
  "parameters": {
    "type": "object",
    "properties": {
      "city": {"type": "string", "description": "城市名"}
    },
    "required": ["city"]
  }
}

用户输入：北京今天天气怎么样？

模型输出：
{
  "tool_calls": [
    {
      "function": {
        "name": "get_weather",
        "arguments": '{"city": "北京"}'
      }
    }
  ]
}
```

Function Calling 是 Agent 调用工具的**标准接口**。

### 自测问题

1. Agent 和普通 LLM 应用的本质区别是什么？
2. ReAct 为什么能减少幻觉？
3. CoT 和 ReAct 的主要区别是什么？
4. Function Calling 的输出格式是什么样的？
5. 为什么 Function Calling 对 Agent 系统很重要？

### 动手练习

1. 用通义千问的 Function Calling API，定义一个 `calculate` 工具，让模型帮你计算 "(12 + 34) * 56"。
2. 观察模型返回的是文本还是 tool_calls 结构。

---

## 第 3 章：RAG 检索增强生成

### 3.1 为什么需要 RAG

LLM 有两个问题：

1. **知识有限**：训练数据有截止日期，不知道最新信息。
2. **幻觉**：会一本正经地编造不存在的信息。

RAG（Retrieval-Augmented Generation，检索增强生成）的解决思路是：

> 在让模型回答问题之前，先从知识库中检索出相关内容，把检索结果和用户问题一起交给模型。模型基于检索到的真实信息生成回答。

### 3.2 RAG 的标准流程

```
文档加载 → 文本分块 → Embedding 向量化 → 存入向量数据库

用户提问 → 问题向量化 → 相似度检索 → 返回 Top-K 片段 → 模型生成回答
```

### 3.3 Embedding 是什么

Embedding 是把文本转换成**向量**（一串数字）的技术。语义相近的文本，向量距离也近。

例如：

- "猫" 和 " kitten" 的向量距离很近。
- "猫" 和 "汽车" 的向量距离很远。

向量之间的距离通常用**余弦相似度**或**欧氏距离**计算。

### 3.4 向量数据库

向量数据库专门存储向量，并支持快速相似度检索。常见选择：

| 向量数据库 | 特点 | 适用场景 |
|---|---|---|
| Chroma | 轻量、本地可用、Python 友好 | 个人项目、原型开发 |
| FAISS | Facebook 开源、纯索引 | 需要自定义索引时 |
| Milvus | 企业级、分布式 | 大规模生产环境 |
| Pinecone | 云服务、托管 | 不想自己运维时 |

Nexus 用 Chroma，因为它零部署、易集成。

### 3.5 文本分块策略

长文档不能直接 embedding，需要切成小段。常见分块策略：

| 策略 | 说明 | 优点 | 缺点 |
|---|---|---|---|
| 固定长度 | 每 N 个字符或 token 切一块 | 简单 | 可能切断句子 |
| 按段落切 | 以换行或段落为边界 | 语义完整 | 长度不均 |
| 重叠切分 | 相邻块有重叠内容 | 避免上下文丢失 | 存储量增加 |
| 语义切分 | 按语义边界切分 | 效果最好 | 实现复杂 |

Nexus 用的是基于 LangChain 的分块器，可以配置块大小和重叠。

### 3.6 Top-K 检索

Top-K 表示返回最相关的 K 个片段。K 的选择影响回答质量：

- K 太小：可能漏掉关键信息。
- K 太大：引入无关信息，增加上下文长度和成本。

常见取值：3 ~ 10。

### 3.7 RAG 的评估维度

RAG 系统做得好不好，可以从多个维度评估：

| 维度 | 含义 | 评估方式 |
|---|---|---|
| 召回率 | 相关文档有没有被检索到 | 人工标注 + 指标 |
| 精确率 | 检索到的文档是否相关 | 人工标注 + 指标 |
| 回答正确性 | 最终回答是否准确 | LLM-as-a-Judge |
| 幻觉率 | 回答中有多少编造内容 | 与检索文档对比 |

### 自测问题

1. RAG 解决 LLM 的哪两个问题？
2. Embedding 和 one-hot 编码有什么区别？
3. 为什么文本要分块？常见分块策略有哪些？
4. Top-K 太大或太小分别有什么问题？
5. 你怎么判断一个 RAG 系统做得好还是不好？

### 动手练习

1. 用 LangChain + Chroma，把 `docs/python_guide.txt` 加载进去，然后问一个 Python 相关问题，观察检索结果。
2. 尝试不同的 chunk_size 和 chunk_overlap，看检索结果有什么变化。

---

## 第 4 章：工具调用与 Function Calling 深入

### 4.1 工具的三要素

一个可被 Agent 调用的工具需要三个信息：

1. **name**：工具名，唯一标识。
2. **description**：工具功能描述，帮助模型判断什么时候调用。
3. **parameters**：参数 schema，告诉模型每个参数的类型和含义。

```json
{
  "name": "execute_python",
  "description": "安全执行 Python 代码表达式，支持数学运算",
  "parameters": {
    "type": "object",
    "properties": {
      "expression": {
        "type": "string",
        "description": "要执行的 Python 表达式"
      }
    },
    "required": ["expression"]
  }
}
```

### 4.2 工具调用循环

Agent 的工具调用通常是一个循环：

```
1. 用户输入问题。
2. 模型判断是否调用工具。
   - 不调用：直接生成回答，结束。
   - 调用：生成 tool_calls。
3. 系统执行工具，得到结果。
4. 把工具结果加入对话历史。
5. 模型再次判断，循环直到不需要调用工具。
6. 生成最终回答。
```

### 4.3 工具安全

工具安全是 Agent 系统的重中之重。尤其是代码执行类工具：

**危险示例**：

```python
# 如果用 eval 执行用户输入
eval("__import__('os').system('rm -rf /')")
```

**安全做法**：

- 用 AST（抽象语法树）做白名单解析。
- 只允许常数和基本运算。
- 禁止 `import`、`open`、网络请求等危险操作。
- 文件操作限制在指定工作目录内。

### 4.4 工具返回格式

工具返回建议统一格式：

```json
{
  "result": "执行结果或错误信息",
  "tool": "工具名",
  "args": {"参数": "值"}
}
```

统一格式的好处：

- Orchestrator 和 Summarizer 不需要关心具体工具。
- 便于日志记录和调试。
- 便于在 Web UI 上展示工具调用过程。

### 自测问题

1. 工具定义为什么需要 description？
2. Agent 调用工具的循环包含哪几步？
3. 为什么 execute_python 不能用 eval？
4. AST 白名单是怎么保证安全的？
5. 统一工具返回格式有什么好处？

### 动手练习

1. 实现一个 `get_current_time` 工具，返回当前时间。
2. 实现一个安全的 `execute_python` 工具，只允许加减乘除和常量。

---

# 第二部分：Nexus 架构逐层理解

## 第 5 章：Nexus 项目总览

### 5.1 项目定位

Nexus 是一个**面向个人使用、可扩展至团队的 Multi-Agent AI 工作流助手**。

它的双重目标：

1. **作为简历项目**：展示 AI Agent 系统设计、RAG、Function Calling、工具编排、质量评估综合能力。
2. **作为日常工具**：开发者本人每天愿意使用，管理知识、辅助编程、操作文件。

### 5.2 从原 ai-demos 到 Nexus

原 ai-demos 有两个独立 demo：

1. RAG 文档问答系统
2. Function Calling 天气/计算 Agent

问题：

- 两个 demo 技术栈重复，像同一个模板套出来的。
- 都是 toy 项目，没有真实价值。
- 缺少评估闭环。

Nexus 的升级思路：

> 把 RAG 和 Function Calling 合并成一个完整的 Agent 系统，用真实工具替换 mock，增加质量评估模块，形成"生成-评估-优化"闭环。

### 5.3 五阶段演进路线

| 阶段 | 目标 | 可展示成果 |
|---|---|---|
| Phase 1 | Multi-Agent 内核 + 消息总线 | 命令行可运行的 Multi-Agent demo |
| Phase 2 | 真实 RAG + Tool Registry | Agent 能检索知识库、调用本地工具 |
| Phase 3 | Web UI + SSE | 浏览器中可用的 Web 版 Agent |
| Phase 4 | SQLite 记忆持久化 | 有长期记忆、有评估数据 |
| Phase 5 | 团队版扩展 | 多用户、共享知识库、外部消息中间件 |

### 5.4 核心组件图

```
用户 (浏览器)
    │
    ▼
Web Gateway (FastAPI + SSE)
    │
    ▼
Orchestrator Agent
    │
    ▼
Message Bus
    │
    ├─→ Planner Agent
    ├─→ Retriever Agent → Knowledge Base (Chroma)
    ├─→ Executor Agent → Tool Registry
    ├─→ Summarizer Agent
    └─→ Critic Agent
    │
    ▼
Memory Store (SQLite)
```

### 自测问题

1. Nexus 的双重目标是什么？
2. 原 ai-demos 的两个 demo 有什么问题？
3. Nexus 五阶段演进路线中，Phase 2 和 Phase 3 分别做什么？
4. 画出 Nexus 的核心组件图。

---

## 第 6 章：Phase 1 — Multi-Agent 内核

### 6.1 Phase 1 的目标

Phase 1 不是做功能最全的系统，而是搭建一个**可运行的 Multi-Agent 骨架**。关键验证点：

- Agent 之间能通过消息总线协作。
- Orchestrator 能调度多个 Agent 完成完整流程。
- LLM 调用有统一抽象。
- 每个模块都有测试保护。

### 6.2 Message Bus：Agent 的神经系统

Message Bus 是 Nexus 最核心的基础设施。它让每个 Agent 只需要关心"收到消息后怎么处理"，不需要知道其他 Agent 在哪里、怎么实现。

核心能力：

- **subscribe(agent_id)**：给 Agent 注册一个队列。
- **publish(message)**：把消息放入接收方队列。
- **send_and_wait(recipient, message, timeout)**：发消息后等待回复，带超时。

### 6.3 BaseAgent：公共骨架

所有 Agent 都继承 `BaseAgent`，获得：

- 唯一的 agent_id
- 消息队列订阅
- 消息处理循环
- 发送消息和调用 LLM 的便利方法

### 6.4 六个专业 Agent

| Agent | 职责 | 在流程中的位置 |
|---|---|---|
| Orchestrator | 总指挥 | 接收输入、调度、聚合 |
| Planner | 任务规划 | 把复杂任务拆成步骤 |
| Retriever | 检索 | 从知识库找资料 |
| Executor | 执行 | 调用工具 |
| Summarizer | 总结 | 生成最终回答 |
| Critic | 评估 | 给回答打分 |

### 6.5 SessionState：任务状态机

每次用户请求都有一个 `SessionState` 对象，跟踪：

- query：用户问题
- plan：执行计划
- documents：检索结果
- tool_results：工具执行结果
- answer：最终回答
- critique：评估结果
- status：任务状态

状态流转：

```
pending → planning → executing → summarizing → critiquing → done
```

### 6.6 为什么 Retriever 和 Executor 先 mock

Phase 1 的关键是验证**协作架构**，不是真实 RAG 和工具。mock 的好处：

- 降低复杂度，快速验证核心机制。
- 保证接口一致，Phase 2 替换实现时其他模块不用大改。
- 测试稳定，不依赖外部 API 和数据库。

### 自测问题

1. Phase 1 的核心目标是什么？
2. Message Bus 的三个核心方法是什么？
3. BaseAgent 给子类提供了哪些能力？
4. SessionState 跟踪哪些字段？
5. 为什么 Phase 1 的 Retriever 和 Executor 用 mock？

### 动手练习

1. 不看项目代码，自己实现一个简化版 MessageBus，支持 publish 和 send_and_wait。
2. 给 BaseAgent 加一个日志方法，每次收到消息时打印内容。

---

## 第 7 章：Phase 2 — 真实 RAG + Tool Registry

### 7.1 Phase 2 的目标

Phase 2 要把 Phase 1 的 mock 替换成真实实现：

- Retriever 接入 Chroma 向量数据库。
- Executor 接入 Tool Registry。
- 实现真实工具：search_docs、execute_python、read_file、list_files。
- 支持多集合知识库。

### 7.2 RAG 模块拆分

Nexus 的 RAG 模块拆成四个子模块：

| 模块 | 文件 | 职责 |
|---|---|---|
| Loader | `rag/loader.py` | 加载各种格式文档 |
| Splitter | `rag/splitter.py` | 文本分块 |
| VectorStore | `rag/vectorstore.py` | 管理 Chroma 集合 |
| Retriever | `rag/retriever.py` | 执行相似度检索 |

### 7.3 Loader：文档加载

Loader 负责把不同来源的文档读成文本：

- `.txt` 文件
- `.md` 文件
- `.pdf` 文件
- `.docx` 文件
- 网页 URL

LangChain 提供了丰富的加载器，Nexus 可以按需扩展。

### 7.4 Splitter：文本分块

分块策略影响检索质量。Nexus 使用 `RecursiveCharacterTextSplitter`：

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # 每个块约 500 字符
    chunk_overlap=50,    # 相邻块重叠 50 字符
)
```

### 7.5 VectorStore：Chroma 多集合管理

Chroma 支持多个 collection。Nexus 按来源划分集合：

| 集合名 | 用途 |
|---|---|
| notes | 个人笔记 |
| code_docs | 代码项目文档 |
| web_articles | 收藏的网页文章 |
| manual | 手动输入 |

多集合的好处：

- 可以按来源过滤检索范围。
- 可以针对不同集合使用不同策略。
- 方便追踪来源。

### 7.6 Retriever Agent 的 Phase 2 版本

Phase 2 的 Retriever 不再返回 mock 数据，而是：

1. 接收 query。
2. 用 Embedding 模型把 query 向量化。
3. 查询 Chroma 的指定集合或多个集合。
4. 返回 Top-K 文档片段 + source + score。

### 7.7 Tool Registry：工具注册中心

Tool Registry 是所有工具的统一管理中心。每个工具注册时提供：

- name
- description
- parameters（JSON Schema）
- handler（执行函数）

```python
class Tool:
    name: str
    description: str
    parameters: dict
    handler: Callable
    source: str  # local / mcp / note_api
```

### 7.8 Executor Agent 的 Phase 2 版本

Phase 2 的 Executor：

1. 从消息中解析 tool 和 args。
2. 去 Tool Registry 查找对应工具。
3. 校验参数是否符合 JSON Schema。
4. 调用 handler 执行。
5. 返回统一格式的结果。

### 7.9 安全执行 Python

`execute_python` 是风险最高的工具。Nexus 的做法：

1. 用 AST 解析表达式。
2. 白名单只允许 `ast.Constant` 和基本运算符。
3. 禁止 `import`、`open`、函数调用等。
4. 所有文件操作通过单独的 `read_file` / `list_files` 工具控制路径白名单。

### 自测问题

1. Phase 2 要把哪些 mock 替换成真实实现？
2. RAG 模块拆成哪四个子模块？各做什么？
3. 为什么 Chroma 要分多个 collection？
4. Tool Registry 需要管理工具的哪些信息？
5. execute_python 怎么做安全控制？

### 动手练习

1. 用 LangChain 把 `docs/python_guide.txt` 加载、分块、存入 Chroma。
2. 实现一个 ToolRegistry 类，支持 register 和 call 两个方法。
3. 实现一个安全的 execute_python，只允许加减乘除。

---

## 第 8 章：Phase 3 — Web UI + SSE

### 8.1 Phase 3 的目标

Phase 3 让 Nexus 从命令行变成可以在浏览器里使用的 Web 应用。核心能力：

- FastAPI 提供 HTTP + SSE 接口。
- 前端页面实时展示 Agent 思考过程、工具调用、最终回答。
- 支持会话管理。

### 8.2 为什么用 SSE 而不是 WebSocket

SSE（Server-Sent Events）是一种服务器向客户端单向推送数据的技术。

| 特性 | SSE | WebSocket |
|---|---|---|
| 方向 | 服务器 → 客户端 | 双向 |
| 协议 | 基于 HTTP | 独立协议 |
| 复杂度 | 低 | 高 |
| 自动重连 | 浏览器原生支持 | 需自己实现 |
| 适用场景 | 服务器推送流式数据 | 实时双向通信 |

Nexus 主要是服务器向客户端推送 Agent 的中间过程和最终结果，SSE 足够用且更简单。

### 8.3 后端 SSE 接口

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/chat")
async def chat(request: ChatRequest):
    async def event_stream():
        async for event in orchestrator.process_stream(request.query):
            yield f"event: {event.type}\ndata: {json.dumps(event.data)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

### 8.4 SSE 事件类型

Nexus 定义的事件类型：

| 事件 | 含义 |
|---|---|
| agent_thought | Agent 思考过程 |
| tool_call | 工具调用请求 |
| tool_result | 工具执行结果 |
| final_answer | 最终回答 |
| error | 错误信息 |

### 8.5 前端页面设计

建议布局：

- 左侧：会话列表 + 知识库管理
- 中间：对话区域（展示 Agent 思考、工具调用、最终回答）
- 右侧：工具状态 / 来源引用

### 8.6 流式 Orchestrator

为了支持 SSE，Orchestrator 需要改造为异步生成器：

```python
async def process_stream(self, query):
    yield {"type": "agent_thought", "data": {"agent": "orchestrator", "content": "开始规划任务"}}
    # ... 调度各 Agent
    yield {"type": "final_answer", "data": {"content": answer, "sources": sources}}
```

### 自测问题

1. SSE 和 WebSocket 的主要区别是什么？
2. 为什么 Nexus 选 SSE 而不是 WebSocket？
3. SSE 的消息格式是什么样的？
4. 前端如何接收 SSE 事件？
5. 为了让 Orchestrator 支持 SSE，需要做什么改造？

### 动手练习

1. 用 FastAPI 写一个最简单的 SSE 接口，每隔 1 秒发送一个数字。
2. 写一个 HTML 页面，用 EventSource 接收 SSE 数据并显示。

---

## 第 9 章：Phase 4 — 记忆持久化

### 9.1 Phase 4 的目标

Phase 4 给 Nexus 增加长期记忆能力：

- 持久化对话历史。
- 持久化 Agent 思考链和工具调用记录。
- 保存用户反馈和偏好。
- 支持跨会话上下文。

### 9.2 为什么用 SQLite

| 数据库 | 优点 | 缺点 |
|---|---|---|
| SQLite | 零部署、轻量、Python 内置支持 | 不适合高并发 |
| PostgreSQL | 功能强、适合团队 | 需要安装和运维 |
| MySQL | 成熟稳定 | 需要安装和运维 |

Phase 4 面向个人使用，SQLite 零部署、足够用。

### 9.3 数据表设计

| 表名 | 用途 | 关键字段 |
|---|---|---|
| sessions | 会话管理 | id, title, created_at, updated_at |
| messages | 消息历史 | id, session_id, role, content, created_at |
| agent_traces | Agent 思考链 | id, message_id, agent, thought, tool_calls, result |
| feedback | 用户反馈 | id, message_id, rating, comment |
| preferences | 用户偏好 | key, value |

### 9.4 记忆怎么用

1. **对话开始时**：加载历史消息作为上下文。
2. **Orchestrator 决策时**：参考用户偏好（如常用工具、输出风格）。
3. **Critic 评估时**：参考历史反馈优化评分策略。
4. **调试时**：查看 agent_traces 了解完整执行路径。

### 9.5 上下文窗口管理

对话历史太长时，不能全部塞进 LLM 上下文。常用策略：

- 只保留最近 N 轮。
- 对早期对话做摘要。
- 按 token 数截断。

### 自测问题

1. Phase 4 要持久化哪些数据？
2. 为什么个人版用 SQLite？
3. agent_traces 表有什么用？
4. 对话历史太长时怎么办？
5. 用户反馈怎么用于系统优化？

### 动手练习

1. 用 SQLite 设计并实现 sessions 和 messages 表。
2. 实现一个函数，加载某个会话最近 10 条消息。

---

# 第三部分：工程化、评估与求职

## 第 10 章：测试与质量评估

### 10.1 为什么测试对 Agent 系统很重要

Agent 系统依赖 LLM，LLM 输出不稳定。测试可以：

- 确保非 LLM 部分（消息总线、工具执行、状态机）稳定。
- 用 mock 隔离 LLM，降低测试成本和不确定性。
- 作为回归保护，改代码时不怕破坏旧功能。

### 10.2 测试金字塔

| 测试类型 | 关注点 | Nexus 示例 |
|---|---|---|
| 单元测试 | 单个函数/类 | `test_message_bus.py` |
| 集成测试 | 多个模块协作 | `test_orchestrator.py` |
| 端到端测试 | 完整用户流程 | CLI 输入 → 最终输出 |
| 评估测试 | 回答质量 | test_cases.json 跑分 |

### 10.3 pytest-asyncio

Agent 都是异步的，测试时需要：

```python
import pytest

@pytest.mark.asyncio
async def test_message_bus():
    bus = MessageBus()
    ...
```

### 10.4 mock LLM 的技巧

测试 Planner 等依赖 LLM 的 Agent 时，用 monkeypatch 替换 `think` 方法：

```python
async def mock_think(system_prompt, user_prompt, tools=None):
    return {
        "content": '{"steps": [...]}',
        "tool_calls": None,
    }

planner.think = mock_think
```

### 10.5 LLM-as-a-Judge

用更强的模型给回答打分。示例 prompt：

```
请评估下面这个回答的质量，从正确性、相关性、完整性、安全性四个维度打分（0-1）。

问题：{query}
回答：{answer}

请输出 JSON 格式：
{
  "correctness": 0.9,
  "relevance": 0.8,
  "completeness": 0.7,
  "safety": 1.0,
  "overall": 0.85,
  "feedback": "..."
}
```

### 10.6 传统评估指标

| 指标 | 用途 | 局限性 |
|---|---|---|
| BLEU | 机器翻译 | 不适合开放式问答 |
| ROUGE | 文本摘要 | 只匹配 n-gram |
| BERTScore | 语义相似度 | 计算成本较高 |

Agent 系统更多用 LLM-as-a-Judge 和规则评估结合。

### 自测问题

1. Agent 系统为什么特别需要测试？
2. 测试金字塔有哪几层？
3. 怎么 mock LLM 调用？
4. LLM-as-a-Judge 是什么？优缺点？
5. BLEU 适合评估 Agent 回答吗？为什么？

### 动手练习

1. 为 `MessageBus` 补充一个超时测试。
2. 写三个测试用例，用 LLM-as-a-Judge 评估 Agent 回答质量。

---

## 第 11 章：工程化实践

### 11.1 环境变量管理

敏感信息（API Key）和可配置项（模型名）不要硬编码，放到 `.env`：

```bash
LLM_PROVIDER=qwen
LLM_MODEL=qwen-turbo
DASHSCOPE_API_KEY=your-key
```

代码中用 `python-dotenv` 加载：

```python
from dotenv import load_dotenv
load_dotenv()
```

### 11.2 日志

日志级别：DEBUG、INFO、WARNING、ERROR。

Agent 系统要记录：

- Agent 行为
- 消息流转
- 工具调用
- LLM 请求/响应

建议用 `logging` 模块，配置结构化输出。

### 11.3 错误处理

| 错误类型 | 处理方式 |
|---|---|
| LLM API 异常 | 重试 3 次，失败后返回错误 |
| 工具执行失败 | 返回错误信息，Orchestrator 决定是否重试 |
| 检索无结果 | 提示用户补充文档 |
| 超时 | Orchestrator 终止任务 |
| 死循环 | max_turns 限制 |

### 11.4 版本控制

- 用 git 管理代码。
- 每个功能一个分支或 worktree。
- 每个任务结束 commit。
- 写好 commit message。

### 11.5 依赖管理

用 `requirements.txt` 或 `pyproject.toml`：

```txt
fastapi==0.111.0
uvicorn==0.30.0
langchain==0.2.0
chromadb==0.5.0
pytest==8.2.0
pytest-asyncio==0.23.0
```

### 自测问题

1. API Key 应该怎么管理？
2. Agent 系统需要记录哪些日志？
3. LLM API 异常应该怎么处理？
4. 怎么防止 Agent 死循环？
5. requirements.txt 和 pyproject.toml 有什么区别？

### 动手练习

1. 给 Nexus 添加统一的日志配置。
2. 实现一个重试装饰器，给 LLM 调用加上 3 次重试。

---

## 第 12 章：简历包装与面试准备

### 12.1 项目描述 STAR 法则

STAR = Situation（背景）+ Task（任务）+ Action（行动）+ Result（结果）。

示例：

> **背景**：在学习 AI Agent 过程中，发现很多 demo 只停留在调用 API，缺乏真实应用场景和评估闭环。
> **任务**：设计并实现一个面向 MOD 开发知识库的智能文档任务 Agent。
> **行动**：整合 RAG 检索与 Function Calling，实现真实工具（代码执行、文件读取），设计回答质量评估模块，编写 pytest 测试。
> **结果**：Agent 能准确回答 Python/MOD 相关问题，支持多工具协同和自动评估，项目已开源到 GitHub。

### 12.2 简历关键词

AI Agent 岗位关键词：

- Agent、Multi-Agent、ReAct、Function Calling
- RAG、Embedding、Chroma、LangChain
- Tool Registry、Tool Orchestration
- LLM-as-a-Judge、Prompt Engineering
- FastAPI、SSE、pytest、asyncio

### 12.3 口述版项目介绍

准备 3 分钟版本，结构：

1. 一句话讲清楚项目是什么（15 秒）。
2. 为什么做这个项目（30 秒）。
3. 技术架构和核心设计（90 秒）。
4. 遇到的挑战和解决方案（45 秒）。
5. 成果和收获（30 秒）。

### 12.4 高频面试题

1. 什么是 Agent？和普通 LLM 应用有什么区别？
2. ReAct、CoT、ToT 有什么区别？
3. RAG 解决了什么问题？文本怎么分块？
4. Function Calling 的原理是什么？
5. 你怎么评估 Agent 的回答质量？
6. 如果模型没有按预期调用工具，你怎么处理？
7. Multi-Agent 相比单 Agent 有什么优势和劣势？
8. 怎么保证 Agent 工具调用的安全性？

### 自测问题

1. 用 STAR 法则描述你的 Agent 项目。
2. 列出 5 个 AI Agent 岗位关键词。
3. 准备 3 分钟口述版项目介绍。

### 动手练习

1. 写一份 300 字的项目简介。
2. 对着镜子练习 3 分钟项目介绍。

---

# 第四部分：分层练习与进阶路线

## 第 13 章：分层练习

### 13.1 基础练习（第 1 ~ 2 周）

1. 用 LLM API 实现一个问答机器人。
2. 用 LangChain 实现一个简单的 RAG 系统。
3. 实现一个 Function Calling demo，调用天气查询工具。
4. 写一个 asyncio 程序，同时启动多个协程。

### 13.2 进阶练习（第 3 ~ 4 周）

1. 不看项目代码，独立实现 MessageBus。
2. 实现 BaseAgent 和 Orchestrator 的简单版本。
3. 用 Chroma 构建多集合知识库。
4. 实现一个 ToolRegistry，支持注册和安全调用工具。

### 13.3 综合练习（第 5 ~ 6 周）

1. 把 Nexus Phase 2 完整跑通。
2. 给 Nexus 添加一个自定义工具。
3. 实现 Web UI + SSE 的前后端。
4. 设计并运行一套评估测试用例。

### 13.4 高阶挑战（第 7 ~ 8 周）

1. 实现 MCP Client，接入外部 MCP Server。
2. 给 Nexus 添加长期记忆和跨会话上下文。
3. 实现 Agent 的自我纠错循环：Critic 评分低时自动重试。
4. 把 Nexus 部署到云服务器。

---

## 第 14 章：系统学习路径总结

### 14.1 八周学习计划

| 周次 | 学习内容 | 产出 |
|---|---|---|
| 第 1 周 | LLM 基础、Agent 概念 | 完成第 1、2 章阅读和练习 |
| 第 2 周 | RAG、Function Calling | 完成第 3、4 章阅读和练习 |
| 第 3 周 | Nexus 架构总览、Phase 1 | 理解 Message Bus、BaseAgent、六个 Agent |
| 第 4 周 | Phase 2 | 实现真实 RAG + Tool Registry |
| 第 5 周 | Phase 3 | 实现 Web UI + SSE |
| 第 6 周 | Phase 4 | 实现 SQLite 记忆持久化 |
| 第 7 周 | 测试、评估、工程化 | 补充测试、评估模块、日志 |
| 第 8 周 | 简历包装、面试准备 | 项目口述、高频题准备 |

### 14.2 关键能力进阶

```
AI 工具使用者
    ↓
能调 API、写 prompt
    ↓
AI 应用开发者
    ↓
能做 RAG、Function Calling、单 Agent
    ↓
AI 系统设计者
    ↓
能设计 Multi-Agent 架构、评估闭环、工程化落地
```

你的目标是从第三层进入第四层。

### 14.3 持续提升建议

1. **多动手**：每看完一章，至少做一个练习。
2. **多写文档**：把自己的理解写成笔记或博客。
3. **多面试模拟**：找人模拟面试，暴露问题。
4. **关注前沿**：阅读 LangChain、LlamaIndex、AutoGen 等框架更新。
5. **参与开源**：给 Nexus 添加功能，推到 GitHub，积累可见作品。

---

# 附录

## 附录 A：术语表

| 术语 | 解释 |
|---|---|
| LLM | 大语言模型 |
| Token | 模型处理文本的最小单元 |
| Context Window | 上下文窗口，模型一次能处理的 token 数 |
| Agent | 能感知环境、决策、行动的智能体 |
| RAG | 检索增强生成 |
| Embedding | 把文本转换为向量的技术 |
| Vector DB | 向量数据库，存储向量并支持相似度检索 |
| Function Calling | 模型调用外部函数的能力 |
| ReAct | Reasoning + Acting，推理与行动交替 |
| CoT | Chain of Thought，思维链 |
| ToT | Tree of Thought，思维树 |
| SSE | Server-Sent Events，服务器推送事件 |
| MCP | Model Context Protocol，模型上下文协议 |
| TDD | 测试驱动开发 |
| LLM-as-a-Judge | 用 LLM 评估输出质量 |
| AST | 抽象语法树 |
| JSON Schema | 描述 JSON 数据结构的规范 |

## 附录 B：推荐学习资源

1. **书籍**：《Building LLM Apps》、《LangChain 实战》
2. **论文**：ReAct、RAG Survey、LLM-as-a-Judge Survey
3. **框架文档**：LangChain、Chroma、FastAPI、pytest-asyncio
4. **开源项目**：AutoGen、MetaGPT、CrewAI
5. **在线课程**：DeepLearning.AI 的 LangChain 课程

## 附录 C：Nexus 核心文件速查

| 文件 | 作用 |
|---|---|
| `core/llm.py` | 统一 LLM Client |
| `core/message_bus.py` | 消息总线 |
| `core/agents/base.py` | Agent 基类 |
| `core/agents/orchestrator.py` | 总指挥 |
| `core/agents/planner.py` | 任务规划 |
| `core/agents/retriever.py` | 检索 |
| `core/agents/executor.py` | 执行工具 |
| `core/agents/summarizer.py` | 总结 |
| `core/agents/critic.py` | 评估 |
| `rag/loader.py` | 文档加载 |
| `rag/vectorstore.py` | Chroma 向量库 |
| `eval/evaluator.py` | 评估模块 |
| `app.py` | FastAPI Web 服务 |
| `main.py` | 命令行入口 |

---

## 写在最后

这份路线图不是为了让你记住所有知识点，而是帮你建立一套**系统的认知框架**。真正掌握这些技能，需要你：

1. 理解概念为什么存在。
2. 动手实现关键模块。
3. 在项目中反复应用。
4. 在面试中清晰表达。

Nexus 是一个很好的练手项目。把它从 Phase 1 推到 Phase 4，你会对 AI Agent 系统有深刻理解。更重要的是，你会从一个"调 API 的人"变成一个"设计系统的人"。

祝你学习顺利，秋招成功。
