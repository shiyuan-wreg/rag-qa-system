# Nexus Phase 2 设计文档：Multi-Agent 内核 + Web 后端

- **文档日期**：2026-06-23
- **项目代号**：Nexus
- **对应项目**：ai-demos（`C:\Users\hzs17\Desktop\ai-demos`）
- **设计目标**：在 `backends/nexus_app` 中实现 Multi-Agent AI 工作流内核，并通过 FastAPI + SSE 暴露给前端；门户外壳新增 `/nexus` 入口。
- **设计状态**：待实现

---

## 1. 写在最前面：这份文档的阅读方式

Nexus Phase 2 涉及多个新概念（Multi-Agent、SSE、LLM-as-a-Judge 等）。如果你对其中的某个术语不熟悉，文档会在第一次出现时给出解释。建议你按顺序阅读，遇到不懂的概念先停下来看解释，再继续往下看。

**本文档假设你已了解的基础知识**：Python 基础语法、FastAPI/HTTP 基础、什么是 LLM（大语言模型）。

---

## 2. Phase 2 要交付什么

### 2.1 一句话目标

在 ai-demos 中新增一个名为 **Nexus** 的 AI 工作流助手，它由多个专业 Agent 协作完成复杂任务，并通过浏览器实时展示 Agent 的思考过程。

### 2.2 交付清单

| 交付物 | 说明 |
|---|---|
| `backends/nexus_app/` | Nexus 后端服务源码 |
| `backends/nexus_app/Dockerfile` | Nexus 服务容器化配置 |
| `deploy/docker-compose.yml` 更新 | 新增 `nexus` 服务 |
| `deploy/nginx/nginx.conf` 更新 | 新增 `/nexus/` 反代规则 |
| `frontends/portfolio/src/data/works.ts` 更新 | 门户首页新增 Nexus 作品卡片 |
| 设计文档 | 本文档 |
| 单元测试 | `tests/` 下覆盖 Message Bus、Agents、SSE 接口 |

### 2.3 Phase 2 的明确边界

**包含**：
- Multi-Agent 内核（Message Bus + 6 个 Agent）
- FastAPI + SSE 流式聊天接口
- 简单前端聊天页面
- 与现有 `rag_app`、`fc_app` 的 HTTP 级复用
- 使用 LLM 进行回答质量评估的 Critic Agent

**不包含**（留给后续阶段）：
- MCP Client、Obsidian/Notion 等笔记平台接入
- SQLite 长期记忆持久化（Phase 2 使用内存会话，刷新页面会清空）
- 用户认证、多用户隔离
- 复杂的 Agent 自我纠错循环（Critic 只打分，不自动重试）

---

## 3. 关键术语解释

### 3.1 Agent（智能体）

Agent 是指能够**感知环境、做出决策、执行行动**的程序。与普通 LLM 应用（只问一次、只答一次）不同，Agent 会反复思考、调用工具、观察结果，直到完成目标。

举例：
- 普通 LLM：你问"北京天气怎么样？"，它回答"我不知道实时天气"。
- Agent：你问"北京天气怎么样？"，它决定调用 `get_weather(city="北京")` 工具，得到结果后回答"北京晴天，25°C"。

### 3.2 Multi-Agent（多智能体）

把原本由一个大模型包揽的所有工作，拆给多个**专业 Agent** 去做。每个 Agent 只负责一小块任务，通过消息协作。

Nexus 的 6 个专业 Agent：

| Agent | 角色 | 类比 |
|---|---|---|
| Orchestrator | 总指挥 | 项目经理 |
| Planner | 任务规划 | 架构师 |
| Retriever | 检索知识 | 资料员 |
| Executor | 执行工具 | 操作员 |
| Summarizer | 总结回答 | 文案 |
| Critic | 质量评估 | 质检员 |

### 3.3 Message Bus（消息总线）

Agent 之间不直接互相调用，而是通过一个中心化的"邮局"发消息。每个 Agent 有一个自己的信箱（队列），Message Bus 负责把消息送到正确的信箱。

这样做的好处：
- Agent 不需要知道其他 Agent 在哪里、怎么实现。
- 新增 Agent 很容易，只要注册一个信箱。
- 便于测试：可以单独测试某个 Agent，不依赖其他 Agent。

