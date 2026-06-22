# Nexus 引导式系统课程：从 LLM 原理到 Multi-Agent 工程落地

> 适用对象：胡智明（23 级软件工程本科）
> 对应项目：C:\Users\hzs17\Desktop\ai-demos（Nexus）
> 文档日期：2026-06-21
> 课程形态：引导式学习（目标 → 讲解 → 实验 → 自测 → 练习 → 检查）
> 前置要求：Python 3.10+ 语法、HTTP/REST 基础、熟悉类与异步概念

---

## 课程导读

### 如何使用本课程

本课程采用**引导式结构**，每一节都按统一模板组织：

1. **本节目标**：学完这节后你能做什么。
2. **前置检查**：学习本节之前必须掌握的内容。
3. **关键概念**：本节涉及的核心术语清单。
4. **深入讲解**：原理、设计动机、边界条件。
5. **代码实验室**：可直接运行的最小示例。
6. **自测题**：带答案和解析。
7. **动手练习**：带详细步骤和参考答案。
8. **常见错误**：真实踩坑记录。
9. **进阶阅读**：论文、文档、源码。
10. **本节检查清单**：确认掌握的标志。

**学习原则**：

- 不要只读代码，要动手改代码。
- 每完成一节，必须完成本节检查清单。
- 遇到不懂的术语，先查附录术语表，再提问。

---

# 模块一：LLM 与 Agent 基础

## 第 1 课：大语言模型的能力边界与工程约束

### 本节目标

学完本节后，你能够：

- 解释 LLM 的 next-token prediction 机制及其对工程应用的影响。
- 计算一次 API 调用的 token 消耗和成本。
- 根据场景选择合适的 Temperature 和 max_tokens。
- 设计一个避免上下文溢出的提示词结构。

### 前置检查

在继续之前，请确认你已掌握：

- Python 基本数据类型和函数。
- 什么是 API 调用（request/response）。
- 能够理解 JSON 格式。

### 关键概念

- **自回归生成（Autoregressive Generation）**
- **Tokenization**
- **上下文窗口（Context Window）**
- **Temperature / Top-p / Top-k**
- **提示词注入（Prompt Injection）**

### 深入讲解

#### 1.1 自回归生成的本质

LLM 不是"理解"问题后给出答案。它的数学本质是：

```
P(token_n | token_1, token_2, ..., token_{n-1})
```

即：给定已生成的所有 token，预测下一个 token 的概率分布，然后采样输出。

**工程影响**：

1. **没有真正的推理记忆**：模型不会"记住"上下文之外的信息。长对话需要显式维护历史消息。
2. **输出具有随机性**：相同输入可能产生不同输出，关键任务需要低 Temperature 或多次采样投票。
3. **知识边界严格**：模型只能基于训练数据中的模式生成，无法访问私有数据或实时信息。

#### 1.2 Token 的经济学

Token 是计费单位，也是性能单位。以通义千问 qwen-turbo 为例（价格会变动，以官方为准）：

| 项目 | 说明 |
|---|---|
| 输入 token | 用户提示 + 系统提示 + 历史消息 + 工具定义 |
| 输出 token | 模型生成的内容 |
| 计费 | 通常按每 1K token 计费 |

**成本优化策略**：

- 精简系统提示，避免冗余说明。
- 对历史消息做摘要或截断。
- RAG 只传入相关片段，而非完整文档。
- 使用更便宜的模型处理简单任务（如分类），贵的模型处理生成任务。

#### 1.3 采样参数的工程选择

**Temperature**：

- 数学上是对 softmax 输出分布的温度缩放：$P_i \propto e^{z_i / T}$。
- $T \to 0$：分布趋于尖锐，输出确定。
- $T \to \infty$：分布趋于均匀，输出随机。

**Top-p（Nucleus Sampling）**：

- 只从累积概率达到 p 的最小 token 集合中采样。
- 例如 top_p=0.9 表示只考虑概率总和 90% 的那些 token。

**Top-k**：

- 只从概率最高的 k 个 token 中采样。

**工程建议**：

| 场景 | Temperature | Top-p | 说明 |
|---|---|---|---|
| 工具调用参数生成 | 0.0 ~ 0.1 | 0.1 | 要求稳定、可解析 |
| JSON 结构化输出 | 0.0 ~ 0.2 | 0.1 | 减少格式错误 |
| 代码生成 | 0.2 ~ 0.4 | 0.5 | 兼顾确定性和多样性 |
| 创意写作 | 0.7 ~ 1.0 | 0.9 | 允许发散 |

#### 1.4 上下文窗口与长上下文技术

上下文窗口限制是 RAG 和 Agent 系统存在的根本原因之一。常见应对策略：

1. **截断（Truncation）**：丢弃最早的消息。简单但可能丢失关键信息。
2. **摘要（Summarization）**：把早期对话压缩成摘要。会损失细节。
3. **RAG 检索**：只在需要时检索相关信息，而非全部塞进上下文。
4. **长上下文模型**：如 GPT-4 128K、Kimi 200K。但长上下文会增加成本和延迟，且存在"中间丢失"（lost in the middle）问题。

### 代码实验室

#### 实验 1.1：观察 Temperature 对输出的影响

```python
import os
import dashscope

 dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

messages = [
    {"role": "system", "content": "你是一个创意写作助手。"},
    {"role": "user", "content": "用一句话描述未来的城市。"},
]

for temp in [0.0, 0.5, 1.0]:
    response = dashscope.Generation.call(
        model="qwen-turbo",
        messages=messages,
        temperature=temp,
        result_format="message",
    )
    content = response.output.choices[0].message["content"]
    print(f"Temperature={temp}: {content}\n")
```

**预期观察**：Temperature 越低，输出越稳定；越高，输出差异越大。

#### 实验 1.2：Token 计数

```python
# 估算 token 数：中文约 1 字 ~ 1.5 token，英文约 1 word ~ 1.3 token

def estimate_tokens(text):
    # 粗糙估算，实际应使用 tokenizer
    cn_chars = sum(1 for c in text if '一' <= c <= '鿿')
    en_words = len(text.split())
    return int(cn_chars * 1.5 + en_words * 1.3)

text = "请解释 Python 中列表和元组的区别，并给出代码示例。"
print(f"估算 token 数: {estimate_tokens(text)}")
```

### 自测题

**Q1：LLM 的"理解"和普通程序的"理解"有什么区别？**

A1：LLM 没有显式知识表示或符号推理能力。它的"理解"是训练数据中的统计模式在参数中的压缩体现。普通程序基于明确规则执行，而 LLM 基于概率预测生成文本。

**Q2：为什么 RAG 比直接给模型塞完整长文档更经济？**

A2：长文档会占用大量输入 token，直接增加 API 成本。RAG 通过检索只把最相关的片段传给模型，减少输入 token，同时降低无关信息对模型生成的干扰。

**Q3：Temperature=0 时模型输出是否一定相同？**

A3：理论上是的，因为采样会退化为 argmax。但实际中，某些实现或模型版本可能对并列最高概率 token 有随机打破机制，因此极少数情况下仍有差异。工程上可认为基本确定。

**Q4：Top-p 和 Top-k 能否同时使用？**

A4：可以。通常先应用 Top-k 限制候选集大小，再应用 Top-p 限制累积概率。但实际 API 中多数只开放其中一个或组合参数，需查阅具体厂商文档。

### 动手练习

#### 练习 1.1：上下文成本计算器

**目标**：写一个函数，估算给定提示和模型的 API 成本。

**步骤**：

1. 输入：系统提示、用户提示、模型单价（元/1K tokens）。
2. 用简单规则估算输入 token 数。
3. 给定预期输出 token 数，计算总成本。
4. 比较不同长度提示的成本差异。

**参考答案**：

```python
def estimate_cost(system_prompt, user_prompt, input_price, output_price, expected_output_tokens=500):
    input_text = system_prompt + user_prompt
    cn_chars = sum(1 for c in input_text if '一' <= c <= '鿿')
    en_words = len(input_text.split())
    input_tokens = int(cn_chars * 1.5 + en_words * 1.3)

    input_cost = (input_tokens / 1000) * input_price
    output_cost = (expected_output_tokens / 1000) * output_price
    return {
        "input_tokens": input_tokens,
        "output_tokens": expected_output_tokens,
        "input_cost": round(input_cost, 6),
        "output_cost": round(output_cost, 6),
        "total_cost": round(input_cost + output_cost, 6),
    }

system = "你是一位专业的 Python 讲师。"
user = "请解释 Python 中列表和元组的区别，并给出代码示例。"
print(estimate_cost(system, user, input_price=0.002, output_price=0.006, expected_output_tokens=300))
```

#### 练习 1.2：温度参数对比实验

**目标**：设计一个实验，定量观察 Temperature 对 JSON 输出稳定性的影响。

**步骤**：

