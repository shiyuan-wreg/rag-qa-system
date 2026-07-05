# RAG 强制检索（must-retrieve）：从"模型偷懒"到工程兜底

> 目标读者：已经能看懂 Python 和简单 HTTP，但对 RAG、Function Calling、Agent 多轮对话还不熟悉的同学。  
> 阅读建议：按顺序读，代码块可以直接对照仓库源码。  
> 配套代码：`core/agent.py`、`core/tools.py`、`core/rag_tool.py`、`backends/rag_app/main.py`。

---

## 目录

1. [前置基础：RAG 到底是什么](#1-前置基础rag-到底是什么)
2. [为什么 RAG Agent 必须"强制检索"](#2-为什么-rag-agent-必须强制检索)
3. [Function Calling 基础：工具、调用、消息](#3-function-calling-基础工具调用消息)
4. [本项目 RAG 代码结构总览](#4-本项目-rag-代码结构总览)
5. [P0 时代的问题现象](#5-p0-时代的问题现象)
6. [为什么仅靠 system prompt 不够](#6-为什么仅靠-system-prompt-不够)
7. [must-retrieve 设计目标](#7-must-retrieve-设计目标)
8. [双保险机制：prompt 层 + 代码层](#8-双保险机制prompt-层--代码层)
9. [完整代码走读](#9-完整代码走读)
10. [关键代码细节](#10-关键代码细节)
11. [本地 Docker 验证过程](#11-本地-docker-验证过程)
12. [边界情况分析](#12-边界情况分析)
13. [历史消息结构对比](#13-历史消息结构对比)
14. [三种控制力度对比](#14-三种控制力度对比)
15. [与 P1 后续工作的关系](#15-与-p1-后续工作的关系)
16. [动手练习与自查](#16-动手练习与自查)
17. [常见问题 FAQ](#17-常见问题-faq)
18. [总结](#18-总结)

---

## 1. 前置基础：RAG 到底是什么

### 1.1 大模型的"知识截止"问题

你现在用的 ChatGPT、DeepSeek、通义千问等模型，都是在某一时刻用大量文本训练出来的。训练完成后，模型脑子里只有训练数据里的知识。  
如果用户问："2026 年 7 月发布的 Python 3.13 有什么新特性？"，模型很可能不知道，因为它的训练数据截止到 2024 年甚至更早。

这个痛点叫 **知识截止（knowledge cutoff）**。

### 1.2 RAG 的基本思想

RAG 的全称是 **Retrieval-Augmented Generation**，中文常译为"检索增强生成"。它的核心思想是：

> 不要让大模型纯靠记忆回答，而是先让模型去查一份外部资料，再把查到的内容和用户问题一起喂给模型，让模型基于资料作答。

流程可以简化为四步：

```
用户提问 → 检索相关文档片段 → 把片段拼进 prompt → 大模型生成回答
```

在本项目中，检索这一步走的是**向量检索**：

1. 把用户问题转成向量（embedding）
2. 在向量数据库里找最相似的文档片段（top_k）
3. 把最相关的片段格式化成文本
4. 拼进 system prompt 或 tool 结果里

### 1.3 本项目的 RAG 数据流

为了让后面的讲解不抽象，先把本项目 RAG 的完整数据流画出来：

```
浏览器 / curl
    │ POST /rag/chat query=...
    ▼
backends/rag_app/main.py  (FastAPI)
    │
    ▼
core/agent.py 的 Agent.chat()
    │
    ├─► 调用 core/llm.py 的 LLMClient
    │       发请求到 DeepSeek API
    │
    ├─► 若模型返回 tool_calls，调用 core/tools.py 中注册的工具
    │       其中 search_docs 来自 core/rag_tool.py
    │
    └─► 若模型返回普通文本，作为最终 answer 返回
```

`search_docs` 工具内部又走了：

```
search_docs(query)
    │
    ▼
RAGTool.search(query)
    │
    ▼
rag/retriever.py 的 retrieve()
    │
    ▼
Chroma 向量库 → 返回 top_k 个 Document
    │
    ▼
format_retrieved() 格式化成带 [1][2] 来源的文本
```

理解了这个流程，才能理解"强制检索"到底在强制哪一环。

---

## 2. 为什么 RAG Agent 必须"强制检索"

### 2.1 模型会"偷懒"

大模型经过大量训练，脑子里有海量通用知识。当用户问"Python 列表和元组有什么区别"时，模型**不需要查文档也能回答得不错**。  
于是问题来了：

- 用户期待的是"基于你上传的 Python 指南回答"
- 模型却可能直接凭记忆回答
- 两者答案可能相似，但**来源不可追溯**

这就是 RAG 系统里常说的 **"模型偷懒"** 或 **"模型 bypass 检索"**。

### 2.2 直接自答的三大风险

| 风险 | 说明 |
|---|---|
| **幻觉（Hallucination）** | 模型可能把通用知识与文档细节混淆，给出错误答案。 |
| **无法引用** | 没有 `[1]`、`[2]` 引用，用户无法验证答案来自哪段文档。 |
| **与文档不一致** | 如果文档是内部规范、课程讲义、API 手册，模型通用答案可能与文档要求冲突。 |

### 2.3 我们的目标

> 让用户明确知道：RAG demo 的回答是基于知识库文档的，每个关键论点都有来源可溯源。

所以必须保证：**只要进入 RAG 对话，模型在组织答案前必须先调用 `search_docs`**。

---

## 3. Function Calling 基础：工具、调用、消息

在讲 must-retrieve 之前，必须先理解 Function Calling（工具调用）的消息格式。这是整个机制的地基。

### 3.1 什么是"工具"

在本项目里，"工具"就是一个 Python 函数，加上一段 JSON Schema 描述。  
例如 `search_docs` 的工具定义在 `core/tools.py` 中：

```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_docs",
            "description": "从知识库中检索与问题相关的文档片段，用于回答需要依据文档内容的问题",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "检索查询，应是具体的问题或关键词"
                    }
                },
                "required": ["query"]
            }
        }
    },
    # ... 其他工具
]
```

这段 schema 告诉模型：

- 有一个工具叫 `search_docs`
- 它的作用是检索文档片段
- 它需要一个必填参数 `query`，类型是字符串

### 3.2 工具调用的消息流程

当模型决定调用工具时，API 返回的消息结构是：

```json
{
  "role": "assistant",
  "content": null,
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "search_docs",
        "arguments": "{\"query\": \"Python 列表和元组区别\"}"
      }
    }
  ]
}
```

注意：

- `content` 通常是 `null` 或简短说明
- `tool_calls` 是一个数组，模型一次可以调多个工具
- `arguments` 是**字符串化的 JSON**，需要 `json.loads()` 解析

接下来，Agent 要做三件事：

1. 把这条 assistant 消息加入历史
2. 执行工具函数，拿到结果
3. 把结果以 `role: "tool"` 的消息加入历史

```json
{
  "role": "tool",
  "tool_call_id": "call_abc123",
  "content": "用户问题:Python 列表和元组区别\n\n[1] 来源:python_guide.txt\n列表是可变的有序序列..."
}
```

最后，再把完整历史发回给模型，模型基于 tool 结果生成最终回答。

### 3.3 为什么 message 角色很重要

OpenAI 兼容 API 对消息顺序有严格要求：

- `system`：系统指令，只能有一条在最前面
- `user`：用户输入
- `assistant`：模型输出，可能带 `tool_calls`
- `tool`：工具执行结果，必须紧跟对应的 assistant `tool_calls`

如果顺序不对，API 会报错。这也是 `_force_tool_call()` 里要"伪造"一条 assistant tool_calls 的原因——不能凭空只发 `tool` 消息。

---

## 4. 本项目 RAG 代码结构总览

在深入 must-retrieve 前，先把相关文件串起来：

### 4.1 `core/agent.py`

通用多轮 Agent。核心职责：

- 维护对话历史 `self.messages`
- 每次把 `[system_message] + messages` 发给 LLM
- 判断模型返回的是 tool_calls 还是普通文本
- 调用工具、记录日志、控制最大轮数

### 4.2 `core/tools.py`

工具注册表：

```python
TOOL_MAP = {
    "execute_python": safe_execute_python,
    "read_file": read_file,
    "list_files": list_files,
}

TOOLS = [
    # search_docs 的 schema,
    # execute_python 的 schema,
    # read_file 的 schema,
    # list_files 的 schema
]
```

注意 `TOOL_MAP` 初始没有 `search_docs`，它是在 `backends/rag_app/main.py` 启动时动态注入的。

### 4.3 `core/rag_tool.py`

封装 RAG 检索能力：

```python
class RAGTool:
    def __init__(self, docs_path, vector_db_dir):
        self._init_vectorstore()

    def search(self, query: str, top_k: int = 3) -> str:
        docs = retrieve(self.vectorstore, query, k=top_k)
        return format_retrieved(query, docs)

def search_docs(query: str) -> str:
    if _rag_tool is None:
        return "错误: RAG 工具未初始化"
    return _rag_tool.search(query)
```

### 4.4 `backends/rag_app/main.py`

FastAPI 入口：

```python
from core.rag_tool import init_rag_tool, search_docs
from core.tools import TOOL_MAP

init_rag_tool()
TOOL_MAP["search_docs"] = search_docs

agent = Agent()
```

must-retrieve 改的就是把最后一行变成：

```python
agent = Agent(require_first_tool="search_docs")
```

---

## 5. P0 时代的问题现象

在 P0 Agent 质量优化之前，RAG 已经能回答文档相关问题。但存在两类典型表现：

### 5.1 文档内问题：模型会主动检索

用户问：

> "Python 中列表和元组有什么区别？"

模型大概率会调用 `search_docs`，因为问题明显和文档相关。返回的回答也带引用，效果不错。

### 5.2 泛化/开放式问题：模型可能直接自答

用户问：

> "你好"
> "介绍一下 Python"
> "你能做什么"

这类问题没有明确指向文档，模型可能直接凭记忆回答：

> "你好！我是你的 Python 学习助手，可以帮你查文档、解释概念、算表达式……"

听起来没问题，但**没有调用 `search_docs`**，也没有基于文档。  
如果用户后续问"根据文档，Python 列表和元组区别是什么"，模型可能仍然不检索——因为上下文里已经有它自己的回答了。

### 5.3 问题的本质

不是模型"坏"，而是 RAG 的语义边界模糊：  
**"什么时候必须查文档"没有明确的判断标准。**  
对工程系统来说，最可靠的标准就是：**所有进入 RAG 的问题，一律先检索。**

---

## 6. 为什么仅靠 system prompt 不够

### 6.1 system prompt 的作用

P0 的 system prompt 已经写了：

> "当问题涉及文档内容时，必须先用 search_docs 检索，再基于检索结果回答。"

这条指令对大多数问题有效。但它有两个弱点：

1. **"涉及文档内容"是模糊的**：模型自己判断，可能误判。
2. **没有物理约束**：模型可以选择不遵循。

### 6.2 LLM 不保证 100% 遵循指令

影响模型是否调用工具的因素很多：

- 模型版本（DeepSeek、GPT-4、qwen-turbo 行为不同）
- 温度（temperature）
- 问题表述方式
- 工具描述的强弱
- 前文上下文

system prompt 是"建议"，不是"锁"。

### 6.3 工程系统需要确定性

对于一个要对外展示的作品集 demo，我们不能赌模型"这次会不会听话"。  
因此必须在**代码层**加一个兜底：**如果首轮没检索，系统强制替你检索一次。**

这就是 must-retrieve 的核心思想。

---

## 7. must-retrieve 设计目标

在动手改代码前，先明确设计目标：

| 目标 | 说明 |
|---|---|
| **保证首轮检索** | 只要用户发消息，RAG Agent 在第一次回答前必须调用 `search_docs`。 |
| **不破坏多轮能力** | 首轮之后的工具链仍然由模型自主决定。 |
| **对话历史合法** | 强制插入的消息必须符合 OpenAI 兼容格式，API 能继续解析。 |
| **改动最小** | 不重构整个 Agent，只增加一个可选参数和一条兜底路径。 |
| **可观测** | 通过日志能区分"模型主动检索"和"系统强制检索"。 |

---

## 8. 双保险机制：prompt 层 + 代码层

must-retrieve 采用"双保险"：

### 8.1 Prompt 层：明确告知模型必须调用

在 system prompt 里追加：

> "强制规则：你必须在第一次回复时调用 'search_docs' 工具，基于返回结果再组织答案。如果第一轮没有调用该工具，系统将自动替你调用一次。"

这句话有两个作用：

1. **提高模型主动调用的概率**
2. **即使模型不调用，后半句也暗示了"反正系统会兜底"，减少模型困惑**

### 8.2 代码层：首轮未调用则强制调用

在 `Agent.chat()` 的主循环里：

```python
for turn in range(self.max_turns):
    message = self.llm.chat([self.system_message] + self.messages, tools=TOOLS)

    if message.get("tool_calls"):
        # 模型主动调用工具，正常处理
        self._handle_tool_calls(message)
        continue
    else:
        # 模型返回普通文本
        if turn == 0 and self.require_first_tool:
            # 强制调用一次
            self._force_tool_call(self.require_first_tool, user_input)
            continue
        else:
            # 正常返回答案
            return {"answer": message["content"], ...}
```

这样，模型主动调用时走 `_handle_tool_calls`，不调用时走 `_force_tool_call`。

---

## 9. 完整代码走读

### 9.1 `Agent.__init__` 的改动

```python
from typing import Any, Dict, List, Optional

class Agent:
    def __init__(self, model: str = "qwen-turbo", require_first_tool: Optional[str] = None):
        self.model = model
        self.llm = LLMClient.from_config()
        self.messages: List[Dict[str, Any]] = []
        self.max_turns = 5
        self.require_first_tool = require_first_tool

        forced_retrieval_rule = ""
        if self.require_first_tool:
            forced_retrieval_rule = (
                f"\n强制规则:你必须在第一次回复时调用 '{self.require_first_tool}' 工具,"
                "基于返回结果再组织答案。如果第一轮没有调用该工具,系统将自动替你调用一次。\n"
            )

        self.system_message = {
            "role": "system",
            "content": (
                # ... 原有指令 ...
                + forced_retrieval_rule
            )
        }
```

要点：

- `require_first_tool` 是可选参数，保持向后兼容
- 只有启用时，system prompt 才会追加强制规则
- 规则里直接写死工具名，让模型明确知道要调什么

### 9.2 `chat()` 主循环的改动

```python
def chat(self, user_input: str) -> Dict[str, Any]:
    self.messages.append({"role": "user", "content": user_input})
    tool_calls_log: List[Dict[str, Any]] = []

    for turn in range(self.max_turns):
        try:
            message = self.llm.chat(
                [self.system_message] + self.messages,
                tools=TOOLS,
            )

            if message.get("tool_calls"):
                # 记录工具调用日志
                for tc in message["tool_calls"]:
                    tool_calls_log.append({
                        "name": tc["function"]["name"],
                        "arguments": json.loads(tc["function"]["arguments"]),
                        "result": None,
                    })

                # 处理工具调用
                self._handle_tool_calls(message)
                continue
            else:
                # 首轮强制检索
                if turn == 0 and self.require_first_tool:
                    forced_result = self._force_tool_call(
                        self.require_first_tool, user_input
                    )
                    tool_calls_log.append({
                        "name": self.require_first_tool,
                        "arguments": {"query": user_input},
                        "result": forced_result,
                    })
                    continue

                answer = message["content"]
                self.messages.append({"role": "assistant", "content": answer})
                return {
                    "answer": answer,
                    "tool_calls": tool_calls_log,
                    "error": False,
                }

        except Exception as e:
            # ... 错误处理 ...
```

要点：

- 只在 `turn == 0` 强制，避免后续轮次被过度干预
- 强制调用后 `continue`，进入下一轮 LLM 调用
- `tool_calls_log` 记录这次强制调用，前端可以展示"调用了 search_docs"

### 9.3 `_force_tool_call()` 的实现

```python
def _force_tool_call(self, tool_name: str, user_input: str) -> str:
    """
    强制调用指定工具并把结果加入对话历史。
    用于 require_first_tool:模型首轮未主动调用时,系统替它调用一次。
    """
    if tool_name not in TOOL_MAP:
        raise ValueError(f"强制调用的工具未注册: {tool_name}")

    # 目前 RAG 的 search_docs 接收 query 参数
    tool_args = {"query": user_input}
    tool_call_id = f"forced-{tool_name}-{len(self.messages)}"

    print(f"  [强制工具] {tool_name}({json.dumps(tool_args, ensure_ascii=False)})")

    # 伪造 assistant 的 tool_calls,保持对话历史完整
    self.messages.append({
        "role": "assistant",
        "content": "",
        "tool_calls": [
            {
                "id": tool_call_id,
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": json.dumps(tool_args, ensure_ascii=False),
                }
            }
        ]
    })

    try:
        result = TOOL_MAP[tool_name](**tool_args)
    except Exception as e:
        result = f"工具执行失败: {e}"
        print(f"  [强制工具错误] {result}")

    print(f"  [强制工具返回] {result[:200]}{'...' if len(result) > 200 else ''}")

    self.messages.append({
        "role": "tool",
        "content": result,
        "tool_call_id": tool_call_id,
    })
    return result
```

要点：

- 先检查工具是否注册，未注册直接抛异常
- 硬编码 `tool_args = {"query": user_input}`，因为当前只给 `search_docs` 用
- 伪造的 assistant message 必须带 `tool_calls` 数组
- `tool_call_id` 用 `"forced-{tool_name}-{len(self.messages)}"` 保证唯一
- 执行工具后，把结果以 `role: "tool"` 插入历史

### 9.4 `backends/rag_app/main.py` 的改动

```python
# 全局 Agent 实例（单用户简化版）
agent = Agent(require_first_tool="search_docs")
```

就这么一行，RAG demo 就启用了 must-retrieve。

---

## 10. 关键代码细节

### 10.1 为什么 `tool_call_id` 要唯一？

OpenAI 兼容 API 要求：每个 `tool` 消息的 `tool_call_id` 必须对应之前某条 assistant `tool_calls` 里的 `id`。  
如果重复或缺失，模型会把上下文解析混乱，甚至 API 报错。

我们用 `"forced-{tool_name}-{len(self.messages)}"` 生成 ID，基于当前消息长度，基本不会重复。

### 10.2 为什么 `arguments` 要 `json.dumps`？

因为 API 要求 `tool_calls[].function.arguments` 是**字符串**，不是 dict。  
模型返回时已经是字符串，我们自己构造时也要字符串化。

### 10.3 为什么 tool 消息必须紧跟 assistant tool_calls？

OpenAI 的消息顺序规则：

> 每条 `role: "tool"` 消息必须对应同一次请求中模型返回的某条 `tool_calls`。

如果我们只发一条 `role: "tool"` 而没有前置的 assistant `tool_calls`，API 可能报错或模型行为异常。

### 10.4 为什么只在 `turn == 0` 强制？

- 强制检索的目的是解决"模型跳过第一步"的问题
- 一旦首轮检索完成，后续轮次应该让模型自主决定是否需要再检索、计算或读文件
- 如果每轮都强制，会变成死板的规则系统，失去 Agent 的灵活性

### 10.5 `_force_tool_call` 的参数硬编码问题

当前实现：

```python
tool_args = {"query": user_input}
```

这只适用于 `search_docs`。如果未来 FC demo 也想用 must-retrieve，比如强制首轮调用 `get_weather`，参数应该是 `{"city": user_input}`，这就需要扩展。

可能的扩展方向：

- 把 `require_first_tool` 改成 `Union[str, Tuple[str, Dict]]`
- 或者让 `_force_tool_call` 根据工具 schema 自动生成参数
- 当前保持简单，因为只给 RAG 用

---

## 11. 本地 Docker 验证过程

### 11.1 修改代码

改动两个文件：

- `core/agent.py`
- `backends/rag_app/main.py`

### 11.2 复制到运行中的容器

因为本地 Docker 栈已经启动，为了快速验证，先不用重建镜像：

```bash
docker cp core/agent.py deploy-rag-1:/app/core/agent.py
docker cp backends/rag_app/main.py deploy-rag-1:/app/backends/rag_app/main.py
docker restart deploy-rag-1
```

注意：容器重建后 IP 会变，需要重启 nginx：

```bash
docker restart deploy-nginx-1
```

### 11.3 测试首页

```bash
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/rag/
# 200
```

### 11.4 测试英文查询

用 Python requests 避免 Git Bash 中文编码问题：

```python
import requests

url = 'http://127.0.0.1:8080/rag/chat'
resp = requests.post(url, data={
    'query': 'difference between list and tuple in Python'
})
data = resp.json()

print('tool_calls:', data['tool_calls'])
print('answer length:', len(data['answer']))
```

结果：

```
tool_calls: [{'name': 'search_docs', 'arguments': {'query': 'difference between list and tuple in Python'}, 'result': None}]
answer length: 3099
```

说明：

- 模型**主动**调用了 `search_docs`
- `result: None` 是因为这是模型主动调用，原代码的 `tool_calls_log` 只记录调用信息，不记录结果
- 回答长度 3099，包含表格、代码块、`[1]` 引用

### 11.5 中文编码问题的发现

在 Git Bash 里用 curl 或 Python 发送中文表单时，后端收到的 `query` 会变成乱码：

```
{"query": "���"}
```

原因不是代码 bug，而是 **Git Bash / Windows 终端的字符编码环境**。浏览器或生产服务器发 UTF-8 是正常的。

这个发现也写进了 `docs/PROJECT-STATE.md` 的已知问题里。

---

## 12. 边界情况分析

### 12.1 模型主动调用 search_docs

如果模型首轮就返回 `tool_calls` 调用 `search_docs`，走 `_handle_tool_calls()`，不会触发 `_force_tool_call()`。  
这是最常见的情况，实测中 DeepSeek 已经会主动听话。

### 12.2 模型首轮调用其他工具

假设用户问：

> "docs 目录下有什么文件？"

模型可能直接调用 `list_files`。但 RAG 开启了 must-retrieve，于是代码会把它"拉回来"先调用 `search_docs`。  
这可能不是最优用户体验，但保证了"回答前先查知识库"的一致性。

### 12.3 工具未注册

如果 `require_first_tool="search_docs"` 但 `TOOL_MAP` 里没有 `search_docs`（比如 rag_app 忘记 `init_rag_tool()`），`_force_tool_call()` 会抛：

```
ValueError: 强制调用的工具未注册: search_docs
```

这是一个明确的启动期错误，容易排查。

### 12.4 工具执行失败

如果 `search_docs` 内部失败（比如 JINA_API_KEY 没配、文档路径不存在），`_force_tool_call()` 会捕获异常，把错误信息作为 tool 结果插入历史：

```
工具执行失败: ...
```

模型下一轮会基于这个错误信息作答，比如"检索服务暂时不可用"。

### 12.5 达到 max_turns

如果模型在强制检索后仍然反复调用工具不返回答案，会走到：

```python
return {
    "answer": "处理时间过长，请简化您的问题后重试。",
    "tool_calls": tool_calls_log,
    "error": False,
}
```

这是原有保护逻辑，must-retrieve 没有改动它。

---

## 13. 历史消息结构对比

### 13.1 正常检索路径

```
system: 你是一位技术文档讲师... 强制规则:...
user: difference between list and tuple in Python
assistant: (tool_calls: search_docs)
tool: (search_docs 结果)
assistant: (最终回答，带 [1] 引用)
```

### 13.2 强制检索路径

```
system: 你是一位技术文档讲师... 强制规则:...
user: 你好
assistant: (可能准备直接回答)
# 代码拦截，插入：
assistant: (forced tool_calls: search_docs)
tool: (search_docs 结果，可能是"未检索到相关片段")
assistant: (最终回答，基于检索结果)
```

注意：强制路径里有两条 assistant 消息相关记录，但第一条是代码伪造的，不是真实 LLM 输出。

---

## 14. 三种控制力度对比

| 方案 | 优点 | 缺点 | 适用场景 |
|---|---|---|---|
| **纯 system prompt** | 简单，不改动代码 | 不保证执行 | 对可靠性要求不高的 demo |
| **must-retrieve 代码兜底** | 保证首轮检索，改动小 | 只覆盖首轮，参数硬编码 | 本项目当前阶段 |
| **复杂 Agent 框架（LangGraph / ReAct）** | 灵活，可定义任意流程 | 引入依赖，学习成本高 | 生产级复杂工作流 |

本项目的策略是**先简单兜底，再逐步增强检索质量**，避免过早引入复杂框架。

---

## 15. 与 P1 后续工作的关系

must-retrieve 只是 RAG P1 的第一步。它解决的是"有没有检索"，不是"检索好不好"。

P1 后续还有：

1. **top_k 加大**：从默认 3 改成 5 或 10，让更多相关片段参与生成
2. **rerank（Jina API）**：先向量召回 20 个，再用 Jina reranker 排序取前 5
3. **hybrid（向量 + BM25）**：向量检索 + 关键词检索，互补召回
4. **chroma_db 持久化挂卷**：避免每次重建容器都重新调 Jina 建库

must-retrieve 与这些不冲突：它保证检索一定发生，后续优化让检索结果更准。

---

## 16. 动手练习与自查

### 练习 1：在浏览器里观察 must-retrieve

1. 打开 `http://127.0.0.1:8080/rag/`
2. 输入"你好"
3. 看回答下方是否显示"调用了工具: search_docs({"query":"你好"})"
4. 如果显示了，说明强制检索生效

### 练习 2：打印对话历史

在 `core/agent.py` 的 `chat()` 最后加一行：

```python
print(json.dumps(self.messages, ensure_ascii=False, indent=2))
```

然后重启容器，观察强制检索时 messages 里多了哪些内容。

### 练习 3：故意让强制调用失败

把 `backends/rag_app/main.py` 里的：

```python
TOOL_MAP["search_docs"] = search_docs
```

注释掉，然后问一个问题。看是否抛出 `ValueError: 强制调用的工具未注册: search_docs`。

---

## 17. 常见问题 FAQ

### Q1: 强制检索会不会让问候语也变奇怪？

会。如果用户只问"你好"，模型也会先检索知识库。检索结果可能和问候无关，模型会基于结果说"你好，我可以帮你查 Python 文档"。  
这是一个 trade-off：为了保证所有回答都可溯源，牺牲了纯问候语的"自然感"。

### Q2: 生产部署要注意什么？

本次改动只改了源码，生产服务器还没部署。部署流程：

```bash
ssh shiyuan-prod
cd /opt/ai-demos
git pull origin master
bash deploy/build-frontends.sh
docker compose -f deploy/docker-compose.yml up -d --build
```

需要本机代理开着（见 `deploy/PRODUCTION.md`）。

### Q3: 和 FC 的 `missing_required_args` 机制有什么区别？

- `missing_required_args`：模型**已经决定调用工具**，但参数缺了 required 字段，系统让模型反问用户补参数。
- `must-retrieve`：模型**没调用工具**，系统替它调用一次。

前者处理"工具调用不规范"，后者处理"工具调用缺失"。

### Q4: 为什么不用 JSON 接口避免中文编码问题？

当前 RAG/FC 用的是 `Form(...)` 表单接口。改成 JSON 可以避免编码问题，但会改动 API 契约，需要同步改前端 fetch。如果后续频繁遇到编码问题，可以考虑统一改成 JSON。

---

## 18. 总结

RAG 系统的核心承诺是：**回答基于文档，且可溯源。**  
但大模型有通用知识，容易"偷懒"直接自答，导致回答没有引用、不可验证。

本项目的解决方案是 **must-retrieve（强制首轮检索）**：

1. **Prompt 层**：在 system message 里明确告诉模型必须调用 `search_docs`
2. **代码层**：如果模型首轮没调用，系统自动伪造一条 assistant tool_call，执行 `search_docs`，把结果插入对话历史，然后让模型基于检索结果作答

实现上只改了两个文件：

- `core/agent.py`：新增 `require_first_tool` 参数和 `_force_tool_call()` 方法
- `backends/rag_app/main.py`：`Agent(require_first_tool="search_docs")`

验证结果：本地 Docker 实测英文查询触发 `search_docs`，返回带 `[1]` 引用的详细 Markdown 回答。

must-retrieve 是 RAG P1 的第一步，后续还会做 top_k 加大、rerank、hybrid 检索、chroma_db 持久化，持续优化检索质量。

---

## 参考链接

- 项目仓库：`https://github.com/shiyuan-wreg/rag-qa-system`
- 本地入口：`http://127.0.0.1:8080/rag/`
- 相关源码：
  - `core/agent.py`
  - `core/tools.py`
  - `core/rag_tool.py`
  - `backends/rag_app/main.py`
- 相关文档：
  - `docs/PROJECT-STATE.md`
  - `docs/dev-log.md`
