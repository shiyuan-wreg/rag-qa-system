# Nexus Phase 1 核心技术教学：Multi-Agent 内核从零理解

> 适用对象：胡智明（23 级软件工程本科）
> 对应项目：C:\Users\hzs17\Desktop\ai-demos
> 文档日期：2026-06-21
> 前置要求：已掌握 Python 基础、FastAPI 基础、了解 asyncio 概念

---

## 写在最前面：Phase 1 到底做了什么

Nexus 的 Phase 1 目标不是做一个能直接卖给用户的成品，而是搭建一个**可运行的 Multi-Agent 骨架**。你可以把它理解成盖房子时的"主体结构"：墙还没刷漆、家具还没摆，但房子的承重柱、楼板、水电管线已经通了。

Phase 1 完成时，系统具备以下能力：

1. 多个专业 Agent 可以互相发消息协作。
2. 用户输入一句话，Orchestrator 能调度 Planner 做计划、Retriever 查资料、Executor 调工具、Summarizer 生成回答、Critic 评估质量。
3. 所有 Agent 共享一套 LLM 调用接口，默认走通义千问，但以后可以无缝切换到 Kimi、DeepSeek、OpenAI。
4. 每个模块都有 pytest 测试保护，改代码时不怕把旧功能搞坏。
5. 有一个命令行入口，可以直接和 Agent 对话。

本教学文档会逐层讲解 Phase 1 里的核心技能点。读完之后，你应该能回答三个问题：

- 为什么要拆成多个 Agent？
- Agent 之间是怎么协作的？
- 每一块代码为什么这么写？

---

## 第一章：为什么需要多个 Agent

### 1.1 从"一个模型回答一切"到"多个专家分工"

很多同学第一次做 LLM 应用时，会写一个这样的函数：

```python
def ask_ai(question):
    response = llm.chat(question)
    return response
```

这叫做"单轮对话"或"直接问答"。它能回答简单问题，但遇到复杂任务就会暴露问题：

- 任务需要先查资料再计算，模型可能胡编。
- 任务需要调用外部工具，模型不会自动执行。
- 任务需要多步骤规划，模型可能漏步骤。
- 模型回答质量不稳定，没人检查它答得好不好。

**Agent 的核心思想是：让模型拥有"行动能力"和"反思能力"。**

但一个 Agent 既要规划、又要检索、又要执行、又要评估，代码会越来越复杂，而且容易互相干扰。于是人们把职责拆开，每个 Agent 只负责一件事，通过协作完成复杂任务。这就是 Multi-Agent 架构。

### 1.2 Nexus 的 Agent 分工

| Agent | 中文名 | 职责 | Phase 1 状态 |
|---|---|---|---|
| Orchestrator | 协调器 | 接收用户输入，调度其他 Agent，聚合结果 | 真实实现 |
| Planner | 规划器 | 把复杂任务拆成可执行步骤 | 真实实现 |
| Retriever | 检索器 | 从知识库检索相关文档 | mock 实现 |
| Executor | 执行器 | 调用外部工具执行具体操作 | mock 实现 |
| Summarizer | 总结器 | 综合中间结果，生成最终回答 | 真实实现 |
| Critic | 评估器 | 评估回答质量，判断是否需要重试 | 真实实现 |

### 1.3 为什么 Retriever 和 Executor 用 mock

这是 Phase 1 的一个重要取舍。

真实 RAG 需要：文档加载、文本分块、Embedding、向量数据库。真实工具需要：Tool Registry、安全沙箱、错误处理。这些都很重要，但把它们和 Multi-Agent 协作骨架混在一起做，会让问题复杂度翻倍。

所以 Phase 1 的做法是：

- 先让 Agent 之间的协作流程跑通。
- Retriever 和 Executor 返回假数据，但接口和真实版本一致。
- Phase 2 再把 mock 替换成真实实现，其他 Agent 不需要大改。

这叫"接口先行，实现后置"。面试时如果被问到"为什么先 mock"，你可以这样回答：

> "Phase 1 聚焦 Multi-Agent 协作架构的验证，Retriever 和 Executor 使用 mock 可以隔离 RAG 和 Tool Registry 的复杂度，确保消息总线、状态机、Agent 生命周期等核心机制稳定后，再逐步替换为真实实现。"

---

## 第二章：Agent 之间怎么说话：Message Bus