1. 让模型反复输出固定格式的 JSON（如 {"city": "...", "weather": "..."}）。
2. 分别用 Temperature 0.0、0.3、0.7 各运行 20 次。
3. 统计每次输出是否合法 JSON、字段是否完整。
4. 得出结论。

**参考答案核心逻辑**：

```python
import json

def is_valid_json(text):
    try:
        json.loads(text)
        return True
    except json.JSONDecodeError:
        return False

# 运行 20 次，统计合法率
valid_count = 0
for _ in range(20):
    response = call_llm(temperature=0.0)
    if is_valid_json(response):
        valid_count += 1
print(f"合法率: {valid_count / 20 * 100}%")
```

### 常见错误

1. **认为 LLM 有真正的记忆**：模型只在当前对话上下文内"记得"内容。跨会话需要显式持久化。
2. **Temperature 设太低导致输出重复**：创意任务中 Temperature=0 可能让模型反复输出常见套话。
3. **忽略输入 token 成本**：系统提示和工具定义会占用大量输入 token，设计时需精简。
4. **上下文窗口填满后报错**：未做截断或摘要处理，导致请求超过模型限制。

### 进阶阅读

1. 《Attention Is All You Need》—— Transformer 架构原始论文。
2. OpenAI 官方文档：Tokenization、Pricing、Best Practices。
3. 论文：《Lost in the Middle: How Language Models Use Long Contexts》。

### 本节检查清单

- [ ] 能解释 next-token prediction 机制。
- [ ] 能估算一次 API 调用的 token 成本。
- [ ] 能根据场景选择 Temperature 和 Top-p。
- [ ] 知道至少两种应对长上下文的方法。

---

## 第 2 课：Agent 架构原理与 ReAct 范式

### 本节目标

学完本节后，你能够：

- 区分 LLM 应用、单 Agent 系统、Multi-Agent 系统的架构差异。
- 用 ReAct 范式设计一个能调用工具的 Agent。
- 解释 Function Calling 的内部流程。
- 评估一个场景是否适合用 Agent 解决。

### 前置检查

- 已理解 LLM 的概率生成机制。
- 已能调用至少一家 LLM API。

### 关键概念

- **Agent Loop**
- **Observation / Thought / Action**
- **Tool Schema（JSON Schema）**
- **Function Calling**
- **Plan-Execute 模式**

### 深入讲解

#### 2.1 从 LLM 应用到 Agent 的演进

| 形态 | 输入 | 处理 | 输出 | 典型场景 |
|---|---|---|---|---|
| LLM 应用 | prompt | 单次生成 | 文本 | 翻译、摘要 |
| 单 Agent | prompt + 工具 | 多轮思考-行动循环 | 文本/行动 | 计算器、搜索 |
| Multi-Agent | prompt + 工具 + 多个专家 | 任务分发、协作、评估 | 综合结果 | 复杂工作流 |

#### 2.2 ReAct 范式的严格定义

ReAct 由 Princeton 和 Google Research 在 2022 年提出，核心思想是将推理（Reasoning）和行动（Acting）交错进行：

```
Thought: 我需要先搜索相关信息。
Action: web_search(query="...")
Observation: 搜索结果显示...

Thought: 根据搜索结果，我需要计算...
Action: calculate(expression="...")
Observation: 计算结果为...

Thought: 我已经有足够信息，可以给出答案。
Action: finish(answer="...")
```

**为什么有效**：

- 把中间推理过程显式化，便于调试。
- 行动结果作为 observation 回到上下文，减少幻觉。
- 可以处理需要多步信息获取的任务。

#### 2.3 Function Calling 的协议层

Function Calling 不是魔法，而是一个**结构化输出协议**：

1. 调用方提供一组工具定义（JSON Schema）。
2. 模型根据用户输入，决定是否输出 `tool_calls`。
3. 调用方解析 `tool_calls`，执行对应函数。
4. 函数结果以 `tool` / `function` 角色加入消息历史。
5. 模型根据函数结果生成最终回答。

**关键协议字段**：

```json
{
  "id": "call_xxx",
  "type": "function",
  "function": {
    "name": "get_weather",
    "arguments": "{\"city\": \"北京\"}"
  }
}
```

#### 2.4 Plan-Execute vs ReAct

ReAct 是**边想边做**，Plan-Execute 是**先规划后执行**。

| 模式 | 优点 | 缺点 | 适用场景 |
|---|---|---|---|
| ReAct | 灵活，能根据观察调整 | 可能陷入局部最优 | 信息不完全、需要探索 |
| Plan-Execute | 全局规划，执行稳定 | 计划错误时成本高 | 步骤明确、可分解 |

Nexus 的 Planner Agent 就是 Plan-Execute 思想的体现，而 Orchestrator 在计划执行过程中也保留了 ReAct 式的循环能力。

### 代码实验室

#### 实验 2.1：最小 ReAct Agent

```python
import json
import dashscope
import os

dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

def calculate(expression):
    try:
        return str(eval(expression))  # 仅示例，生产环境用 AST
    except Exception as e:
        return f"Error: {e}"

tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算数学表达式",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式"}
                },
                "required": ["expression"]
            }
        }
    }
]

messages = [
    {"role": "system", "content": "你可以使用 calculate 工具帮助用户计算。请用中文回答。"},
    {"role": "user", "content": "123 乘以 456 等于多少？"},
]

response = dashscope.Generation.call(
    model="qwen-turbo",
    messages=messages,
    tools=tools,
    result_format="message",
)

msg = response.output.choices[0].message
print("模型输出:", msg)

if "tool_calls" in msg and msg["tool_calls"]:
    tool_call = msg["tool_calls"][0]
    name = tool_call["function"]["name"]
    args = json.loads(tool_call["function"]["arguments"])
    result = calculate(**args)
    print(f"工具 {name} 执行结果: {result}")

    messages.append(msg)
    messages.append({
        "role": "tool",
        "content": result,
        "tool_call_id": tool_call["id"],
    })

    final_response = dashscope.Generation.call(
        model="qwen-turbo",
        messages=messages,
        tools=tools,
        result_format="message",
    )
    print("最终回答:", final_response.output.choices[0].message["content"])
```

### 自测题

**Q1：ReAct 中的 Observation 有什么作用？**

A1：Observation 是工具执行后返回的事实信息，被重新加入模型上下文。它让模型基于真实结果继续推理，而不是基于想象，从而减少幻觉。

**Q2：Function Calling 和普通的文本生成有什么本质区别？**

A2：Function Calling 是模型被训练成输出结构化调用指令（tool_calls），而普通文本生成是自由文本。本质上都是生成 token，但输出空间和解析方式不同。

**Q3：什么场景不适合用 Agent？**

A3：以下场景通常不适合：
- 输入输出映射明确，规则即可解决（如简单数据转换）。
- 对延迟和成本敏感，且不需要多步推理。
- 需要严格可解释性和确定性的场景（如金融核心交易）。

**Q4：Plan-Execute 模式和 ReAct 模式在 Nexus 中分别体现在哪里？**

A4：Planner Agent 体现 Plan-Execute，它先输出完整执行计划；Orchestrator 在计划执行过程中根据 Critic 反馈可能重新调度，体现了 ReAct 的循环调整思想。

### 动手练习

#### 练习 2.1：实现一个支持多工具的 ReAct Agent

**目标**：让 Agent 能交替使用 `search_docs` 和 `calculate` 工具，直到不需要调用工具。

**步骤**：

1. 定义两个工具：
   - `search_docs(query)`：返回模拟文档片段。
   - `calculate(expression)`：计算表达式。
2. 实现 Agent 循环：
   - 调用模型。
   - 如果有 tool_calls，执行工具并把结果加入历史。
   - 重复直到没有 tool_calls。
3. 用问题测试："Python 列表和元组有什么区别？2 的 10 次方是多少？"

**参考答案框架**：

```python
import json

class ReActAgent:
    def __init__(self, llm_client, tools):
        self.llm = llm_client
        self.tools = {tool["function"]["name"]: tool for tool in tools}
        self.messages = []

    def run(self, query, max_turns=5):
        self.messages.append({"role": "user", "content": query})
        for _ in range(max_turns):
            response = self.llm.chat(self.messages, tools=list(self.tools.values()))
            content = response["content"]
            tool_calls = response.get("tool_calls")

            if not tool_calls:
                return content

            self.messages.append({"role": "assistant", "content": content, "tool_calls": tool_calls})
            for tc in tool_calls:
                name = tc["function"]["name"]
                args = json.loads(tc["function"]["arguments"])
                result = self.execute_tool(name, args)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": str(result),
                })
        return "达到最大轮次"

    def execute_tool(self, name, args):
        if name == "search_docs":
            return f"关于 {args['query']} 的模拟检索结果。"
        elif name == "calculate":
            return eval(args["expression"])  # 生产环境用 AST
        return "未知工具"
```

#### 练习 2.2：设计一个工具的 JSON Schema

**目标**：为一个 `read_file` 工具设计 JSON Schema，要求：

- 参数：path（文件路径）、encoding（编码，默认 utf-8）。
- path 必须是字符串，encoding 只能是 utf-8 或 gbk。