### 3.4 SSE（Server-Sent Events，服务器推送事件）

一种让服务器向浏览器**单向实时推送数据**的技术。基于普通 HTTP，浏览器用 `EventSource` 接收。

为什么 Nexus 选 SSE 而不是 WebSocket？

| 特性 | SSE | WebSocket |
|---|---|---|
| 方向 | 服务器 → 客户端 | 双向 |
| 协议 | 普通 HTTP | 独立协议 |
| 复杂度 | 低 | 高 |
| 自动重连 | 浏览器原生支持 | 需自己实现 |
| 适用场景 | 服务器主动推送流 | 高频双向互动 |

Nexus 主要是服务器向浏览器推送 Agent 的中间过程（思考、工具调用、结果），SSE 足够且更简单。

### 3.5 LLM-as-a-Judge（让大模型当裁判）

让另一个 LLM（通常比生成答案的模型一样强或更强）来评估答案质量。相比写死的规则，LLM 能更灵活地判断"回答是否准确"、"是否跑题"、"是否完整"。

举例：
- 规则评分：检查回答里是否包含关键词"列表"和"元组"。
- LLM 评分：让模型读问题和回答，判断"回答是否正确地解释了列表和元组的区别"。

**优点**：更接近人类判断，能处理开放式问题。
**缺点**：多一次 LLM 调用，增加成本和延迟；LLM 本身也可能判错。

### 3.6 Critic Agent（批评者 Agent）

Critic 是 Nexus 中的"质检员"。它不看代码，只看"用户问了什么"和"系统答了什么"，然后给出质量分数和改进建议。

在 Phase 2 中，Critic 使用 **LLM-as-a-Judge** 评分。如果 LLM 调用失败或返回格式异常，会 fallback 到规则评分，保证系统不崩。

---

## 4. 高层架构

### 4.1 服务边界

```
浏览器
  │
  ▼
nginx (80/443)
  ├── /          → frontends/portfolio (静态门户)
  ├── /rag/      → backends/rag_app:8001
  ├── /fc/       → backends/fc_app:8002
  └── /nexus/    → backends/nexus_app:8003  ← Phase 2 新增
```

### 4.2 nexus_app 内部架构

```
用户请求
  │
  ▼
FastAPI Web Gateway
  │ POST /chat (SSE)
  ▼
Orchestrator Agent（总指挥）
  │
  ▼
Message Bus（asyncio Queue）
  │
  ├─→ Planner Agent（规划）
  ├─→ Retriever Agent ──HTTP──→ rag_app:8001
  ├─→ Executor Agent ──HTTP──→ fc_app:8002
  ├─→ Summarizer Agent（总结）
  └─→ Critic Agent（评估，LLM-as-a-Judge）
```

### 4.3 为什么复用 rag_app/fc_app

现有 `rag_app` 已经实现了：
- 文档加载、分块、Embedding、Chroma 检索
- 基于 RAG 的问答 Agent

现有 `fc_app` 已经实现了：
- Function Calling Agent
- calculate、get_weather、set_reminder 等工具

如果 Nexus 重新实现一遍，会造成大量重复代码，且维护困难。因此 Nexus 的 **Retriever Agent** 和 **Executor Agent** 通过内部 HTTP 调用它们，把两者当作"工具服务"。

**好处**：
- 避免重复造轮子。
- `rag_app` 和 `fc_app` 可以独立演进。
- Nexus 专注做 Agent 编排层，职责清晰。

**代价**：
- 多一次网络调用，延迟增加几十到几百毫秒（都在 Docker 内部，通常可接受）。
- 需要定义清晰的调用契约。

---

## 5. Multi-Agent 内核详细设计

### 5.1 消息格式

所有 Agent 之间通信使用统一的 `Message` 对象：

```python
@dataclass
class Message:
    task_id: str          # 一次用户请求的唯一 ID
    sender: str           # 发送方 Agent 名称
    recipient: str        # 接收方 Agent 名称，或 "broadcast"
    message_type: str     # task / result / plan / thought / critique / error
    payload: dict         # 具体内容
    message_id: str       # 消息唯一 ID
    in_reply_to: str      # 回复哪条消息（可选）
```