### 2.1 为什么不用函数直接调用

最简单的协作方式是函数调用：

```python
async def orchestrator(query):
    plan = await planner.plan(query)
    docs = await retriever.retrieve(plan)
    result = await summarizer.summarize(docs)
    return result
```

这种方式在 Agent 少、流程固定时没问题，但有两个致命缺点：

1. **耦合太强**：Orchestrator 必须知道每个 Agent 的函数名和参数。新增 Agent 时要改 Orchestrator。
2. **流程不灵活**：如果 Planner 发现某一步不需要检索，或者 Critic 要求重试，函数调用方式很难优雅处理。

**消息总线（Message Bus）** 是一种"发布-订阅"模式：每个 Agent 有一个自己的邮箱（队列），谁想给它发消息就往邮箱里扔；Agent 自己决定什么时候处理、怎么处理。Orchestrator 不需要知道 Agent 内部怎么实现，只需要知道它的"地址"（agent_id）。

### 2.2 Message 数据结构

所有 Agent 之间传递的消息都用同一个数据结构：

```python
@dataclass
class Message:
    task_id: str           # 一次用户请求的唯一标识
    sender: str            # 发送方，如 "orchestrator"
    recipient: str         # 接收方，如 "planner" 或 "broadcast"
    message_type: str      # 消息类型：task / result / plan / thought / critique / error
    payload: Dict[str, Any] # 具体数据，内容随消息类型变化
    message_id: str        # 消息唯一 id，自动生成的 UUID
    in_reply_to: Optional[str] = None  # 回复哪条消息
```

**思考题**：为什么 message_type 要用字符串而不是枚举（Enum）？

答案：字符串更灵活，方便扩展新类型；枚举虽然类型安全，但在动态扩展和日志阅读时不如字符串直观。Phase 1 选择简单优先。

### 2.3 MessageBus 的核心能力

```python
class MessageBus:
    def subscribe(self, agent_id: str) -> asyncio.Queue: ...
    async def publish(self, message: Message) -> None: ...
    async def send_and_wait(self, recipient, message, timeout) -> Message: ...
```

- **subscribe**：给某个 Agent 注册一个队列。如果队列不存在就自动创建。
- **publish**：把消息放到接收方的队列里。如果 recipient 是 "broadcast"，则发给所有订阅者。
- **send_and_wait**：先发消息，然后阻塞等待该任务的结果消息，支持超时。

### 2.4 send_and_wait 的实现难点

这是 MessageBus 里最 tricky 的一段代码。Orchestrator 给 Retriever 发消息后，Retriever 过一会儿会回传一个结果。但 Orchestrator 的队列里可能同时有多个任务的消息，怎么拿到自己那个？

实现思路：

1. Orchestrator 发消息前，先创建一个 `asyncio.Future`，并记录到 `_pending_futures[task_id]`。
2. 把消息 publish 出去。
3. Orchestrator 的消息循环（handle_message）收到结果时，根据 task_id 找到对应的 Future，把结果塞进去。
4. `send_and_wait` 等待这个 Future 完成。

```python
async def _send_and_wait(self, recipient, message, timeout):
    future = asyncio.get_event_loop().create_future()
    self._pending_futures[message.task_id] = future
    await self.bus.publish(message)
    try:
        result = await asyncio.wait_for(future, timeout=timeout)
        return result
    finally:
        self._pending_futures.pop(message.task_id, None)
```

**关键点**：`asyncio.Future` 是低层原语，比 `asyncio.Event` 更灵活，因为它可以承载结果对象。

### 2.5 为什么用 asyncio.Queue 而不是 Redis

Phase 1 用 `asyncio.Queue` 做内存消息队列，有三个原因：

1. **零部署**：不需要安装 Redis 或 RabbitMQ，个人电脑直接跑。
2. **代码清晰**：用 Python 原生队列，学习成本低。
3. **足够用**：Phase 1 只验证架构，没有高并发、持久化需求。

未来团队版要支持多实例部署时，只需要把 MessageBus 的实现换成基于 Redis 的，Agent 的调用代码不需要改。这就是"抽象层"的好处。

---

## 第三章：不被一家大模型绑定：LLM Client 抽象

### 3.1 为什么需要抽象层

国内大模型市场变化很快：通义千问、Kimi、DeepSeek、文心一言、智谱……每家 SDK 的调用方式略有不同。