**参考答案**：

```json
{
  "type": "function",
  "function": {
    "name": "read_file",
    "description": "读取指定路径的文本文件内容",
    "parameters": {
      "type": "object",
      "properties": {
        "path": {
          "type": "string",
          "description": "要读取的文件路径"
        },
        "encoding": {
          "type": "string",
          "enum": ["utf-8", "gbk"],
          "default": "utf-8",
          "description": "文件编码"
        }
      },
      "required": ["path"]
    }
  }
}
```

### 常见错误

1. **不验证工具参数**：模型生成的参数可能不合法，执行前必须校验 JSON Schema。
2. **忘记把工具结果加入上下文**：导致模型看不到执行结果，循环出错。
3. **max_turns 不设限**：Agent 可能陷入无限循环。
4. **工具描述写得太模糊**：模型无法判断什么时候该调用哪个工具。

### 进阶阅读

1. 论文：《ReAct: Synergizing Reasoning and Acting in Language Models》。
2. LangChain Agent 文档：ReAct Agent、Plan-and-Execute Agent。
3. OpenAI Function Calling 最佳实践。

### 本节检查清单

- [ ] 能画出 ReAct 的 Thought-Action-Observation 循环。
- [ ] 能独立实现一个最小 Function Calling 流程。
- [ ] 能区分 Plan-Execute 和 ReAct 的适用场景。
- [ ] 知道 Agent 循环必须设置 max_turns。

---

## 第 3 课：RAG 系统的设计与优化

### 本节目标

学完本节后，你能够：

- 设计一个完整的 RAG 流程，包括加载、分块、向量化、检索、生成。
- 根据数据特点选择合适的分块策略。
- 评估 RAG 检索质量和生成质量。
- 诊断 RAG 系统的常见问题（检索不到、检索到无关、回答幻觉）。

### 前置检查

- 已理解 Embedding 和向量相似度的基本概念。
- 已能调用 LLM API。

### 关键概念

- **Document Loader**
- **Text Splitter**
- **Embedding Model**
- **Vector Store / Vector Database**
- **Retriever**
- **Top-K / MMR / Similarity Threshold**

### 深入讲解

#### 3.1 RAG 的完整数据流

```
离线阶段：
原始文档 → Loader 提取文本 → Splitter 分块 → Embedding 模型编码 → 存入 Vector Store

在线阶段：
用户 query → Embedding 模型编码 → Vector Store 相似度检索 → Top-K 片段 + query → LLM 生成回答
```

#### 3.2 文档加载的多样性

RAG 的数据源可能是：

- 本地文件：txt、md、pdf、docx、csv
- 网页：HTML
- 数据库：SQL 查询结果
- API：Notion、Obsidian、飞书文档

每种数据源需要不同的 Loader。Nexus 的 `rag/loader.py` 会封装这些差异。

#### 3.3 分块策略的选择

分块是 RAG 中最影响质量的环节之一。

**固定长度分块**：

```python
from langchain.text_splitter import CharacterTextSplitter

splitter = CharacterTextSplitter(
    separator="\n\n",
    chunk_size=500,
    chunk_overlap=50,
)
```

**递归字符分块**：

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", " ", ""],
)
```

递归分块会优先按语义边界（段落、句子）切分，比纯固定长度效果更好。

**分块参数的选择原则**：

- chunk_size：取决于 Embedding 模型的输入限制和语义完整性。常见 200 ~ 1000。
- chunk_overlap：保证上下文连续性，常见 10% ~ 20%。

#### 3.4 Embedding 模型选型

| 模型 | 特点 | 适用场景 |
|---|---|---|
| text-embedding-v3（通义） | 中文效果好 | 中文知识库 |
| text-embedding-ada-002（OpenAI） | 通用、稳定 | 英文或多语言 |
| BGE / GTE 系列 | 开源、可本地部署 | 隐私敏感场景 |

选型考虑：语言、成本、是否需本地部署、向量维度。

#### 3.5 检索策略

**相似度检索（Similarity Search）**：

- 返回与 query 向量最相似的 K 个片段。
- 简单直接，但可能返回过于相似的冗余内容。

**最大边际相关性（MMR）**：

- 在相似性和多样性之间做权衡。
- 适合需要覆盖多个角度的 query。

**相似度阈值过滤**：

- 只返回相似度高于阈值的片段。
- 避免返回"硬凑"的无关结果。

#### 3.6 RAG 评估

**检索评估**：

- 准备一组 query 和对应的相关文档标注。
- 计算 Hit Rate、MRR（Mean Reciprocal Rank）、NDCG。

**生成评估**：

- 准备标准答案。
- 用 LLM-as-a-Judge 打分。
- 用 BERTScore 计算语义相似度。

### 代码实验室

#### 实验 3.1：用 LangChain + Chroma 构建最小 RAG

```python
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

# 1. 加载文档
loader = TextLoader("docs/python_guide.txt", encoding="utf-8")
documents = loader.load()

# 2. 分块
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)

# 3. 存入 Chroma
embeddings = DashScopeEmbeddings(model="text-embedding-v3", dashscope_api_key="...")
vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")

# 4. 检索
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
results = retriever.invoke("Python 列表和元组有什么区别？")
for doc in results:
    print(doc.page_content[:200])
```

### 自测题

**Q1：为什么分块策略对 RAG 质量影响很大？**

A1：分块决定了每个片段的语义完整性。如果切分位置不当，会把一个完整概念切断，导致检索到的片段缺少上下文；或者把无关内容混在一起，降低检索精度。

**Q2：MMR 和相似度检索有什么区别？**

A2：相似度检索只按与 query 的相似度排序返回 Top-K；MMR 在相似度的基础上引入多样性惩罚，避免返回内容高度重复的片段，更适合需要多角度信息的 query。

**Q3：如何评估 RAG 检索的好坏？**

A3：常用指标包括：
- Hit Rate：相关文档是否出现在 Top-K 中。
- MRR：第一个相关文档的排名倒数。
- NDCG：考虑排序位置的加权相关性。
这些指标需要人工标注或自动标注的 relevance 数据。

**Q4：RAG 仍然出现幻觉的可能原因有哪些？**

A4：
- 检索到的片段不包含答案，但模型强行生成。
- 检索结果有误导性信息。
- prompt 没有明确约束"不知道就回答不知道"。
- 模型过度依赖自身参数知识而非检索内容。

### 动手练习

#### 练习 3.1：比较不同分块参数的效果

**目标**：固定 query，比较不同 chunk_size 和 chunk_overlap 下的检索结果。

**步骤**：

1. 用 `docs/python_guide.txt` 作为数据源。
2. 尝试三组参数：
   - chunk_size=200, overlap=0
   - chunk_size=500, overlap=50
   - chunk_size=1000, overlap=100
3. 对同一个 query（如"Python 装饰器是什么"），记录每组返回的 Top-3 片段。
4. 从语义完整性和相关性两个维度评分。

**参考答案思路**：

```python
configs = [
    {"chunk_size": 200, "chunk_overlap": 0},
    {"chunk_size": 500, "chunk_overlap": 50},
    {"chunk_size": 1000, "chunk_overlap": 100},
]

for config in configs:
    splitter = RecursiveCharacterTextSplitter(**config)
    chunks = splitter.split_documents(documents)
    vectorstore = Chroma.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    results = retriever.invoke("Python 装饰器")
    print(f"\nConfig: {config}")
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc.page_content[:100]}...")
```

#### 练习 3.2：实现一个 RAG 答案生成器

**目标**：把检索结果和用户 query 拼接成 prompt，让模型生成带引用的回答。

**步骤**：

1. 检索 Top-K 片段。
2. 为每个片段编号。
3. 构造 prompt："根据以下参考资料回答问题，如果不知道就回答不知道。[资料 1] ... [资料 2] ... 问题：..."
4. 让模型生成回答，并尝试让模型在回答中标注引用来源。

**参考答案框架**：

```python
def generate_answer(query, retrieved_docs, llm_client):
    context = "\n\n".join(
        f"[资料 {i+1}]\n{doc.page_content}"
        for i, doc in enumerate(retrieved_docs)
    )
    prompt = f"""根据以下参考资料回答问题。如果参考资料中没有答案，请明确回答"根据现有资料无法回答"。
请在回答中标注引用来源的编号，如 [1]、[2]。

{context}

问题：{query}
"""
    response = llm_client.chat([
        {"role": "system", "content": "你是一位严谨的问答助手。"},
        {"role": "user", "content": prompt},
    ])
    return response["content"]