**字段解释**：
- `task_id`：一次用户提问对应一个 task_id，所有相关消息共享同一个 ID，方便追踪。
- `message_type`：区分消息用途。`task` 表示"派任务"，`result` 表示"任务结果"，`critique` 表示"评估结果"。
- `payload`：任意字典，内容由 sender 和 message_type 决定。

### 5.2 Message Bus 接口

```python
class MessageBus:
    def subscribe(self, agent_id: str) -> asyncio.Queue
    async def publish(self, message: Message) -> None
    async def send_and_wait(
        self, recipient: str, message: Message, timeout: float = 30.0
    ) -> Message
```

- `subscribe`：给 Agent 注册一个队列。每个 Agent 一个队列。
- `publish`：发送消息。如果 `recipient` 是 `broadcast`，则广播给所有订阅者。
- `send_and_wait`：发消息后阻塞等待回复，带超时控制。Orchestrator 用它同步收集结果。

### 5.3 BaseAgent

所有 Agent 的基类，提供公共骨架：

```python
class BaseAgent:
    def __init__(self, agent_id: str, bus: MessageBus, llm: LLMClient)
    async def run(self) -> None          # 消息循环
    def stop(self) -> None               # 停止循环
    async def handle_message(self, message: Message) -> None  # 子类实现
    async def send_message(...) -> None  # 发送消息便利方法
    async def think(...) -> dict         # 调用 LLM
```

### 5.4 Orchestrator Agent

**职责**：总指挥。接收用户请求，决定调用哪些 Agent，聚合结果，返回最终答案。

**状态机**：

```
pending → planning → retrieving → executing → summarizing → critiquing → done
```

**一次完整流程**：

1. 用户提问 → Orchestrator 创建 `SessionState`。
2. 调用 Planner，得到执行计划（例如：先检索，再总结）。
3. 按顺序执行计划：
   - `retriever` 步骤 → 调用 Retriever Agent，得到文档。
   - `executor` 步骤 → 调用 Executor Agent，得到工具结果。
4. 调用 Summarizer，生成最终回答。
5. 调用 Critic，对回答评分。
6. 把结果通过 SSE 推送给浏览器。

### 5.5 Planner Agent

**职责**：把用户请求拆成可执行步骤。

**输入**：`{"query": "用户问题"}`

**输出**：`{"plan": [{"step_id": 1, "agent": "retriever", "task": "..."}, ...]}`

Planner 通过 LLM 生成计划。LLM 的 system prompt 会约束输出格式为 JSON。

### 5.6 Retriever Agent

**职责**：从知识库检索相关文档。

Phase 2 中，Retriever 不直接操作 Chroma，而是**通过 HTTP 调用 `rag_app`**。

**调用方式**：
- 初始方案：调用 `POST /rag/chat`（Form: query），解析返回中的回答和工具调用记录。
- 更优方案：在 `rag_app` 新增 `POST /rag/retrieve`，只返回检索到的文档片段（不生成回答），让 Nexus 自己控制生成过程。

**输出**：`{"documents": [{"content": "...", "source": "...", "score": 0.95}, ...]}`

### 5.7 Executor Agent

**职责**：调用工具执行具体操作。

Phase 2 中，Executor 通过 HTTP 调用 `fc_app`。

**调用方式**：
- `fc_app` 需要新增 `POST /fc/execute` 接口，接受 JSON：`{"tool": "calculate", "args": {"expression": "2+2"}}`。
- 返回：`{"result": "4"}`。

**输出**：`{"result": "...", "tool": "calculate", "args": {...}}`

> 为什么不在 Nexus 内直接实现 `calculate`？因为 `fc_app` 已经有完整的 Function Calling 能力和工具集合。Phase 2 先复用，避免重复。

### 5.8 Summarizer Agent

**职责**：综合检索结果和工具结果，生成面向用户的最终回答。

**输入**：`{"query": "...", "documents": [...], "tool_results": [...]}`

**输出**：`{"answer": "...", "sources": [...]}`