如果代码里直接写：

```python
import dashscope
response = dashscope.Generation.call(...)
```

那么切换模型时，所有调用处都要改。更好的做法是封装一个统一的 `LLMClient`，对外提供一致的接口。

### 3.2 统一接口设计

```python
class LLMClient:
    def __init__(self, provider, model, api_key, base_url=None): ...
    def chat(self, messages, tools=None, stream=False) -> Dict[str, Any]: ...
```

`chat` 返回统一的字典：

```python
{
    "content": "模型生成的文本",
    "tool_calls": [
        {
            "id": "1",
            "function": {
                "name": "search_docs",
                "arguments": '{"query": "Python list"}'
            }
        }
    ]  # 如果没有工具调用，则为 None
}
```

### 3.3 适配通义千问和 OpenAI 格式

通义千问的原始返回：

```python
{
    "output": {
        "choices": [
            {"message": {"content": "...", "tool_calls": [...]}}
        ]
    }
}
```

OpenAI 兼容接口的返回：

```python
{
    "choices": [
        {"message": {"content": "...", "tool_calls": [...]}}
    ]
}
```

LLMClient 内部用 `_extract_content` 方法把两种格式统一成同一种结构。这样上层 Agent 完全不用关心底层是哪家模型。

### 3.4 环境变量切换模型

`.env` 文件示例：

```bash
# 默认用通义千问
LLM_PROVIDER=qwen
LLM_MODEL=qwen-turbo
DASHSCOPE_API_KEY=your-key

# 切换到 Kimi 时只改这几行
# LLM_PROVIDER=kimi
# LLM_MODEL=moonshot-v1-auto
# LLM_API_KEY=your-key
# LLM_BASE_URL=https://api.moonshot.cn/v1
```

业务代码不需要任何修改，这就是"配置驱动"。

---

## 第四章：所有 Agent 的公共骨架：BaseAgent

### 4.1 抽象基类的意义

每个 Agent 都有共同的需求：

- 一个唯一的 agent_id
- 订阅自己的消息队列
- 不断从队列里取消息并处理
- 发送消息时自动填充 sender
- 调用 LLM 时统一封装

把这些共性抽出来，就形成了 `BaseAgent`。

### 4.2 BaseAgent 的结构

```python
class BaseAgent:
    def __init__(self, agent_id: str, bus: MessageBus, llm: LLMClient):
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

    def stop(self):
        self._running = False

    @abstractmethod
    async def handle_message(self, message: Message) -> None:
        pass

    async def send_message(self, recipient, message_type, payload, task_id):
        msg = Message(
            task_id=task_id,
            sender=self.agent_id,
            recipient=recipient,
            message_type=message_type,
            payload=payload,
        )
        await self.bus.publish(msg)

    async def think(self, system_prompt, user_prompt, tools=None):
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return self.llm.chat(messages, tools=tools)
```

### 4.3 run 方法的细节

```python
async def run(self):
    self._running = True
    queue = self.bus.subscribe(self.agent_id)
    while self._running:
        try:
            message = await asyncio.wait_for(queue.get(), timeout=0.5)
            await self.handle_message(message)
        except asyncio.TimeoutError:
            continue
```

这里有两个设计点：

1. **用 `asyncio.wait_for` 设置 0.5 秒超时**：如果没有消息，队列会抛 `asyncio.TimeoutError`，循环继续检查 `_running`。这样 `stop()` 调用后，Agent 能在最多 0.5 秒内退出。
2. **不直接 `await queue.get()`**：如果直接 await，队列永久阻塞，`stop()` 后也无法结束循环。

### 4.4 think 方法的作用

`think` 是 BaseAgent 给子类提供的 LLM 调用便利方法。它把 system_prompt 和 user_prompt 组装成 messages，调用 `llm.chat()`，返回统一格式的结果。

子类 Agent 只需要关心"我要问模型什么问题"，不需要关心模型是通义千问还是 Kimi。

---

## 第五章：总指挥：Orchestrator Agent

### 5.1 Orchestrator 是系统的"大脑"

用户不会直接和 Planner、Retriever 打交道，用户只和 Orchestrator 对话。Orchestrator 的职责是：