```

### 常见错误

1. ** chunk_size 过大导致检索不精确**：大块包含多个主题，相似度计算会被稀释。
2. **不做来源标注**：用户无法验证回答，降低可信度。
3. **检索结果为空时不处理**：模型可能开始编造答案。
4. **Embedding 模型与语言不匹配**：英文模型处理中文会损失语义。

### 进阶阅读

1. 论文：《Retrieval-Augmented Generation for Large Language Models: A Survey》。
2. LangChain RAG 文档：Retrieval、Document Loaders、Text Splitters。
3. Hugging Face MTEB 排行榜：选择 Embedding 模型。

### 本节检查清单

- [ ] 能画出完整 RAG 数据流。
- [ ] 能根据场景选择分块策略和参数。
- [ ] 能解释 MMR 和相似度检索的区别。
- [ ] 能设计至少两个 RAG 评估指标。

---

## 第 4 课：Function Calling 的协议设计与安全实现

### 本节目标

学完本节后，你能够：

- 设计符合 JSON Schema 规范的工具定义。
- 实现一个安全的 Python 代码执行沙箱。
- 处理工具调用失败、参数错误、超时等异常情况。
- 设计统一的工具返回协议。

### 前置检查

- 已理解 ReAct 和 Function Calling 流程。
- 已了解 JSON Schema 基础。

### 关键概念

- **JSON Schema**
- **AST（Abstract Syntax Tree）**
- **沙箱执行（Sandboxed Execution）**
- **Tool Registry**
- **参数校验**

### 深入讲解

#### 4.1 JSON Schema 在工具定义中的作用

JSON Schema 是工具与模型之间的**接口契约**：

- 告诉模型每个参数的名称、类型、是否必填。
- 让调用方在执行前校验模型输出。
- 作为文档，方便开发者维护工具。

#### 4.2 安全执行 Python 的原理

`eval` 和 `exec` 的问题在于它们会执行任意代码。安全做法是用 AST 白名单：

1. 用 `ast.parse(code, mode='eval')` 解析表达式。
2. 遍历 AST 节点。
3. 只允许白名单内的节点类型。
4. 解释执行白名单节点。

#### 4.3 Tool Registry 的设计

Tool Registry 需要支持：

- 注册工具。
- 根据名字查找工具。
- 校验参数。
- 执行并捕获异常。
- 返回统一格式。

### 代码实验室

#### 实验 4.1：AST 安全表达式求值

```python
import ast
import operator

class SafeEvaluator:
    ALLOWED_NODES = (
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
        ast.USub, ast.UAdd,
    )

    def eval(self, expression):
        tree = ast.parse(expression, mode='eval')
        for node in ast.walk(tree):
            if not isinstance(node, self.ALLOWED_NODES):
                raise ValueError(f"Disallowed node: {type(node).__name__}")
        return self._eval_node(tree.body)

    def _eval_node(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.BinOp):
            ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
                ast.Pow: operator.pow,
            }
            return ops[type(node.op)](self._eval_node(node.left), self._eval_node(node.right))
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.USub):
                return -self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +self._eval_node(node.operand)
        raise ValueError(f"Unsupported node: {type(node).__name__}")

evaluator = SafeEvaluator()
print(evaluator.eval("(2 + 3) * 4"))  # 20
# print(evaluator.eval("__import__('os').system('ls')"))  # 会报错
```

### 自测题

**Q1：为什么 JSON Schema 对 Function Calling 至关重要？**

A1：JSON Schema 是模型生成参数的结构化约束，也是调用方校验参数是否合法的依据。没有它，模型不知道参数的合法取值，调用方也无法安全执行。

**Q2：AST 白名单沙箱和黑名单沙箱有什么区别？为什么用白名单？**

A2：白名单只允许明确的节点类型，其他全部禁止；黑名单只禁止已知危险的节点类型。由于 Python AST 节点类型很多，黑名单很难覆盖所有绕过方式，因此安全场景必须用白名单。

**Q3：execute_python 返回错误时，应该怎么传递给模型？**

A3：应该把错误信息以 tool / function 角色加入消息历史，让模型基于错误信息决定下一步。错误信息要包含足够上下文，但不要暴露敏感路径或内部实现细节。

### 动手练习

#### 练习 4.1：扩展 SafeEvaluator 支持函数调用

**目标**：在 SafeEvaluator 中安全地支持 `math.sqrt`、`math.sin` 等白名单函数。

**步骤**：

1. 允许 `ast.Call` 节点。
2. 只允许 `math` 模块中的特定函数。
3. 校验函数名在白名单中。
4. 递归求值参数。
5. 调用真实函数。

**参考答案框架**：

```python
import math

class SafeEvaluator:
    ALLOWED_FUNCTIONS = {"sqrt": math.sqrt, "sin": math.sin, "cos": math.cos}

    def _eval_node(self, node):
        # ... 之前的逻辑
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only simple function calls allowed")
            func_name = node.func.id
            if func_name not in self.ALLOWED_FUNCTIONS:
                raise ValueError(f"Function {func_name} not allowed")
            args = [self._eval_node(arg) for arg in node.args]
            return self.ALLOWED_FUNCTIONS[func_name](*args)
        raise ValueError(f"Unsupported node: {type(node).__name__}")
```

#### 练习 4.2：实现 ToolRegistry

**目标**：实现一个支持注册、查找、执行、参数校验的 ToolRegistry。

**参考答案框架**：

```python
import json
from jsonschema import validate, ValidationError

class ToolRegistry:
    def __init__(self):
        self._tools = {}

    def register(self, name, description, parameters, handler):
        self._tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "handler": handler,
        }

    def call(self, name, arguments):
        tool = self._tools.get(name)
        if not tool:
            return {"error": f"Tool '{name}' not found"}
        try:
            args = json.loads(arguments) if isinstance(arguments, str) else arguments
            validate(instance=args, schema=tool["parameters"])
            result = tool["handler"](**args)
            return {"result": result, "tool": name, "args": args}
        except ValidationError as e:
            return {"error": f"Invalid arguments: {e.message}", "tool": name}
        except Exception as e:
            return {"error": str(e), "tool": name}