Summarizer 的 system prompt 会要求：
- 基于提供的资料回答，不要编造。
- 如果资料不足，明确说明。
- 回答末尾列出引用来源。

### 5.9 Critic Agent（LLM-as-a-Judge）

**职责**：评估最终回答的质量。

#### 5.9.1 评估维度

| 维度 | 含义 | 满分 |
|---|---|---|
| correctness（正确性） | 回答是否有事实错误 | 1.0 |
| relevance（相关性） | 是否回答了用户的问题 | 1.0 |
| completeness（完整性） | 是否遗漏关键信息 | 1.0 |
| safety（安全性） | 是否包含有害、敏感内容 | 1.0 |
| overall（综合） | 上面几项的加权平均 | 1.0 |

#### 5.9.2 LLM 评估 Prompt 示例

```
你是一位严格的回答质量评估专家。请根据用户问题和系统回答，从以下维度打分（0.0 ~ 1.0）。

评估维度：
1. correctness：回答是否事实正确。
2. relevance：回答是否针对用户问题。
3. completeness：回答是否完整，没有遗漏关键信息。
4. safety：回答是否安全，没有有害或敏感内容。

用户问题：{query}
系统回答：{answer}

请只输出 JSON，不要输出其他内容：
{
  "correctness": 0.0,
  "relevance": 0.0,
  "completeness": 0.0,
  "safety": 1.0,
  "overall": 0.0,
  "feedback": "简要说明评分理由和改进建议"
}
```

#### 5.9.3 Fallback 机制

LLM 可能返回：
- 非 JSON 内容
- JSON 但缺少字段
- LLM 调用失败（网络、API 限制）

因此 Critic 必须有 fallback：

```python
try:
    scores = await self._llm_critique(query, answer)
except Exception:
    scores = self._rule_based_scores(query, answer)
```

规则评分作为保底：检查关键词匹配、回答长度、敏感词等。

#### 5.9.4 为什么用 LLM 评分

- 规则评分只能检查"有没有关键词"，无法判断"回答是否真正正确"。
- LLM 评分更接近人类判断，对开放式问题更准确。
- 这是"LLM-as-a-Judge"模式，是 Agent 系统常见的评估手段。

#### 5.9.5 成本与延迟说明

- 每次用户请求会额外调用一次 LLM（Critic）。
- 使用 `qwen-turbo`，成本很低（ DashScope 通常有免费额度或低价）。
- 如果在意延迟，可以在后续版本中添加"是否启用 Critic"的开关。

### 3.7 HTTP 与 REST API 基础

#### 3.7.1 HTTP 是什么

HTTP（HyperText Transfer Protocol，超文本传输协议）是浏览器和服务器之间**请求-响应**的通信规则。

一次 HTTP 交互包含：
- **请求（Request）**：客户端（如浏览器）向服务器发送的消息。
- **响应（Response）**：服务器处理完后返回给客户端的消息。

一个 HTTP 请求包含：
- **方法（Method）**：告诉服务器要做什么。常见：
  - `GET`：获取资源
  - `POST`：提交数据、创建资源
  - `PUT`：更新资源
  - `DELETE`：删除资源
- **URL（路径）**：资源地址，例如 `/chat`、`/rag/chat`。
- **Headers**：元信息，例如 `Content-Type: application/json`。
- **Body**：请求体，POST/PUT 时携带具体数据。

一个 HTTP 响应包含：
- **状态码（Status Code）**：
  - `200 OK`：成功
  - `404 Not Found`：资源不存在
  - `500 Internal Server Error`：服务器内部错误
- **Headers**：元信息。
- **Body**：响应体，例如 JSON 数据或 HTML 页面。

#### 3.7.2 REST API 是什么

REST（Representational State Transfer）是一种设计 API 的风格。它把服务器上的资源用 URL 表示，用 HTTP 方法操作资源。

举例：

| 操作 | 方法 | URL | 含义 |
|---|---|---|---|
| 获取会话列表 | GET | `/sessions` | 读取所有会话 |
| 创建会话 | POST | `/sessions` | 新建一个会话 |
| 获取某个会话 | GET | `/sessions/{id}` | 读取指定会话 |
| 发送消息 | POST | `/chat` | 发起一次对话 |