1. 接收用户请求。
2. 决定任务类型：简单问答？多步骤任务？需要检索？需要执行工具？
3. 调用 Planner 生成执行计划。
4. 按顺序调用 Retriever / Executor 执行计划。
5. 调用 Summarizer 生成最终回答。
6. 调用 Critic 评估回答质量。
7. 如果需要，触发重试或补充信息。
8. 把最终结果返回给用户。

### 5.2 任务状态机

Orchestrator 用 `SessionState` 跟踪一次任务的完整生命周期：

```python
@dataclass
class SessionState:
    task_id: str
    query: str
    plan: List[Dict] = field(default_factory=list)
    documents: List[Dict] = field(default_factory=list)
    tool_results: List[Dict] = field(default_factory=list)
    answer: str = ""
    critique: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    # pending → planning → executing → summarizing → critiquing → done / error
```

状态机的好处：

- 代码结构清晰，每一步做什么一目了然。
- 方便日志记录和调试。
- 未来做 SSE 流式输出时，可以按状态推送事件。

### 5.3 process 方法的主流程

```python
async def process(self, query, timeout=60.0):
    task_id = str(uuid.uuid4())
    session = SessionState(task_id=task_id, query=query)

    # Step 1: Plan
    session.status = "planning"
    plan_msg = await self._send_and_wait("planner", Message(...))
    session.plan = plan_msg.payload.get("plan", [])

    # Step 2: Execute plan steps
    session.status = "executing"
    for step in session.plan:
        if step["agent"] == "retriever":
            ...
        elif step["agent"] == "executor":
            ...

    # Step 3: Summarize
    session.status = "summarizing"
    summary_msg = await self._send_and_wait("summarizer", Message(...))
    session.answer = summary_msg.payload.get("answer", "")

    # Step 4: Critique
    session.status = "critiquing"
    critique_msg = await self._send_and_wait("critic", Message(...))
    session.critique = critique_msg.payload
    session.status = "done"

    return {...}
```

### 5.4 为什么 Orchestrator 也用 BaseAgent

Orchestrator 既是"总指挥"，也是一个 Agent。它继承 BaseAgent，意味着：

- 它也能接收消息（比如 Critic 的 critique 消息）。
- 它能被统一启动和停止。
- 未来如果其他 Agent 需要回调 Orchestrator，机制是一样的。

### 5.5 _send_and_wait 的封装

Orchestrator 里没有直接调用 `self.bus.send_and_wait`，而是封装了一个 `_send_and_wait` 方法。原因是：

- MessageBus 的 `send_and_wait` 是基于队列轮询实现的，需要 Orchestrator 先订阅自己的队列。
- Orchestrator 用 `asyncio.Future` 实现更高效的等待，避免不断从队列里取消息再判断。

这是 Phase 1 里的一个优化点。理解了这一点，你就理解了"Future 比 Queue 更高效"的异步编程技巧。

---

## 第六章：任务拆解：Planner Agent

### 6.1 Planner 解决什么问题

复杂问题不能一步回答。比如用户问：

> "查一下 Python 列表和元组的区别，然后写个示例代码并运行验证。"

这个问题可以拆成三步：

1. 检索知识库中关于列表和元组区别的内容。
2. 调用 execute_python 工具运行示例代码。
3. 总结检索结果和运行结果，生成最终回答。

Planner 就是做这件事的 Agent。

### 6.2 输出格式：JSON Plan

Planner 的输出是一个 JSON 结构：

```json
{
  "steps": [
    {"step_id": 1, "agent": "retriever", "task": "检索 Python 列表和元组区别"},
    {"step_id": 2, "agent": "executor", "task": "调用 execute_python 运行示例代码"},
    {"step_id": 3, "agent": "summarizer", "task": "总结结果并生成回答"}
  ]
}
```

为什么要求模型输出 JSON？

- 机器容易解析，不需要用正则表达式去猜。
- Orchestrator 可以直接按步骤执行。
- 方便后续做可视化（在 Web UI 上展示执行计划）。

### 6.3 JSON 解析与失败降级

模型可能输出 Markdown 代码块（```json ... ```），也可能输出不合法的 JSON。Planner 的 `_parse_plan` 方法做了容错：

```python
def _parse_plan(self, content: str) -> list:
    try:
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        data = json.loads(content.strip())
        return data.get("steps", [])
    except json.JSONDecodeError:
        return [
            {"step_id": 1, "agent": "retriever", "task": "检索相关知识"},
            {"step_id": 2, "agent": "summarizer", "task": "总结生成回答"},
        ]
```