```

### 常见错误

1. **用 eval 执行用户输入**：最严重的安全问题。
2. **不校验工具参数**：模型可能生成缺失必填字段的参数。
3. **工具返回格式不统一**：增加 Orchestrator 和 Summarizer 的处理复杂度。
4. **异常信息泄露敏感信息**：如文件绝对路径、数据库连接字符串。

### 进阶阅读

1. Python `ast` 模块官方文档。
2. JSON Schema 官方规范。
3. 论文：《Tool Learning with Foundation Models》。

### 本节检查清单

- [ ] 能写出符合 JSON Schema 的工具定义。
- [ ] 能实现基于 AST 的安全表达式求值。
- [ ] 能实现 ToolRegistry 的注册、查找、执行、校验。
- [ ] 知道如何处理工具执行异常。

---

# 模块二：Nexus 架构实现

## 第 5 课：Nexus 的系统架构与演进策略

### 本节目标

学完本节后，你能够：

- 解释 Nexus 的组件职责和交互关系。
- 说明从 ai-demos 到 Nexus 的演进动机。
- 制定一个分阶段的开发计划。
- 判断某个功能应该放在哪个阶段实现。

### 前置检查

- 已完成模块一的学习。
- 已阅读 `docs/superpowers/specs/2026-06-18-nexus-personal-ai-workflow-agent-design.md`。

### 关键概念

- **Multi-Agent 架构**
- **消息总线（Message Bus）**
- **分层架构**
- **接口先行**
- **MVP（Minimum Viable Product）**

### 深入讲解

#### 5.1 Nexus 的架构分层

Nexus 采用分层架构：

| 层级 | 组件 | 职责 |
|---|---|---|
| 接入层 | Web Gateway（FastAPI + SSE） | 接收用户请求，推送流式事件 |
| 编排层 | Orchestrator Agent | 任务调度、状态管理、结果聚合 |
| 协作层 | Message Bus | Agent 间异步通信 |
| 专家层 | Planner / Retriever / Executor / Summarizer / Critic | 各专业化 Agent |
| 能力层 | Tool Registry / Knowledge Base / Memory Store | 工具、知识库、记忆 |

#### 5.2 从 ai-demos 到 Nexus 的演进动机

原 ai-demos 的问题：

1. **项目同质化**：两个 demo 都是 Python + FastAPI + 通义千问，缺乏差异化。
2. **缺少真实价值**：RAG 只处理示例文档，Agent 工具都是 mock。
3. **缺少评估闭环**：没有回答质量评估。
4. **缺少系统架构**：两个 demo 孤立，没有整合。

Nexus 的解决方案：

- 合并 RAG 和 Function Calling 为统一 Agent 系统。
- 引入 Multi-Agent 架构，职责分离。
- 增加真实工具和质量评估。
- 分阶段实现，每个阶段都有可运行的版本。

#### 5.3 分阶段策略

| 阶段 | 目标 | 关键产出 |
|---|---|---|
| Phase 1 | 验证 Multi-Agent 协作骨架 | CLI 可运行 |
| Phase 2 | 接入真实 RAG 和工具 | 能检索知识库、调用真实工具 |
| Phase 3 | Web UI + SSE | 浏览器可用 |
| Phase 4 | 记忆持久化 + 评估优化 | 有长期记忆和评估数据 |
| Phase 5 | 团队版扩展 | 多用户、外部消息中间件 |

### 自测题

**Q1：Nexus 为什么采用 Multi-Agent 而不是单 Agent？**

A1：单 Agent 需要同时承担规划、检索、执行、总结、评估等职责，代码复杂且难以维护。Multi-Agent 把职责拆给专业化 Agent，通过消息总线协作，每个 Agent 职责单一、易于测试和扩展。

**Q2：接口先行（interface-first）在 Nexus 中如何体现？**

A2：Phase 1 中 Retriever 和 Executor 先用 mock 实现，但保持与真实版本一致的接口。Phase 2 替换实现时，其他 Agent 不需要大改。

**Q3：为什么 Phase 1 要先做 CLI 而不是 Web UI？**

A3：CLI 开发成本低、调试方便，适合快速验证核心架构。Web UI 涉及前后端联调、SSE、状态管理，复杂度更高，放到 Phase 3 更合理。

### 动手练习

#### 练习 5.1：画出 Nexus 架构图

**目标**：用 draw.io 或纸笔画出 Nexus 的组件图，标注每个组件的职责和数据流。

**要求**：

- 包含用户、Web Gateway、Orchestrator、Message Bus、五个专业 Agent、Tool Registry、Knowledge Base、Memory Store。
- 用箭头表示消息流向。

#### 练习 5.2：制定一个你自己的分阶段计划

**目标**：假设你要做一个"代码审查 Agent"，制定 Phase 1 ~ Phase 3 计划。

**参考答案框架**：

```
Phase 1：单 Agent 能读取文件并调用 LLM 做审查。
Phase 2：Multi-Agent，拆分为代码分析 Agent、规范检查 Agent、总结 Agent。
Phase 3：接入 GitHub PR，自动评论审查结果。
```

### 常见错误

1. **一开始就追求大而全**：导致项目长期无法运行，失去反馈。
2. **阶段划分不清晰**：每个阶段没有明确可展示成果。
3. **过早优化**：Phase 1 就考虑分布式、高并发。

### 进阶阅读

1. 《Designing Data-Intensive Applications》—— 系统设计基础。
2. AutoGen、CrewAI、MetaGPT 等 Multi-Agent 框架源码。

### 本节检查清单

- [ ] 能画出 Nexus 架构图并解释每个组件。
- [ ] 能说明 ai-demos 到 Nexus 的演进动机。
- [ ] 能为一个新项目制定分阶段计划。

---

## 第 6 课：Message Bus 与异步协作机制

### 本节目标

学完本节后，你能够：

- 实现一个基于 asyncio.Queue 的消息总线。
- 理解点对点、广播、请求-响应三种通信模式。
- 处理超时、死锁、消息丢失等异步问题。
- 解释为什么消息总线比直接函数调用更适合 Multi-Agent。

### 前置检查

- 已理解 Python asyncio 基础。
- 已理解队列（Queue）数据结构。

### 关键概念

- **asyncio.Queue**
- **Pub/Sub（发布-订阅）**
- **Future / Task**
- **Timeout**
- **Deadlock**

### 深入讲解

#### 6.1 消息总线的通信模式

**点对点**：

```
Orchestrator → Planner
```

**广播**：

```
Orchestrator → broadcast
              ├─→ Planner
              ├─→ Retriever
              └─→ Executor
```

**请求-响应**：

```
Orchestrator → send_and_wait → Retriever
Retriever → publish result → Orchestrator
```

#### 6.2 asyncio.Queue 的选择

`asyncio.Queue` 是线程安全的协程队列：

- `await queue.get()`：阻塞直到有消息。
- `await queue.put(msg)`：放入消息。
- 支持 maxsize 限制。

#### 6.3 send_and_wait 的 Future 实现

核心思路：

1. Orchestrator 为每个 task_id 创建一个 Future。
2. 发送消息后等待 Future。
3. Orchestrator 的消息循环收到结果时，设置对应 Future 的结果。

```python
async def _send_and_wait(self, recipient, message, timeout):
    future = asyncio.get_event_loop().create_future()
    self._pending_futures[message.task_id] = future
    await self.bus.publish(message)
    try:
        return await asyncio.wait_for(future, timeout=timeout)
    finally:
        self._pending_futures.pop(message.task_id, None)
```

#### 6.4 为什么不用直接函数调用

| 维度 | 函数调用 | 消息总线 |
|---|---|---|
| 耦合 | 高 | 低 |
| 扩展性 | 新增 Agent 需改调用方 | 新增 Agent 只需订阅消息 |
| 异步 | 需显式 await | 天然异步 |
| 调试 | 堆栈清晰 | 需跟踪消息流 |
| 分布式 | 不支持 | 未来可替换为 Redis |

### 自测题

**Q1：消息总线的广播模式和点对点模式分别适用于什么场景？**

A1：广播适合通知所有 Agent 某个全局事件（如系统关闭）；点对点适合定向任务分发（如 Orchestrator 让 Planner 做计划）。

**Q2：send_and_wait 中为什么要用 Future 而不是一直从队列里轮询？**

A2：Future 是事件驱动的，收到结果时立即唤醒等待协程；轮询需要不断尝试从队列取消息并判断 task_id，效率低且代码复杂。

**Q3：如果 Orchestrator 同时处理多个任务，怎么保证不会拿到别的任务的结果？**

A3：通过 task_id 关联 Future。每个任务有唯一 task_id，结果消息里也携带 task_id，Orchestrator 根据 task_id 找到对应 Future。

### 动手练习

#### 练习 6.1：独立实现 MessageBus

**目标**：不参考 Nexus 代码，实现一个支持 subscribe / publish / send_and_wait 的 MessageBus。

**要求**：

- publish 支持广播。
- send_and_wait 支持超时。
- 用 pytest-asyncio 写测试。

**参考答案框架**：

```python
import asyncio
from dataclasses import dataclass, field
from typing import Dict, Any
from uuid import uuid4

@dataclass
class Message:
    task_id: str
    sender: str
    recipient: str
    message_type: str
    payload: Dict[str, Any]
    message_id: str = field(default_factory=lambda: str(uuid4()))

class MessageBus:
    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}

    def subscribe(self, agent_id: str) -> asyncio.Queue:
        if agent_id not in self._queues:
            self._queues[agent_id] = asyncio.Queue()
        return self._queues[agent_id]

    async def publish(self, message: Message) -> None:
        if message.recipient == "broadcast":
            for queue in self._queues.values():
                await queue.put(message)
        else:
            queue = self._queues.get(message.recipient)
            if queue is None:
                raise ValueError(f"No subscriber for {message.recipient}")
            await queue.put(message)

    async def send_and_wait(self, recipient, message, timeout=30.0):
        await self.publish(message)
        queue = self.subscribe("orchestrator")
        deadline = asyncio.get_event_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_event_loop().time()
            if remaining <= 0:
                raise asyncio.TimeoutError()
            msg = await asyncio.wait_for(queue.get(), timeout=remaining)
            if msg.sender == recipient and msg.task_id == message.task_id:
                return msg
            await queue.put(msg)
```

#### 练习 6.2：处理消息超时

**目标**：测试 send_and_wait 在超时情况下的行为。

**参考答案**：

```python
import pytest

@pytest.mark.asyncio
async def test_send_and_wait_timeout():
    bus = MessageBus()
    msg = Message(task_id="t1", sender="orchestrator", recipient="retriever", message_type="task", payload={})
    with pytest.raises(asyncio.TimeoutError):
        await bus.send_and_wait("retriever", msg, timeout=0.1)
```

### 常见错误

1. **Future 没有清理**：任务完成后没有从 `_pending_futures` 删除，导致内存泄漏。
2. **消息队列里没有响应**：recipient 没启动或没正确处理消息，send_and_wait 一直超时。
3. **广播时没有排除发送方**：可能把自己发的消息又收回来，造成循环。
4. **在同步代码里调用 async publish**：需要用 `asyncio.run` 或 `await`。

### 进阶阅读

1. Python asyncio 官方文档：Queue、Future、Task。
2. RabbitMQ / Redis Pub/Sub 文档（理解分布式消息总线）。

### 本节检查清单

- [ ] 能独立实现 MessageBus。
- [ ] 能解释 Future 在 send_and_wait 中的作用。
- [ ] 能写出消息总线的单元测试。
- [ ] 能列举消息总线相比函数调用的优势和劣势。

---

## 第 7 课：BaseAgent 与专业 Agent 设计

### 本节目标

学完本节后，你能够：

- 设计一个可扩展的 Agent 基类。
- 实现 Orchestrator、Planner、Retriever、Executor、Summarizer、Critic 六个 Agent。
- 理解每个 Agent 的职责边界。
- 设计 Agent 之间的消息协议。

### 前置检查

- 已实现 MessageBus。
- 已理解抽象基类（ABC）和 async/await。

### 关键概念

- **BaseAgent**
- **Agent Loop**
- **消息协议（Message Protocol）**
- **职责分离（Separation of Concerns）**

### 深入讲解

#### 7.1 BaseAgent 的设计

BaseAgent 是所有 Agent 的公共骨架：

```python
class BaseAgent:
    def __init__(self, agent_id, bus, llm):
        self.agent_id = agent_id
        self.bus = bus
        self.llm = llm
        self._running = False

    async def run(self):
        self._running = True
        queue = self.bus.subscribe(self.agent_id)
        while self._running:
            try:
                message = await asyncio.wait_for(queue.get(), timeout=0.5)
                await self.handle_message(message)
            except asyncio.TimeoutError:
                continue

    @abstractmethod
    async def handle_message(self, message): ...

    async def send_message(self, recipient, message_type, payload, task_id):
        await self.bus.publish(Message(
            task_id=task_id,
            sender=self.agent_id,
            recipient=recipient,
            message_type=message_type,
            payload=payload,
        ))

    async def think(self, system_prompt, user_prompt, tools=None):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return self.llm.chat(messages, tools=tools)