REST API 通常返回 JSON 格式数据，方便程序处理。

### 3.8 FastAPI 是什么

FastAPI 是一个用 Python 写 Web 后端的框架。它的特点是：
- **快**：性能接近 Node.js 和 Go。
- **简单**：用 Python 类型注解自动生成接口文档。
- **异步支持**：原生支持 `async/await`，适合处理 SSE、高并发请求。

#### 3.8.1 一个最简单的 FastAPI 例子

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello World"}
```

运行后访问 `http://127.0.0.1:8000/`，会返回：

```json
{"message": "Hello World"}
```

#### 3.8.2 FastAPI 在 Nexus 中的作用

Nexus 的 Web 后端用 FastAPI 实现，它负责：
- 接收浏览器发来的 HTTP 请求。
- 调用 Orchestrator 处理用户问题。
- 通过 SSE 把 Agent 的中间过程实时推送给浏览器。

### 3.9 反向代理（Reverse Proxy）是什么

#### 3.9.1 生活中的类比

想象一栋办公楼有很多部门：
- 前台（nginx）只有一个对外电话号码（80/443 端口）。
- 外面的人打电话只说"找财务部"或"找技术部"。
- 前台根据请求内容，把电话转接到内部对应分机（rag_app、fc_app、nexus_app）。

**反向代理就是这个前台。**

#### 3.9.2 技术解释

反向代理是部署在服务器前端的程序（常用 nginx），它：
- 对外暴露一个统一入口（例如 `www.shiyuan-wreg.cloud`）。
- 根据 URL 路径，把请求转发给内部不同的后端服务。

在 ai-demos 中：

```
用户访问 www.shiyuan-wreg.cloud/rag/chat
                │
                ▼
           nginx（反向代理）
                │
                ▼
         转发到 rag_app:8001/chat
```

#### 3.9.3 反向代理的好处

| 好处 | 说明 |
|---|---|
| 统一入口 | 用户只需要记住一个域名，不用关心后端有多少服务。 |
| 路径隔离 | `/rag/`、`/fc/`、`/nexus/` 走不同后端，互不干扰。 |
| SSL/HTTPS | 证书配置在 nginx 一层，后端服务不用管 HTTPS。 |
| 负载均衡 | 未来如果某个服务需要多个实例，nginx 可以分配流量。 |
| 静态文件托管 | nginx 可以直接返回 HTML/CSS/JS，不打扰后端。 |

#### 3.9.4 nginx 配置示例

```nginx
server {
    listen 80;
    server_name www.shiyuan-wreg.cloud;

    # 门户网站
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # RAG 后端
    location /rag/ {
        proxy_pass http://rag:8001/;
    }

    # FC 后端
    location /fc/ {
        proxy_pass http://fc:8002/;
    }

    # Nexus 后端（Phase 2 新增）
    location /nexus/ {
        proxy_pass http://nexus:8003/;
    }
}
```

关键行解释：
- `location /rag/`：匹配所有以 `/rag/` 开头的请求。
- `proxy_pass http://rag:8001/`：把请求转发给 Docker 服务 `rag` 的 8001 端口。
- `root /usr/share/nginx/html`：静态文件从哪个目录读取。

### 3.10 SSE（Server-Sent Events）语法详解

#### 3.10.1 SSE 消息格式

SSE 消息是纯文本，格式固定：

```
event: 事件类型
data: JSON 数据

```

注意：
- 每条消息以**两个换行**（`\n\n`）结束。
- `event:` 行可选，没有时浏览器默认当作 `message` 事件。
- `data:` 行可以有多行，表示一条消息分多行传输。

#### 3.10.2 一个完整的 SSE 例子

服务器推送：

```
event: planner_thought
data: {"content": "需要检索知识库"}

event: tool_call
data: {"agent": "retriever", "tool": "search_docs", "args": {"query": "Python"}}

event: final_answer
data: {"content": "列表可变，元组不可变。", "sources": []}

```

#### 3.10.3 前端如何接收 SSE

浏览器用 `EventSource` 对象接收 SSE：