**设计思想**：即使模型不听话，系统也要能继续工作。解析失败时回退到一个保守的默认计划。

---

## 第七章：检索与执行：Retriever / Executor

### 7.1 Retriever：从知识库找答案

Retriever 的职责是根据 query 找到相关文档片段。Phase 1 用 mock，Phase 2 会接入 Chroma 向量数据库。

mock 实现的关键是：**接口和真实版本一致**。

```python
async def handle_message(self, message: Message):
    query = message.payload.get("query", "")
    documents = self._mock_retrieve(query)
    await self.send_message(
        recipient=message.sender,
        message_type="result",
        payload={"documents": documents, "query": query},
        task_id=message.task_id,
    )
```

返回的 document 结构：

```python
{
    "content": "列表是可变序列，支持增删改。",
    "source": "mock_notes/python_basics.md",
    "score": 0.95
}
```

真实 RAG 返回的也是这个结构，只是 score 是真实相似度分数。

### 7.2 Executor：调用外部工具

Executor 负责执行具体工具。Phase 1 实现了两个 mock 工具：

- `calculate`：基于 AST 的安全表达式计算。
- `read_file`：返回模拟文件内容。

`calculate` 工具值得重点看。它用 Python 的 `ast` 模块解析表达式，只允许常数和四则运算：

```python
def _calculate(self, expression: str) -> str:
    try:
        tree = ast.parse(expression, mode='eval')
        result = self._eval_node(tree.body)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

def _eval_node(self, node):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        ops = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
        }
        return ops[type(node.op)](
            self._eval_node(node.left),
            self._eval_node(node.right)
        )
    raise ValueError(f"Unsupported node: {type(node).__name__}")
```

**为什么不用 eval**：

`eval("__import__('os').system('rm -rf /')")` 可以直接执行危险操作。用 AST 白名单可以限制只能做数学运算，这是 Agent 工具安全的基础。

### 7.3 工具接口的标准化

每个工具返回统一结构：

```python
{
    "result": "工具执行结果或错误信息",
    "tool": "工具名",
    "args": {"参数": "值"}
}
```

这样 Orchestrator 和 Summarizer 不需要关心具体工具，只需要按统一格式处理。

---

## 第八章：总结与评估：Summarizer / Critic

### 8.1 Summarizer：把中间结果变成人话

Summarizer 的输入包括：

- 用户原始问题 query
- Retriever 返回的 documents
- Executor 返回的 tool_results

它的任务是把检索结果和工具结果整合成一段通顺、准确的自然语言回答。

```python
system_prompt = """你是一个总结专家。请根据检索到的文档和工具执行结果，生成准确、简洁的中文回答。
如果文档中没有相关内容，请明确说明。不要编造信息。"""
```

**关键 prompt 技巧**：

- 明确告诉模型"不要编造信息"，减少幻觉。
- 提供结构化上下文（文档 1、文档 2、工具结果 1），帮助模型定位信息来源。

### 8.2 Critic：回答质量评估

Critic 是系统的"自我检查"机制。它从四个维度打分：

| 维度 | 含义 | Phase 1 实现方式 |
|---|---|---|
| 正确性 | 是否有事实错误 | 关键词判断（是否包含"错误"、"不知道"） |
| 相关性 | 是否回答了用户问题 | 计算 query 关键词在回答中的匹配率 |
| 完整性 | 信息是否充分 | 根据回答长度打分 |
| 安全性 | 是否包含有害内容 | 黑名单关键词匹配 |

```python
def _rule_based_scores(self, query, answer):
    # 相关性
    query_keywords = set(re.findall(r"\b\w{2,}\b", query.lower()))
    matched = sum(1 for kw in query_keywords if kw in answer.lower())
    relevance = round(min(matched / len(query_keywords) * 1.5, 1.0), 2)

    # 完整性
    if len(answer) < 10:
        completeness = 0.0
    elif len(answer) > 100:
        completeness = 0.8
    else:
        completeness = 0.5

    # 安全性
    harmful = ["炸弹", "毒品", "杀人"]
    safety = 0.0 if any(kw in answer for kw in harmful) else 1.0

    # 综合分
    overall = round((correctness + relevance + completeness + safety) / 4, 2)
    return {...}
```

### 8.3 规则评估 vs LLM-as-a-Judge

Phase 1 用规则评估，因为：