```

#### 7.2 Orchestrator 的状态机

Orchestrator 维护 `SessionState`：

```
pending → planning → executing → summarizing → critiquing → done
```

每个状态对应一次对外部 Agent 的调用。

#### 7.3 Planner 的输出协议

Planner 返回 JSON Plan：

```json
{
  "steps": [
    {"step_id": 1, "agent": "retriever", "task": "检索 xxx"},
    {"step_id": 2, "agent": "executor", "task": "执行 yyy"},
    {"step_id": 3, "agent": "summarizer", "task": "总结 zzz"}
  ]
}
```

Orchestrator 按 step 顺序执行。

### 自测题

**Q1：BaseAgent 的 run 方法为什么用 0.5 秒超时？**

A1：为了定期检查 `_running` 标志，响应 stop() 调用。如果直接 await queue.get()，队列会永久阻塞，无法优雅退出。

**Q2：如果 Planner 返回的 JSON 不合法，Orchestrator 应该怎么办？**

A2：Planner 应该内部降级为默认计划；Orchestrator 也可以捕获异常并使用保守计划（如只检索后总结），保证系统不崩溃。

**Q3：Critic 的 critique 消息类型为什么是独立的？**

A3：critique 是评估结果，可能触发 Orchestrator 的重试逻辑。用独立类型便于 Orchestrator 区分普通结果和评估反馈。

### 动手练习

#### 练习 7.1：实现 EchoAgent

**目标**：继承 BaseAgent，实现一个收到消息后立即把内容返回的 EchoAgent。

**参考答案**：

```python
class EchoAgent(BaseAgent):
    async def handle_message(self, message):
        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"echo": message.payload},
            task_id=message.task_id,
        )
```

#### 练习 7.2：实现简单 Orchestrator

**目标**：实现一个 Orchestrator，能调度 EchoAgent 并返回结果。

**参考答案框架**：

```python
class SimpleOrchestrator(BaseAgent):
    async def process(self, query):
        task_id = str(uuid.uuid4())
        future = asyncio.get_event_loop().create_future()
        self._pending[task_id] = future
        await self.send_message(
            recipient="echo",
            message_type="task",
            payload={"text": query},
            task_id=task_id,
        )
        result = await asyncio.wait_for(future, timeout=5.0)
        return result.payload

    async def handle_message(self, message):
        if message.message_type == "result":
            future = self._pending.get(message.task_id)
            if future and not future.done():
                future.set_result(message)
```

### 常见错误

1. **Agent 不调用 stop()**：导致程序无法退出。
2. **handle_message 里没有 await**：异步操作要 await，否则消息没发出去。
3. **task_id 冲突**：未使用 UUID，多个任务可能冲突。
4. **抽象方法未实现**：子类忘记实现 handle_message。

### 进阶阅读

1. Python ABC 模块官方文档。
2. LangChain Agent 源码结构。
3. AutoGen 的 ConversableAgent 设计。

### 本节检查清单

- [ ] 能实现 BaseAgent 和至少一个子类。
- [ ] 能解释 Orchestrator 的状态机。
- [ ] 能设计 Agent 间消息协议。
- [ ] 能写出 Agent 的单元测试。

---

## 第 8 课：Phase 2 — 真实 RAG 与 Tool Registry 实现

### 本节目标

学完本节后，你能够：

- 把 Phase 1 的 mock Retriever 替换为基于 Chroma 的真实检索。
- 实现 Tool Registry，注册并执行真实工具。
- 设计多集合知识库。
- 保证代码执行工具的安全性。

### 前置检查

- 已完成 RAG 基础学习。
- 已实现 ToolRegistry 和 SafeEvaluator。

### 关键概念

- **Collection（Chroma）**
- **Metadata**
- **Source Tracing**
- **Tool Registry**
- **AST Sandbox**

### 深入讲解

#### 8.1 Chroma 多集合设计

```python
vectorstore = Chroma(
    collection_name="notes",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
)
```

每个 collection 对应一类知识来源：

- notes：个人笔记
- code_docs：代码文档
- web_articles：网页文章
- manual：手动输入

#### 8.2 Retriever Agent 的 Phase 2 版本

```python
class RetrieverAgent(BaseAgent):
    async def handle_message(self, message):
        query = message.payload.get("query", "")
        collection = message.payload.get("collection", "notes")
        results = self.vectorstore.similarity_search(query, k=5, filter={"collection": collection})
        documents = [
            {
                "content": doc.page_content,
                "source": doc.metadata.get("source", "unknown"),
                "score": doc.metadata.get("score", 0.0),
            }
            for doc in results
        ]
        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"documents": documents, "query": query},
            task_id=message.task_id,
        )
```

#### 8.3 工具安全边界

- `execute_python`：AST 白名单，禁止 import、open、网络请求。
- `read_file`：路径白名单，防止越界访问。
- `list_files`：限制在指定工作目录内。

### 自测题

**Q1：多集合知识库相比单集合有什么优势？**

A1：可以按来源检索、过滤和管理；不同集合可以使用不同的分块策略和元数据；便于来源追踪和权限控制。

**Q2：Retriever Agent 的接口在 Phase 1 和 Phase 2 之间是否变化？**

A2：不变化。输入仍然是 query，输出仍然是 documents 列表。变化的只是内部实现从 mock 换成了 Chroma 检索。

**Q3：Tool Registry 中如何处理工具执行异常？**

A3：捕获异常并返回统一错误格式， Orchestrator 根据错误决定是否重试、换工具或终止任务。

### 动手练习

#### 练习 8.1：把 mock Retriever 替换为 Chroma

**步骤**：

1. 用 `docs/python_guide.txt` 构建 Chroma 集合。
2. 修改 `core/agents/retriever.py`。
3. 运行测试，验证检索结果。

#### 练习 8.2：注册真实工具

**目标**：在 ToolRegistry 中注册 `search_docs`、`execute_python`、`read_file`。

**参考答案框架**：见第 4 课练习 4.2。

### 常见错误

1. **Chroma 集合不存在时报错**：调用前先创建或检查集合。
2. **Embedding 模型维度不匹配**：不同模型产生的向量维度不同，不能混用。
3. **工具路径越界**：未做路径校验，导致读取敏感文件。

### 进阶阅读

1. Chroma 官方文档：Collections、Metadata、Where Filters。
2. LangChain VectorStore 文档。

### 本节检查清单

- [ ] 能用 Chroma 实现真实检索。
- [ ] 能实现多集合管理。
- [ ] 能注册并安全执行真实工具。
- [ ] 能保持 Retriever 和 Executor 的接口不变。

---

## 第 9 课：Phase 3 — Web UI 与 SSE 流式交互

### 本节目标

学完本节后，你能够：

- 用 FastAPI 实现 SSE 接口。
- 设计前端事件协议。
- 改造 Orchestrator 支持流式输出。
- 理解 SSE 与 WebSocket 的选型依据。

### 前置检查

- 已会用 FastAPI。
- 已理解 async generator。

### 关键概念

- **SSE（Server-Sent Events）**
- **StreamingResponse**
- **EventSource**
- **流式 Orchestrator**
- **前端状态管理**

### 深入讲解

#### 9.1 SSE 协议格式

```
event: agent_thought
data: {"agent": "planner", "content": "需要检索知识库"}

event: tool_call
data: {"tool": "search_docs", "arguments": {"query": "..."}}

event: final_answer
data: {"content": "...", "sources": [...]}
```

#### 9.2 FastAPI SSE 实现

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/chat")
async def chat(request: dict):
    async def event_stream():
        async for event in orchestrator.process_stream(request["query"]):
            yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

#### 9.3 流式 Orchestrator

```python
async def process_stream(self, query):
    yield {"type": "agent_thought", "data": {"agent": "orchestrator", "content": "开始处理"}}
    # ... 调度 Agent
    yield {"type": "final_answer", "data": {"content": answer}}