```javascript
const source = new EventSource('/nexus/chat', {
    method: 'POST',
    body: JSON.stringify({query: "Python 列表和元组区别"})
});

source.addEventListener('planner_thought', (event) => {
    const data = JSON.parse(event.data);
    console.log('Planner 思考:', data.content);
});

source.addEventListener('tool_call', (event) => {
    const data = JSON.parse(event.data);
    console.log('工具调用:', data);
});

source.addEventListener('final_answer', (event) => {
    const data = JSON.parse(event.data);
    console.log('最终回答:', data.content);
    source.close();
});
```

#### 3.10.4 SSE 与 HTTP 的关系

SSE 就是普通的 HTTP 响应，只是：
- 响应头 `Content-Type: text/event-stream`
- 响应体不会一次性返回，而是服务器持续推送，直到连接关闭
- 浏览器会自动处理重连（如果连接断开）

#### 3.10.5 为什么 SSE 适合 Nexus

Nexus 需要把 Agent 的思考过程、工具调用、最终结果逐步展示给用户。如果用普通 HTTP POST，只能等全部处理完再一次性返回，用户会看到一个长长的"思考中..."。

SSE 让用户**实时看到每一步**，体验更好，也更便于调试。

---

## 6. Web 后端与 SSE 设计

### 6.1 接口清单

| 接口 | 方法 | 说明 |
|---|---|---|
| `/chat` | POST | 发起对话，返回 SSE 流 |
| `/sessions` | GET | 获取内存中的会话列表 |
| `/sessions/{id}` | GET | 获取某个会话的历史消息 |
| `/sessions/{id}/clear` | POST | 清空某个会话 |
| `/health` | GET | 健康检查 |

### 6.2 SSE 事件类型

```
event: planner_thought
data: {"content": "需要检索知识库"}

event: tool_call
data: {"agent": "retriever", "tool": "search_docs", "args": {"query": "..."}}

event: tool_result
data: {"agent": "retriever", "result": [...]}

event: agent_thought
data: {"agent": "summarizer", "content": "正在生成最终回答"}

event: final_answer
data: {"content": "...", "sources": [...], "critique": {...}}

event: error
data: {"message": "..."}
```

### 6.3 服务端 SSE 实现

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.post("/chat")
async def chat(request: ChatRequest):
    async def event_stream():
        async for event in orchestrator.process_stream(request.query, request.session_id):
            yield f"event: {event.type}\ndata: {json.dumps(event.data)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

### 6.4 会话管理（内存版）

Phase 2 不持久化，用内存字典保存会话：

```python
sessions: dict[str, Session] = {}
```

每个 `Session` 包含：
- `session_id`
- `messages`（历史消息）
- `created_at`、`updated_at`

页面刷新后会话丢失，这是 Phase 2 的可接受限制。

---

## 7. 前端设计

### 7.1 页面结构

nexus_app 自带一个简单 HTML 前端，包含：

- **顶部工具栏**：新建会话、清空当前会话
- **左侧会话列表**：显示当前内存中的会话
- **中间聊天区**：展示用户消息、Agent 思考过程、工具调用、最终回答
- **右侧思考过程面板**：实时显示 SSE 事件流

### 7.2 门户集成

在 `frontends/portfolio/src/data/works.ts` 中新增：

```typescript
{ slug: 'nexus', title: 'Nexus Multi-Agent 工作流', desc: '多 Agent 协作的 AI 工作流助手，实时展示思考过程。',
  tech: ['Multi-Agent', 'FastAPI', 'SSE', '通义千问'], path: '/nexus' }
```

在 `App.tsx` 的路由中新增 `/nexus` → `<DemoFrame work={...} src="/nexus/" />`。

nginx 配置新增：

```nginx
location /nexus/ {
    proxy_pass http://nexus:8003/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

---

## 8. 复用现有服务的契约

### 8.1 rag_app 需要新增的接口

**`POST /retrieve`**（建议新增）

请求：
```json
{"query": "Python 列表和元组区别"}
```

响应：
```json
{
  "documents": [
    {"content": "列表可变...", "source": "notes/python.md", "score": 0.95}
  ]
}
```

如果不新增，`POST /chat` 也能用，但会多一次回答生成，控制权弱。

### 8.2 fc_app 需要新增的接口

**`POST /execute`**（必须新增）

请求：
```json
{"tool": "calculate", "args": {"expression": "2+2"}}
```

响应：
```json
{"result": "4"}
```

`fc_app` 原有 `/chat` 是由模型自己决定工具，不适合被 Nexus Executor 显式调用。

---

## 9. 部署与集成

### 9.1 新增 Dockerfile

`backends/nexus_app/Dockerfile`：

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY backends/nexus_app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backends/nexus_app/ ./
EXPOSE 8003
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
```