- 不依赖额外 LLM 调用，成本低。
- 逻辑简单透明，容易调试。
- 能快速验证"评估闭环"这个机制。

Phase 4 会引入 **LLM-as-a-Judge**：用一个更强的模型给回答打分。规则评估和 LLM 评估可以互补：

- 规则评估：速度快、成本低、可解释。
- LLM 评估：更灵活、能理解语义、适合复杂场景。

---

## 第九章：测试驱动开发（TDD）

### 9.1 什么是 TDD

测试驱动开发的基本流程是：

1. 先写一个会失败的测试。
2. 运行测试，确认它确实失败了。
3. 写最少的代码让测试通过。
4. 运行测试，确认通过。
5. 重构代码，保持测试通过。

### 9.2 Phase 1 为什么用 TDD

Multi-Agent 系统涉及多个异步组件，很容易"看起来能跑，一改就坏"。TDD 的好处是：

- 每个 Agent 都有明确的行为契约。
- 改代码时有安全网，不怕破坏旧功能。
- 测试本身就是文档，告诉别人这个模块应该怎么用。

### 9.3 一个典型测试：Message Bus

```python
@pytest.mark.asyncio
async def test_publish_and_subscribe():
    bus = MessageBus()
    queue = bus.subscribe("retriever")

    msg = Message(
        task_id="t1",
        sender="orchestrator",
        recipient="retriever",
        message_type="task",
        payload={"query": "hello"},
    )

    await bus.publish(msg)
    received = await asyncio.wait_for(queue.get(), timeout=1.0)

    assert received.task_id == "t1"
    assert received.sender == "orchestrator"
    assert received.payload["query"] == "hello"
```

这个测试验证了：消息能被正确投递，接收方能拿到完整内容。

### 9.4 pytest-asyncio

Agent 都是异步函数，测试时需要 `pytest.mark.asyncio` 装饰器。它会自动把测试函数放到事件循环里执行。

```python
@pytest.mark.asyncio
async def test_planner_returns_steps():
    ...
```

### 9.5 mock 技巧：monkeypatch

测试 Planner 时，不想真的调用 LLM（会消耗 API 额度、速度慢、结果不稳定），所以用 monkeypatch 替换 `think` 方法：

```python
planner.think = async_mock_think

async def async_mock_think(system_prompt, user_prompt, tools=None):
    return {
        "content": '{"steps": [...]}',
        "tool_calls": None,
    }
```

这样测试只验证 Planner 的解析和消息发送逻辑，不依赖真实模型。

---

## 第十章：Phase 1 到 Phase 2 的演进路线

Phase 1 完成的是"骨架"，Phase 2 开始填"肉"。主要工作：

### 10.1 Retriever 接入真实 RAG

把 `core/agents/retriever.py` 里的 `_mock_retrieve` 替换成真实检索：

```
用户 query
    ↓
Embedding 模型向量化
    ↓
Chroma 向量相似度检索
    ↓
返回 Top-K 文档片段 + source + score
```

需要复用 `rag/` 目录下的 loader、splitter、vectorstore、retriever 模块。

### 10.2 Executor 接入 Tool Registry

把 mock 工具注册到 Tool Registry：

```python
registry.register(
    name="search_docs",
    description="检索知识库文档",
    parameters={...},
    handler=search_docs_handler,
)
```

Executor 根据工具名查找 handler，调用后返回结果。

### 10.3 新增真实工具

Phase 2 要实现：

- `search_docs`：封装 RAG 检索能力。
- `execute_python`：安全执行 Python 代码（基于 AST 沙箱）。
- `read_file`：读取指定文件。
- `list_files`：列出目录文件。

### 10.4 多集合知识库

Chroma 支持多个 collection。Phase 2 按来源划分：

- `notes`：个人笔记
- `code_docs`：代码仓库文档
- `web_articles`：网页文章
- `manual`：手动输入

Retriever Agent 需要根据 query 选择最合适的集合，或者多集合联合检索。

---

## 第十一章：面试常问问题

### 11.1 Agent 基础

**Q：什么是 Agent？和普通 LLM 应用有什么区别？**

> Agent 是能感知环境、做出决策并执行行动的系统。普通 LLM 应用只做文本生成，Agent 可以调用外部工具、规划多步骤任务、评估自身输出。

**Q：ReAct 是什么？**