```

### 自测题

**Q1：SSE 和 WebSocket 在 Agent 系统中如何选型？**

A1：如果主要是服务器向客户端推送流式数据，SSE 更简单，且原生支持自动重连；如果需要双向实时通信（如语音输入、协同编辑），选 WebSocket。

**Q2：前端如何识别不同事件类型？**

A2：通过 EventSource 的 `event` 字段监听不同事件：`source.addEventListener('tool_call', handler)`。

**Q3：流式输出时如何保持会话状态？**

A3：通过 session_id 关联，Orchestrator 在流式生成过程中持续更新 SessionState，前端通过 `/sessions/{id}/messages` 拉取历史。

### 动手练习

#### 练习 9.1：最小 SSE 服务

**目标**：实现一个 FastAPI 接口，每秒推送一个数字，共 5 次。

**参考答案**：

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

@app.get("/stream")
async def stream():
    async def generator():
        for i in range(5):
            await asyncio.sleep(1)
            yield f"data: {i}\n\n"
    return StreamingResponse(generator(), media_type="text/event-stream")
```

#### 练习 9.2：前端接收 SSE

**目标**：写一段 HTML + JS，用 EventSource 接收 SSE 并显示在页面上。

**参考答案**：

```html
<div id="output"></div>
<script>
const source = new EventSource('/stream');
source.onmessage = (event) => {
    document.getElementById('output').innerHTML += event.data + '<br>';
};
</script>
```

### 常见错误

1. **SSE 被代理缓冲**：Nginx 等代理默认会缓冲响应，需配置 `X-Accel-Buffering: no`。
2. **async generator 提前退出**：未正确处理异常导致客户端收不到完整流。
3. **前端跨域问题**：FastAPI 需配置 CORS。

### 进阶阅读

1. FastAPI 官方 StreamingResponse 文档。
2. MDN：Server-Sent Events。
3. 论文或博客：LLM Streaming UI 设计模式。

### 本节检查清单

- [ ] 能实现 FastAPI SSE 接口。
- [ ] 能设计 SSE 事件协议。
- [ ] 能改造 Orchestrator 为 async generator。
- [ ] 能写出前端 EventSource 接收代码。

---

## 第 10 课：Phase 4 — 记忆持久化与上下文管理

### 本节目标

学完本节后，你能够：

- 设计 SQLite 数据表存储对话历史和 Agent Trace。
- 实现长期记忆查询。
- 管理上下文窗口，避免超长历史。
- 用用户反馈优化系统。

### 前置检查

- 已会 SQL 基础。
- 已理解上下文窗口限制。

### 关键概念

- **Session / Message / Trace**
- **SQLite**
- **Context Compression**
- **User Feedback Loop**

### 深入讲解

#### 10.1 数据表设计

```sql
CREATE TABLE sessions (
    id TEXT PRIMARY KEY,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    role TEXT,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES sessions(id)
);

CREATE TABLE agent_traces (
    id TEXT PRIMARY KEY,
    message_id TEXT,
    agent TEXT,
    thought TEXT,
    tool_calls TEXT,
    result TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 10.2 上下文压缩策略

1. **滑动窗口**：只保留最近 N 条消息。
2. **摘要压缩**：对早期消息做摘要，只保留摘要。
3. **token 预算**：按 token 数截断，优先保留近期和系统提示。

### 自测题

**Q1：为什么要持久化 Agent Trace？**

A1：Agent Trace 记录了 Agent 的思考过程和工具调用链，用于调试、评估、审计和后续优化。

**Q2：长期记忆和用户短期对话历史有什么区别？**

A2：短期对话历史是当前会话的消息序列；长期记忆是跨会话提取的用户偏好、事实和模式，需要在会话开始时加载。

**Q3：上下文压缩会损失信息吗？如何权衡？**

A3：会损失细节。权衡方式包括：保留系统提示、保留最近 N 轮完整对话、对早期对话做摘要、根据 token 预算动态调整。

### 动手练习

#### 练习 10.1：实现 SQLite 会话存储

**目标**：实现 `MemoryStore` 类，支持创建会话、添加消息、查询历史。

**参考答案框架**：

```python
import sqlite3

class MemoryStore:
    def __init__(self, db_path="memory.db"):
        self.conn = sqlite3.connect(db_path)
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                session_id TEXT,
                role TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def create_session(self, session_id, title):
        self.conn.execute("INSERT INTO sessions (id, title) VALUES (?, ?)", (session_id, title))
        self.conn.commit()

    def add_message(self, message_id, session_id, role, content):
        self.conn.execute(
            "INSERT INTO messages (id, session_id, role, content) VALUES (?, ?, ?, ?)",
            (message_id, session_id, role, content)
        )
        self.conn.commit()

    def get_messages(self, session_id, limit=50):
        cursor = self.conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
            (session_id, limit)
        )
        return cursor.fetchall()
```

### 常见错误

1. **并发写入冲突**：SQLite 默认文件锁，高并发需用连接池或 WAL 模式。
2. **消息顺序错误**：查询时未按时间排序。
3. **未限制历史长度**：导致上下文超限。

### 进阶阅读

1. SQLite 官方文档。
2. 论文：《MemGPT: Towards LLMs as Operating Systems》。

### 本节检查清单

- [ ] 能设计 SQLite 表结构。
- [ ] 能实现 MemoryStore 的基本 CRUD。
- [ ] 知道至少两种上下文压缩策略。
- [ ] 能理解 Agent Trace 的用途。

---

# 模块三：工程化、评估与求职

## 第 11 课：测试策略与 LLM 评估

### 本节目标

学完本节后，你能够：

- 为 Agent 系统编写单元测试、集成测试和评估测试。
- 用 mock 隔离 LLM 调用。
- 设计 LLM-as-a-Judge 评估流程。
- 解释传统指标（BLEU、ROUGE、BERTScore）的局限性。

### 前置检查

- 已会用 pytest。
- 已理解 mock 和 monkeypatch。

### 关键概念

- **pytest-asyncio**
- **Monkeypatch**
- **LLM-as-a-Judge**
- **BERTScore**
- **Regression Test**

### 深入讲解

#### 11.1 Agent 系统测试的分层

| 层级 | 范围 | 工具 | 示例 |
|---|---|---|---|
| 单元测试 | 单个函数/类 | pytest | MessageBus、SafeEvaluator |
| 集成测试 | 多个模块 | pytest-asyncio | Orchestrator 完整流程 |
| 评估测试 | 回答质量 | LLM / 规则 | test_cases.json |

#### 11.2 mock LLM 的原则

- 只 mock 不稳定或昂贵的依赖（LLM API）。
- 不 mock 被测模块自身的核心逻辑。
- mock 返回值要覆盖正常、异常、边界情况。

#### 11.3 LLM-as-a-Judge 设计

```python
def judge(query, answer, reference=None):
    prompt = f"""请从正确性、相关性、完整性、安全性四个维度评估以下回答。

问题：{query}
{'参考答案：' + reference if reference else ''}
回答：{answer}

请输出 JSON 格式评分。"""
    response = llm.chat([{"role": "user", "content": prompt}])
    return json.loads(response["content"])
```

### 自测题

**Q1：为什么 Agent 系统不能完全依赖单元测试？**

A1：因为 LLM 输出具有随机性，且 Agent 的行为是多个模块协作的结果。单元测试只能保证非 LLM 部分正确，整体质量需要评估测试。

**Q2：mock LLM 时要注意什么？**

A2：要模拟真实返回格式（content + tool_calls），覆盖成功、失败、异常格式，并确保被测模块的调用路径被覆盖。

**Q3：BERTScore 比 ROUGE 好在哪里？**

A3：ROUGE 基于 n-gram 重叠，只匹配字面；BERTScore 基于语义嵌入，能识别同义词和语义等价表达。

### 动手练习

#### 练习 11.1：为 MessageBus 写测试

**参考答案**：见第 6 课练习 6.2。

#### 练习 11.2：实现 LLM-as-a-Judge

**目标**：实现一个评估函数，对 Agent 回答从四个维度打分。

**参考答案框架**：

```python
import json

def evaluate_answer(query, answer, llm_client):
    prompt = f"""请评估以下回答，从 correctness、relevance、completeness、safety 四个维度打分（0-1），并给出 overall 分数。

问题：{query}
回答：{answer}

请只输出 JSON：{{"correctness": ..., "relevance": ..., "completeness": ..., "safety": ..., "overall": ..., "feedback": "..."}}"""
    response = llm_client.chat([{"role": "user", "content": prompt}])
    return json.loads(response["content"])