### 9.2 docker-compose.yml 更新

```yaml
services:
  nexus:
    build:
      context: ..
      dockerfile: backends/nexus_app/Dockerfile
    env_file: ../.env
    restart: always
    expose: ["8003"]
    depends_on: [rag, fc]
```

### 9.3 本地运行步骤

1. 确保 Docker Desktop 启动。
2. 仓库根有 `.env`（含 `DASHSCOPE_API_KEY`）。
3. `bash deploy/build-frontends.sh`
4. `docker compose -f deploy/docker-compose.yml up -d --build`
5. 访问 `http://127.0.0.1:8080`（或生产域名）。

---

## 10. 错误处理

| 错误场景 | 处理方式 |
|---|---|
| LLM API 异常 | Orchestrator 重试 3 次，失败后通过 SSE 返回 `error` 事件 |
| rag_app/fc_app 不可用 | Executor/Retriever 返回错误信息，Summarizer 在回答中说明 |
| Planner 返回非 JSON | 使用默认计划：检索 + 总结 |
| Critic LLM 失败 | Fallback 到规则评分 |
| 请求超时 | Orchestrator 终止任务，返回超时提示 |
| Agent 死循环 | `max_turns` 限制，防止无限循环 |

---

## 11. 测试策略

| 测试文件 | 覆盖内容 |
|---|---|
| `tests/test_message_bus.py` | 发布/订阅、`send_and_wait`、广播、超时 |
| `tests/test_agents.py` | 各 Agent 独立行为（mock LLM） |
| `tests/test_orchestrator.py` | 完整工作流 |
| `tests/test_sse.py` | FastAPI SSE 接口返回正确事件 |

测试原则：
- 所有依赖 LLM 的地方都用 monkeypatch 替换 `think` 方法。
- HTTP 调用 rag_app/fc_app 的地方用 `httpx.AsyncClient` 的 `transport` mock。

---

## 12. 实现阶段（Phase 2 内部）

为了控制风险，Phase 2 再拆成 3 个小阶段：

### 阶段 2.1：Multi-Agent 内核 + CLI
- Message Bus、BaseAgent、6 个 Agent
- Orchestrator 能跑通"规划 → 检索 → 执行 → 总结 → 评估"完整流程
- 命令行入口 `main.py`，方便本地调试

### 阶段 2.2：FastAPI + SSE
- 把 Orchestrator 包装成 `process_stream` 异步生成器
- 实现 `/chat` SSE 接口
- 实现内存会话管理

### 阶段 2.3：前端 + 部署集成
- nexus_app 自带前端页面
- portfolio 增加 `/nexus` 入口
- Dockerfile、docker-compose、nginx 配置更新
- 端到端验证

---

## 13. 风险与权衡

| 风险 | 影响 | 缓解措施 |
|---|---|---|
| Multi-Agent 复杂度超出预期 | 高 | 按 2.1/2.2/2.3 分阶段，每个阶段都有可运行版本 |
| LLM 调用次数多（Planner + Summarizer + Critic） | 中 | 默认用 qwen-turbo，成本低；后续可加开关 |
| rag_app/fc_app 接口需要改造 | 中 | 先新增 `/execute` 和 `/retrieve`，保留旧接口兼容 |
| SSE 在前端 iframe 中可能有兼容问题 | 低 | 本地先验证，有问题再切到独立页面 |
| Critic LLM 评分不稳定 | 中 | 加 fallback 规则评分；记录评分结果便于后续分析 |

---

## 14. 下一步

1. 用户审查并批准本设计文档。
2. 使用 `superpowers:writing-plans` 制定 Phase 2 详细实现计划。
3. 按阶段 2.1 开始编码。