> ReAct = Reasoning + Acting。模型在回答问题时交替进行"思考"和"行动"：先思考下一步该做什么，再调用工具，观察工具结果，再思考，直到得出结论。

### 11.2 架构设计

**Q：为什么要用消息总线而不是直接函数调用？**

> 消息总线解耦了 Agent 之间的依赖。新增 Agent 不需要改 Orchestrator，只需要给新 Agent 发消息。同时消息总线天然支持异步、广播、超时重试等机制。

**Q：Phase 1 为什么 Retriever 和 Executor 用 mock？**

> Phase 1 聚焦验证 Multi-Agent 协作架构。mock 可以隔离 RAG 和工具实现的复杂度，确保核心机制稳定后再替换真实实现，降低一次性改动过大的风险。

### 11.3 代码细节

**Q：BaseAgent 的 run 方法为什么要用 asyncio.wait_for？**

> 因为 `queue.get()` 会一直阻塞。用 `asyncio.wait_for(queue.get(), timeout=0.5)` 可以在没消息时超时返回，检查 `_running` 标志，从而响应 `stop()` 调用，优雅退出循环。

**Q：LLMClient 抽象层有什么好处？**

> 业务代码不依赖具体模型 SDK，切换模型只需改环境变量。同时统一了 Function Calling 的返回格式，上层 Agent 无需适配不同厂商的返回结构。

---

## 第十二章：附录：Windows / asyncio 踩坑记录

### 12.1 asyncio.get_event_loop() 弃用警告

旧代码可能写：

```python
loop = asyncio.get_event_loop()
```

Python 3.10+ 推荐在已有事件循环时用：

```python
loop = asyncio.get_running_loop()
```

否则会有 DeprecationWarning。

### 12.2 Windows 终端中文乱码

测试输出中如果包含中文字符串匹配，可能在 Windows Git Bash 或 cmd 中显示乱码。解决方法是：

- 测试中避免直接匹配中文字符串。
- 改用英文前缀（如 "Error:"）或返回值特征判断。

### 12.3 子 Agent 在 worktree 外提交

用 Claude subagent 开发时，默认工作目录可能不是 worktree。如果 subagent 在原始 repo 提交，会导致 master 和 worktree 同时出现 commit。

**解决方法**：

- 每次派 subagent 前，明确要求它在 worktree 中执行。
- 开发完成后用 `git worktree list` 确认当前目录。
- 合并前检查 commit 是否只在 worktree 分支上。

---

## 第十三章：给你的练习建议

光看不练掌握不深。建议按下面顺序自己动手：

1. **自己重写一遍 MessageBus**：不参考项目代码，独立实现 subscribe / publish / send_and_wait。
2. **给 BaseAgent 加一个日志功能**：每次收到消息时打印 sender 和 message_type。
3. **扩展 Executor**：新增一个 `get_weather` mock 工具，测试 Orchestrator 调用它。
4. **修改 Planner prompt**：让它输出更详细的计划，包含每个步骤的输入输出。
5. **给 Critic 加维度**：增加"可读性"评分，根据句子长度和标点判断。

每完成一个练习，跑一遍 `pytest`，确保没破坏现有功能。

---

## 第十四章：总结

Phase 1 的核心不是把功能做全，而是建立四个能力：

1. **Multi-Agent 协作能力**：多个 Agent 通过消息总线分工协作。
2. **抽象层设计能力**：LLM Client、BaseAgent、工具接口，让系统可扩展。
3. **状态管理能力**：SessionState 跟踪任务生命周期， Orchestrator 调度有序。
4. **测试保护能力**：每个模块有测试，改代码有安全网。

理解了这四点，Phase 2 的真实 RAG、Phase 3 的 Web UI、Phase 4 的记忆持久化，都是在骨架上长肉，而不是从零开始。

如果你能把这套东西在面试里讲清楚，已经超越大多数只会调用 ChatGPT API 的同学了。

---

## 推荐延伸阅读

1. 《ReAct: Synergizing Reasoning and Acting in Language Models》—— Agent 决策经典论文。
2. LangChain 官方文档的 Agent 和 Tool 章节。
3. FastAPI 官方 SSE 示例（为 Phase 3 做准备）。
4. Chroma 文档的 Collections 和 Metadata 部分（为 Phase 2 做准备）。
5. pytest-asyncio 官方文档（为持续写测试做准备）。