```

### 常见错误

1. **测试覆盖不到异步分支**：忘记用 `pytest.mark.asyncio`。
2. **LLM mock 返回格式不对**：导致被测模块解析失败。
3. **评估 prompt 太开放**：模型输出不合法 JSON，需要加格式约束。

### 进阶阅读

1. pytest-asyncio 官方文档。
2. 论文：《LLM-as-a-Judge: A Comprehensive Survey》。
3. BERTScore 官方仓库。

### 本节检查清单

- [ ] 能为异步代码写 pytest 测试。
- [ ] 会 mock LLM 调用。
- [ ] 能实现 LLM-as-a-Judge。
- [ ] 知道 BLEU/ROUGE/BERTScore 的适用场景。

---

## 第 12 课：工程化与部署

### 本节目标

学完本节后，你能够：

- 管理环境变量和敏感配置。
- 设计日志和监控方案。
- 实现错误处理和重试机制。
- 打包和部署 Python 应用。

### 前置检查

- 已会基础 Linux / 命令行。
- 已了解 Docker 基本概念。

### 关键概念

- **Environment Variables**
- **Structured Logging**
- **Retry with Backoff**
- **Docker**
- **CI/CD**

### 深入讲解

#### 12.1 配置管理

敏感信息：API Key、数据库密码。

```python
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "qwen")
    LLM_MODEL = os.getenv("LLM_MODEL", "qwen-turbo")
    DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
```

#### 12.2 重试机制

```python
import asyncio

async def retry_async(func, max_retries=3, delay=1.0):
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(delay * (2 ** attempt))  # 指数退避
```

### 自测题

**Q1：为什么 API Key 不能硬编码？**

A1：硬编码会泄露到版本控制中，存在安全风险；也不利于不同环境（开发/测试/生产）切换。

**Q2：指数退避（Exponential Backoff）有什么好处？**

A2：避免在服务端故障时集中重试造成雪崩，给服务端恢复时间。

**Q3：日志应该记录哪些内容？**

A3：Agent 行为、消息流转、工具调用、LLM 请求/响应、错误堆栈。但要避免记录 API Key、用户隐私数据。

### 动手练习

#### 练习 12.1：实现配置类

**目标**：实现一个从 .env 加载配置的 Config 类，支持默认值和类型校验。

#### 练习 12.2：实现重试装饰器

**目标**：为 LLM 调用加上带指数退避的重试。

**参考答案框架**：

```python
import functools
import asyncio

def retry(max_retries=3, delay=1.0):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    await asyncio.sleep(delay * (2 ** attempt))
        return wrapper
    return decorator

@retry(max_retries=3, delay=1.0)
async def call_llm(messages):
    ...
```

### 常见错误

1. **.env 文件提交到 git**：应加入 .gitignore。
2. **日志级别配置混乱**：生产环境不应输出 DEBUG。
3. **重试没有上限**：导致长时间阻塞。

### 进阶阅读

1. Python `logging` 模块官方文档。
2. Docker 官方文档。
3. GitHub Actions CI/CD 入门。

### 本节检查清单

- [ ] 能用 .env 管理配置。
- [ ] 能实现带退避的重试。
- [ ] 能设计合理的日志方案。
- [ ] 知道部署的基本流程。

---

## 第 13 课：简历包装与面试表达

### 本节目标

学完本节后，你能够：

- 用 STAR 法则描述项目。
- 准备 3 分钟项目口述。
- 回答 Agent / RAG / Function Calling 高频面试题。
- 根据岗位调整简历关键词。

### 前置检查

- 已完成 Nexus Phase 1 或更高阶段实现。

### 关键概念

- **STAR 法则**
- **技术关键词**
- **项目口述**
- **岗位匹配**

### 深入讲解

#### 13.1 STAR 法则

STAR = Situation（背景）+ Task（任务）+ Action（行动）+ Result（结果）。

#### 13.2 项目口述结构

1. 一句话定义项目（15 秒）。
2. 为什么做（30 秒）。
3. 技术架构和核心设计（90 秒）。
4. 挑战和解决（45 秒）。
5. 成果和收获（30 秒）。

### 自测题

**Q1：面试时如何解释"为什么用 Multi-Agent"？**

A1：职责分离，每个 Agent 专注单一任务；通过消息总线解耦，便于扩展；可以引入专门的评估 Agent 做质量闭环。

**Q2：如果面试官问"RAG 和微调有什么区别"，怎么回答？**

A2：RAG 是动态检索外部知识，不修改模型参数，适合知识频繁更新；微调是修改模型参数，让模型记住特定知识，适合固定领域风格，但成本高、更新慢。

### 动手练习

#### 练习 13.1：写 STAR 版项目描述

**目标**：用 STAR 法则写一段 Nexus 项目描述，不超过 300 字。

#### 练习 13.2：模拟面试

**目标**：对着镜子或录音，3 分钟口述 Nexus 项目。然后回听，找出表达不清的地方。

### 常见错误

1. **只说技术名词不讲解决什么问题**：面试官关心的是价值。
2. **夸大项目难度**：容易被追问穿帮。
3. **没有准备失败的应对**：要诚实说明哪些部分是 mock、哪些是真实实现。

### 进阶阅读

1. 《Cracking the Coding Interview》—— 面试技巧。
2. 目标公司面经。

### 本节检查清单

- [ ] 能用 STAR 写项目描述。
- [ ] 能 3 分钟口述项目。
- [ ] 能回答 10 个以上高频面试题。
- [ ] 能根据岗位调整简历关键词。

---

# 模块四：综合实战与持续提升

## 第 14 课：八周实战计划

### 本节目标

学完本节后，你能够：

- 制定并执行一个 8 周学习计划。
- 把 Nexus 从 Phase 1 推进到 Phase 4。
- 积累可展示的 GitHub 作品。

### 八周计划

| 周次 | 模块 | 重点任务 | 产出 |
|---|---|---|---|
| 1 | 基础 | LLM、Agent、RAG、Function Calling | 完成模块一 |
| 2 | 基础 | 工具安全、测试、评估 | 完成模块一练习 |
| 3 | Nexus Phase 1 | Message Bus、BaseAgent、六个 Agent | CLI 可运行 |
| 4 | Nexus Phase 2 | Chroma RAG、Tool Registry | 真实检索和工具 |
| 5 | Nexus Phase 3 | FastAPI + SSE、前端 | Web UI 可用 |
| 6 | Nexus Phase 4 | SQLite 记忆、评估优化 | 有长期记忆 |
| 7 | 工程化 | 日志、重试、部署、测试补全 | 可部署版本 |
| 8 | 求职 | 简历、口述、面试题 | 准备投递 |

### 持续提升

1. 每周至少提交一次代码到 GitHub。
2. 每周写一篇技术博客或学习笔记。
3. 每月复盘一次项目进展和面试准备。
4. 关注 LangChain、LlamaIndex、AutoGen 等框架更新。

---

# 附录

## 附录 A：术语表

| 术语 | 解释 |
|---|---|
| LLM | 大语言模型 |
| Token | 模型处理文本的最小单元 |
| Context Window | 上下文窗口 |
| Temperature | 采样温度，控制输出随机性 |
| Agent | 能感知、决策、行动的智能体 |
| ReAct | Reasoning + Acting |
| Function Calling | 模型调用外部函数的能力 |
| RAG | 检索增强生成 |
| Embedding | 文本向量化 |
| Vector DB | 向量数据库 |
| JSON Schema | JSON 数据结构描述规范 |
| AST | 抽象语法树 |
| SSE | Server-Sent Events |
| MCP | Model Context Protocol |
| TDD | 测试驱动开发 |
| LLM-as-a-Judge | 用 LLM 评估输出质量 |
| BERTScore | 基于语义嵌入的评估指标 |

## 附录 B：推荐资源

1. 论文：《Attention Is All You Need》
2. 论文：《ReAct: Synergizing Reasoning and Acting in Language Models》
3. 论文：《Retrieval-Augmented Generation for Large Language Models: A Survey》
4. 框架：LangChain、LlamaIndex、AutoGen、CrewAI
5. 文档：FastAPI、Chroma、pytest-asyncio、SQLite

## 附录 C：Nexus 核心文件索引

| 文件 | 作用 |
|---|---|
| `core/llm.py` | 统一 LLM Client |
| `core/message_bus.py` | 消息总线 |
| `core/agents/base.py` | Agent 基类 |
| `core/agents/orchestrator.py` | 协调器 |
| `core/agents/planner.py` | 规划器 |
| `core/agents/retriever.py` | 检索器 |
| `core/agents/executor.py` | 执行器 |
| `core/agents/summarizer.py` | 总结器 |
| `core/agents/critic.py` | 评估器 |
| `rag/loader.py` | 文档加载 |
| `rag/vectorstore.py` | 向量库 |
| `eval/evaluator.py` | 评估模块 |
| `app.py` | FastAPI Web 服务 |
| `main.py` | CLI 入口 |

---

## 写在最后

这份课程文档试图在"系统深度"和"可执行性"之间取得平衡。它不再是零散知识点的堆砌，而是按"概念 → 代码 → 验证 → 应用"的链条组织。

但文档本身不能替代动手。每完成一课，请确保：

1. 理解了关键概念。
2. 完成了代码实验室。
3. 能独立回答自测题。
4. 完成了至少一个动手练习。

只有经过这个闭环，知识才会真正变成你的能力。

祝你学习顺利。
