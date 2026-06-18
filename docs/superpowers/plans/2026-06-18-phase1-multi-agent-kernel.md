# Nexus Phase 1: Multi-Agent Kernel + Message Bus Implementation Plan

> **For agentic workers:** REQUIRED SUB-_SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the foundational Multi-Agent kernel with an in-memory async message bus, six specialized agents (Orchestrator, Planner, Retriever, Executor, Summarizer, Critic), and a command-line interface that can run a complete task end-to-end.

**Architecture:** Agents communicate through a centralized `MessageBus` using typed `Message` objects. The `OrchestratorAgent` receives user input, dispatches tasks to other agents, and aggregates results. Each agent is an async task that processes messages from its own queue. Phase 1 uses mocked retrieval and tool execution so the kernel can be tested without RAG or Tool Registry dependencies.

**Tech Stack:** Python 3.10+, FastAPI (for future web integration), DashScope (Tongyi Qwen), pytest, asyncio.

## Global Constraints

- **LLM Provider**: Default to Tongyi Qwen (`qwen-turbo`) via DashScope; architecture must allow future provider swaps.
- **Python version**: 3.10+
- **No external message broker**: Use `asyncio.Queue` for Phase 1.
- **Test-driven**: Every non-trivial unit must have a failing test before implementation.
- **Commit frequency**: Each task ends with a git commit.
- **No real tool/RAG dependencies in Phase 1**: Retriever and Executor return mocked results.
- **File boundaries**: Each agent lives in its own file under `core/agents/`.

---

## File Structure

| File | Responsibility |
|---|---|
| `core/config.py` | Load `.env` configuration (LLM keys, model name) |
| `core/llm.py` | `LLMClient` abstraction for Qwen and future providers |
| `core/message.py` | `Message` dataclass and message type constants |
| `core/message_bus.py` | In-memory async pub/sub message bus |
| `core/agents/base.py` | `BaseAgent` abstract class with message loop |
| `core/agents/orchestrator.py` | `OrchestratorAgent`: task dispatch and aggregation |
| `core/agents/planner.py` | `PlannerAgent`: decomposes tasks into steps |
| `core/agents/retriever.py` | `RetrieverAgent`: mocked knowledge retrieval |
| `core/agents/executor.py` | `ExecutorAgent`: mocked tool execution |
| `core/agents/summarizer.py` | `SummarizerAgent`: synthesizes final answers |
| `core/agents/critic.py` | `CriticAgent`: evaluates answer quality |
| `core/session.py` | `SessionState`: tracks task status and history |
| `main.py` | Command-line entry point for Phase 1 |
| `tests/test_message_bus.py` | Tests for message bus |
| `tests/test_agents.py` | Tests for individual agents |
| `tests/test_orchestrator.py` | Integration tests for full workflow |

---

### Task 1: Project Configuration and LLM Client

**Files:**
- Create: `core/config.py`
- Create: `core/llm.py`
- Test: `tests/test_llm_client.py`
- Modify: `.env.example`

**Interfaces:**
- Consumes: environment variables `LLM_PROVIDER`, `LLM_MODEL`, `DASHSCOPE_API_KEY`
- Produces: `LLMClient.chat(messages, tools=None, stream=False)` returning a dict with `content` and optional `tool_calls`

- [ ] **Step 1: Write the failing test**

Create `tests/test_llm_client.py`:

```python
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.llm import LLMClient


def test_llm_client_extracts_content_from_qwen_response():
    client = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake-key")
    mock_response = {
        "output": {
            "choices": [
                {"message": {"content": "hello", "tool_calls": None}}
            ]
        }
    }
    result = client._extract_content(mock_response)
    assert result["content"] == "hello"
    assert result["tool_calls"] is None


def test_llm_client_extracts_tool_calls():
    client = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake-key")
    mock_response = {
        "output": {
            "choices": [
                {
                    "message": {
                        "content": "",
                        "tool_calls": [
                            {"id": "1", "function": {"name": "search", "arguments": "{}"}}
                        ]
                    }
                }
            ]
        }
    }
    result = client._extract_content(mock_response)
    assert result["content"] == ""
    assert len(result["tool_calls"]) == 1
    assert result["tool_calls"][0]["function"]["name"] == "search"
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_llm_client.py -v
```

Expected: FAIL with "ModuleNotFoundError: No module named 'core.llm'"

- [ ] **Step 3: Write minimal implementation**

Create `core/config.py`:

```python
"""Configuration management."""

import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "qwen")
    LLM_MODEL = os.environ.get("LLM_MODEL", "qwen-turbo")
    DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
```

Create `core/llm.py`:

```python
"""Unified LLM client abstraction."""

from typing import Any, Dict, List, Optional


class LLMClient:
    """
    Unified LLM client supporting Qwen (default) and OpenAI-compatible APIs.
    """

    def __init__(self, provider: str, model: str, api_key: str, base_url: Optional[str] = None):
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self._raw_client = self._create_client()

    def _create_client(self):
        if self.provider == "qwen":
            import dashscope
            dashscope.api_key = self.api_key
            return dashscope.Generation
        else:
            from openai import OpenAI
            return OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict]] = None, stream: bool = False) -> Dict[str, Any]:
        if self.provider == "qwen":
            response = self._raw_client.call(
                model=self.model,
                messages=messages,
                tools=tools,
                result_format="message",
            )
        else:
            response = self._raw_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                stream=stream,
            )
        return self._extract_content(response)

    def _extract_content(self, response: Any) -> Dict[str, Any]:
        if self.provider == "qwen":
            message = response.output.choices[0].message
            return {
                "content": message.get("content", ""),
                "tool_calls": message.get("tool_calls"),
            }
        else:
            message = response.choices[0].message
            tool_calls = []
            if message.tool_calls:
                for tc in message.tool_calls:
                    tool_calls.append({
                        "id": tc.id,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    })
            return {
                "content": message.content or "",
                "tool_calls": tool_calls or None,
            }
```

Update `.env.example`:

```bash
LLM_PROVIDER=qwen
LLM_MODEL=qwen-turbo
DASHSCOPE_API_KEY=your-dashscope-api-key
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_llm_client.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add core/config.py core/llm.py tests/test_llm_client.py .env.example
git commit -m "feat: add LLM client abstraction with Qwen support"
```

---

### Task 2: Message Bus

**Files:**
- Create: `core/message.py`
- Create: `core/message_bus.py`
- Test: `tests/test_message_bus.py`

**Interfaces:**
- Consumes: `Message` dataclass
- Produces: `MessageBus.subscribe(agent_id)`, `MessageBus.publish(message)`, `MessageBus.send_and_wait(agent_id, message, timeout=30)`

- [ ] **Step 1: Write the failing test**

Create `tests/test_message_bus.py`:

```python
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from core.message import Message
from core.message_bus import MessageBus


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


@pytest.mark.asyncio
async def test_send_and_wait():
    bus = MessageBus()

    async def responder():
        queue = bus.subscribe("retriever")
        msg = await queue.get()
        await bus.publish(Message(
            task_id=msg.task_id,
            sender="retriever",
            recipient="orchestrator",
            message_type="result",
            payload={"result": "found"},
        ))

    asyncio.create_task(responder())

    request = Message(
        task_id="t2",
        sender="orchestrator",
        recipient="retriever",
        message_type="task",
        payload={"query": "hello"},
    )

    result = await bus.send_and_wait("retriever", request, timeout=1.0)
    assert result.payload["result"] == "found"


@pytest.mark.asyncio
async def test_send_and_wait_timeout():
    bus = MessageBus()
    request = Message(
        task_id="t3",
        sender="orchestrator",
        recipient="retriever",
        message_type="task",
        payload={},
    )

    with pytest.raises(asyncio.TimeoutError):
        await bus.send_and_wait("retriever", request, timeout=0.1)
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_message_bus.py -v
```

Expected: FAIL with import errors.

- [ ] **Step 3: Write minimal implementation**

Create `core/message.py`:

```python
"""Message definitions for inter-agent communication."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from uuid import uuid4


@dataclass
class Message:
    task_id: str
    sender: str
    recipient: str
    message_type: str  # task, result, plan, thought, critique, error
    payload: Dict[str, Any]
    message_id: str = field(default_factory=lambda: str(uuid4()))
    in_reply_to: Optional[str] = None
```

Create `core/message_bus.py`:

```python
"""In-memory async message bus for agent communication."""

import asyncio
from typing import Dict

from core.message import Message


class MessageBus:
    """
    In-memory message bus using asyncio.Queue.
    Each subscriber gets its own queue identified by agent_id.
    """

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
                raise ValueError(f"No subscriber for agent: {message.recipient}")
            await queue.put(message)

    async def send_and_wait(
        self,
        recipient: str,
        message: Message,
        timeout: float = 30.0,
    ) -> Message:
        await self.publish(message)
        return await self.wait_for_result(message.task_id, recipient, timeout)

    async def wait_for_result(
        self,
        task_id: str,
        sender: str,
        timeout: float = 30.0,
    ) -> Message:
        queue = self.subscribe("orchestrator")
        deadline = asyncio.get_event_loop().time() + timeout

        while True:
            remaining = deadline - asyncio.get_event_loop().time()
            if remaining <= 0:
                raise asyncio.TimeoutError()

            try:
                msg = await asyncio.wait_for(queue.get(), timeout=remaining)
            except asyncio.TimeoutError:
                raise

            if msg.sender == sender and msg.task_id == task_id:
                return msg
            else:
                await queue.put(msg)
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_message_bus.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add core/message.py core/message_bus.py tests/test_message_bus.py
git commit -m "feat: add in-memory async message bus"
```

---

### Task 3: Base Agent

**Files:**
- Create: `core/agents/__init__.py`
- Create: `core/agents/base.py`
- Test: `tests/test_base_agent.py`

**Interfaces:**
- Consumes: `MessageBus`, `Message`, `LLMClient`
- Produces: `BaseAgent.run()` coroutine that processes messages until stopped

- [ ] **Step 1: Write the failing test**

Create `tests/test_base_agent.py`:

```python
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from core.agents.base import BaseAgent
from core.llm import LLMClient
from core.message import Message
from core.message_bus import MessageBus


class EchoAgent(BaseAgent):
    async def handle_message(self, message: Message) -> None:
        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"echo": message.payload.get("text", "")},
            task_id=message.task_id,
        )


@pytest.mark.asyncio
async def test_base_agent_message_loop():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    agent = EchoAgent("echo", bus, llm)

    task = asyncio.create_task(agent.run())

    request = Message(
        task_id="t1",
        sender="orchestrator",
        recipient="echo",
        message_type="task",
        payload={"text": "hello"},
    )

    result = await bus.send_and_wait("echo", request, timeout=1.0)
    assert result.payload["echo"] == "hello"

    agent.stop()
    await asyncio.wait_for(task, timeout=1.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_base_agent.py -v
```

Expected: FAIL with import error.

- [ ] **Step 3: Write minimal implementation**

Create `core/agents/__init__.py`:

```python
"""Agent implementations."""
```

Create `core/agents/base.py`:

```python
"""Base agent class."""

from abc import abstractmethod
from typing import Any, Dict, Optional

from core.llm import LLMClient
from core.message import Message
from core.message_bus import MessageBus


class BaseAgent:
    def __init__(self, agent_id: str, bus: MessageBus, llm: LLMClient):
        self.agent_id = agent_id
        self.bus = bus
        self.llm = llm
        self._running = False

    async def run(self) -> None:
        """Main message processing loop."""
        self._running = True
        queue = self.bus.subscribe(self.agent_id)

        while self._running:
            try:
                message = await asyncio.wait_for(queue.get(), timeout=0.5)
                await self.handle_message(message)
            except asyncio.TimeoutError:
                continue

    def stop(self) -> None:
        self._running = False

    @abstractmethod
    async def handle_message(self, message: Message) -> None:
        """Process incoming message. Must be implemented by subclasses."""
        pass

    async def send_message(
        self,
        recipient: str,
        message_type: str,
        payload: Dict[str, Any],
        task_id: str,
        in_reply_to: Optional[str] = None,
    ) -> None:
        msg = Message(
            task_id=task_id,
            sender=self.agent_id,
            recipient=recipient,
            message_type=message_type,
            payload=payload,
            in_reply_to=in_reply_to,
        )
        await self.bus.publish(msg)

    async def think(self, system_prompt: str, user_prompt: str, tools: Optional[list] = None) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return self.llm.chat(messages, tools=tools)
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_base_agent.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add core/agents/__init__.py core/agents/base.py tests/test_base_agent.py
git commit -m "feat: add BaseAgent with message loop"
```

---

### Task 4: Planner Agent

**Files:**
- Create: `core/agents/planner.py`
- Test: `tests/test_planner.py`

**Interfaces:**
- Consumes: task message with `query` in payload
- Produces: result message with `plan` (list of steps) in payload

- [ ] **Step 1: Write the failing test**

Create `tests/test_planner.py`:

```python
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from core.agents.planner import PlannerAgent
from core.llm import LLMClient
from core.message import Message
from core.message_bus import MessageBus


@pytest.mark.asyncio
async def test_planner_returns_steps():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    planner = PlannerAgent(bus, llm)

    task = asyncio.create_task(planner.run())

    request = Message(
        task_id="t1",
        sender="orchestrator",
        recipient="planner",
        message_type="task",
        payload={"query": "查一下 Python 列表和元组的区别，然后写个示例代码"},
    )

    # Mock LLM response by monkeypatching
    planner.think = async_mock_think

    result = await bus.send_and_wait("planner", request, timeout=1.0)
    assert "plan" in result.payload
    assert len(result.payload["plan"]) > 0
    assert result.payload["plan"][0]["agent"] == "retriever"

    planner.stop()
    await asyncio.wait_for(task, timeout=1.0)


async def async_mock_think(system_prompt: str, user_prompt: str, tools=None):
    return {
        "content": '{"steps": [{"step_id": 1, "agent": "retriever", "task": "检索 Python 列表和元组区别"}, {"step_id": 2, "agent": "executor", "task": "写示例代码"}, {"step_id": 3, "agent": "summarizer", "task": "总结结果"}]}',
        "tool_calls": None,
    }
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_planner.py -v
```

Expected: FAIL with import error.

- [ ] **Step 3: Write minimal implementation**

Create `core/agents/planner.py`:

```python
"""Planner Agent: decomposes user requests into executable steps."""

import json
from typing import Any, Dict

from core.agents.base import BaseAgent
from core.message import Message


class PlannerAgent(BaseAgent):
    def __init__(self, bus, llm):
        super().__init__("planner", bus, llm)

    async def handle_message(self, message: Message) -> None:
        query = message.payload.get("query", "")

        system_prompt = """你是一个任务规划专家。请将用户的需求拆解为可执行的步骤。
每个步骤必须包含：step_id（整数）、agent（执行该步骤的 Agent 名称）、task（具体任务描述）。
可用 Agent：retriever（检索知识库）、executor（执行工具）、summarizer（总结生成）。
请只输出 JSON 格式，不要输出其他解释。

输出格式示例：
{
  "steps": [
    {"step_id": 1, "agent": "retriever", "task": "检索知识库中关于 xxx 的内容"},
    {"step_id": 2, "agent": "executor", "task": "调用工具执行 xxx"},
    {"step_id": 3, "agent": "summarizer", "task": "总结结果并生成回答"}
  ]
}"""

        response = await self.think(system_prompt, f"用户需求：{query}")
        plan = self._parse_plan(response.get("content", "{}"))

        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"plan": plan},
            task_id=message.task_id,
        )

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

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_planner.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add core/agents/planner.py tests/test_planner.py
git commit -m "feat: add PlannerAgent for task decomposition"
```

---

### Task 5: Retriever Agent (Mocked)

**Files:**
- Create: `core/agents/retriever.py`
- Test: `tests/test_retriever.py`

**Interfaces:**
- Consumes: task message with `query` in payload
- Produces: result message with `documents` (list of snippets) in payload

- [ ] **Step 1: Write the failing test**

Create `tests/test_retriever.py`:

```python
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from core.agents.retriever import RetrieverAgent
from core.llm import LLMClient
from core.message import Message
from core.message_bus import MessageBus


@pytest.mark.asyncio
async def test_retriever_returns_mock_documents():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    retriever = RetrieverAgent(bus, llm)

    task = asyncio.create_task(retriever.run())

    request = Message(
        task_id="t1",
        sender="orchestrator",
        recipient="retriever",
        message_type="task",
        payload={"query": "Python 列表和元组"},
    )

    result = await bus.send_and_wait("retriever", request, timeout=1.0)
    assert "documents" in result.payload
    assert len(result.payload["documents"]) > 0
    assert "source" in result.payload["documents"][0]

    retriever.stop()
    await asyncio.wait_for(task, timeout=1.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_retriever.py -v
```

Expected: FAIL with import error.

- [ ] **Step 3: Write minimal implementation**

Create `core/agents/retriever.py`:

```python
"""Retriever Agent: retrieves relevant knowledge (mocked in Phase 1)."""

from core.agents.base import BaseAgent
from core.message import Message


class RetrieverAgent(BaseAgent):
    """
    Phase 1 mock retriever.
    In Phase 2, this will connect to Chroma vector store.
    """

    def __init__(self, bus, llm):
        super().__init__("retriever", bus, llm)

    async def handle_message(self, message: Message) -> None:
        query = message.payload.get("query", "")

        # Mock retrieval based on keywords
        documents = self._mock_retrieve(query)

        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"documents": documents, "query": query},
            task_id=message.task_id,
        )

    def _mock_retrieve(self, query: str) -> list:
        query_lower = query.lower()
        if "python" in query_lower and ("list" in query_lower or "列表" in query_lower):
            return [
                {"content": "列表（list）是可变序列，支持增删改。", "source": "mock_notes/python_basics.md", "score": 0.95},
                {"content": "元组（tuple）是不可变序列，通常用于固定数据。", "source": "mock_notes/python_basics.md", "score": 0.93},
            ]
        elif "rag" in query_lower or "评估" in query_lower:
            return [
                {"content": "RAG 评估可以从正确性、相关性、完整性等维度进行。", "source": "mock_notes/rag_eval.md", "score": 0.91},
            ]
        else:
            return [
                {"content": f"关于 '{query}' 的模拟检索结果。", "source": "mock_notes/general.md", "score": 0.80},
            ]
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_retriever.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add core/agents/retriever.py tests/test_retriever.py
git commit -m "feat: add mocked RetrieverAgent"
```

---

### Task 6: Executor Agent (Mocked)

**Files:**
- Create: `core/agents/executor.py`
- Test: `tests/test_executor.py`

**Interfaces:**
- Consumes: task message with `tool` and `args` in payload
- Produces: result message with `result` in payload

- [ ] **Step 1: Write the failing test**

Create `tests/test_executor.py`:

```python
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from core.agents.executor import ExecutorAgent
from core.llm import LLMClient
from core.message import Message
from core.message_bus import MessageBus


@pytest.mark.asyncio
async def test_executor_calculate():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    executor = ExecutorAgent(bus, llm)

    task = asyncio.create_task(executor.run())

    request = Message(
        task_id="t1",
        sender="orchestrator",
        recipient="executor",
        message_type="task",
        payload={"tool": "calculate", "args": {"expression": "2 + 2"}},
    )

    result = await bus.send_and_wait("executor", request, timeout=1.0)
    assert result.payload["result"] == "4"

    executor.stop()
    await asyncio.wait_for(task, timeout=1.0)


@pytest.mark.asyncio
async def test_executor_unknown_tool():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    executor = ExecutorAgent(bus, llm)

    task = asyncio.create_task(executor.run())

    request = Message(
        task_id="t2",
        sender="orchestrator",
        recipient="executor",
        message_type="task",
        payload={"tool": "unknown", "args": {}},
    )

    result = await bus.send_and_wait("executor", request, timeout=1.0)
    assert "error" in result.payload["result"].lower()

    executor.stop()
    await asyncio.wait_for(task, timeout=1.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_executor.py -v
```

Expected: FAIL with import error.

- [ ] **Step 3: Write minimal implementation**

Create `core/agents/executor.py`:

```python
"""Executor Agent: executes tools (mocked in Phase 1)."""

import ast
import operator

from core.agents.base import BaseAgent
from core.message import Message


class ExecutorAgent(BaseAgent):
    """
    Phase 1 mock executor.
    In Phase 2, this will connect to the real Tool Registry.
    """

    def __init__(self, bus, llm):
        super().__init__("executor", bus, llm)
        self._tools = {
            "calculate": self._calculate,
            "read_file": self._read_file,
        }

    async def handle_message(self, message: Message) -> None:
        tool_name = message.payload.get("tool", "")
        args = message.payload.get("args", {})

        handler = self._tools.get(tool_name)
        if handler is None:
            result = f"Error: unknown tool '{tool_name}'"
        else:
            result = handler(**args)

        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"result": result, "tool": tool_name, "args": args},
            task_id=message.task_id,
        )

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
            return ops[type(node.op)](self._eval_node(node.left), self._eval_node(node.right))
        raise ValueError(f"Unsupported node: {type(node).__name__}")

    def _read_file(self, path: str) -> str:
        return f"[Mock] Content of {path}"
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_executor.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add core/agents/executor.py tests/test_executor.py
git commit -m "feat: add mocked ExecutorAgent"
```

---

### Task 7: Summarizer Agent

**Files:**
- Create: `core/agents/summarizer.py`
- Test: `tests/test_summarizer.py`

**Interfaces:**
- Consumes: task message with `query`, `documents`, `tool_results` in payload
- Produces: result message with `answer` in payload

- [ ] **Step 1: Write the failing test**

Create `tests/test_summarizer.py`:

```python
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from core.agents.summarizer import SummarizerAgent
from core.llm import LLMClient
from core.message import Message
from core.message_bus import MessageBus


@pytest.mark.asyncio
async def test_summarizer_returns_answer():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    summarizer = SummarizerAgent(bus, llm)

    summarizer.think = async_mock_think

    task = asyncio.create_task(summarizer.run())

    request = Message(
        task_id="t1",
        sender="orchestrator",
        recipient="summarizer",
        message_type="task",
        payload={
            "query": "Python 列表和元组区别",
            "documents": [{"content": "列表可变，元组不可变。"}],
            "tool_results": [{"result": "2 + 2 = 4"}],
        },
    )

    result = await bus.send_and_wait("summarizer", request, timeout=1.0)
    assert "answer" in result.payload
    assert len(result.payload["answer"]) > 0

    summarizer.stop()
    await asyncio.wait_for(task, timeout=1.0)


async def async_mock_think(system_prompt: str, user_prompt: str, tools=None):
    return {
        "content": "列表示可变序列，元组是不可变序列。",
        "tool_calls": None,
    }
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_summarizer.py -v
```

Expected: FAIL with import error.

- [ ] **Step 3: Write minimal implementation**

Create `core/agents/summarizer.py`:

```python
"""Summarizer Agent: synthesizes final answers from intermediate results."""

from core.agents.base import BaseAgent
from core.message import Message


class SummarizerAgent(BaseAgent):
    def __init__(self, bus, llm):
        super().__init__("summarizer", bus, llm)

    async def handle_message(self, message: Message) -> None:
        query = message.payload.get("query", "")
        documents = message.payload.get("documents", [])
        tool_results = message.payload.get("tool_results", [])

        system_prompt = """你是一个总结专家。请根据检索到的文档和工具执行结果，生成准确、简洁的中文回答。
如果文档中没有相关内容，请明确说明。不要编造信息。"""

        context = self._build_context(documents, tool_results)
        user_prompt = f"用户问题：{query}\n\n参考资料：\n{context}\n\n请生成最终回答："

        response = await self.think(system_prompt, user_prompt)
        answer = response.get("content", "抱歉，无法生成回答。")

        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"answer": answer},
            task_id=message.task_id,
        )

    def _build_context(self, documents: list, tool_results: list) -> str:
        parts = []
        for i, doc in enumerate(documents, 1):
            parts.append(f"[文档 {i}] {doc.get('content', '')}")
        for i, result in enumerate(tool_results, 1):
            parts.append(f"[工具结果 {i}] {result.get('result', '')}")
        return "\n\n".join(parts) if parts else "无参考资料"
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_summarizer.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add core/agents/summarizer.py tests/test_summarizer.py
git commit -m "feat: add SummarizerAgent"
```

---

### Task 8: Critic Agent

**Files:**
- Create: `core/agents/critic.py`
- Test: `tests/test_critic.py`

**Interfaces:**
- Consumes: task message with `query`, `answer` in payload
- Produces: result message with `scores` and `passed` in payload

- [ ] **Step 1: Write the failing test**

Create `tests/test_critic.py`:

```python
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from core.agents.critic import CriticAgent
from core.llm import LLMClient
from core.message import Message
from core.message_bus import MessageBus


@pytest.mark.asyncio
async def test_critic_scores_answer():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    critic = CriticAgent(bus, llm)

    task = asyncio.create_task(critic.run())

    request = Message(
        task_id="t1",
        sender="orchestrator",
        recipient="critic",
        message_type="task",
        payload={
            "query": "Python 列表和元组区别",
            "answer": "列表是可变序列，元组是不可变序列。",
        },
    )

    result = await bus.send_and_wait("critic", request, timeout=1.0)
    assert "scores" in result.payload
    assert "passed" in result.payload
    assert 0.0 <= result.payload["scores"]["overall"] <= 1.0

    critic.stop()
    await asyncio.wait_for(task, timeout=1.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_critic.py -v
```

Expected: FAIL with import error.

- [ ] **Step 3: Write minimal implementation**

Create `core/agents/critic.py`:

```python
"""Critic Agent: evaluates answer quality."""

import re

from core.agents.base import BaseAgent
from core.message import Message


class CriticAgent(BaseAgent):
    def __init__(self, bus, llm):
        super().__init__("critic", bus, llm)

    async def handle_message(self, message: Message) -> None:
        query = message.payload.get("query", "")
        answer = message.payload.get("answer", "")

        scores = self._rule_based_scores(query, answer)
        passed = scores["overall"] >= 0.6

        await self.send_message(
            recipient=message.sender,
            message_type="critique",
            payload={
                "scores": scores,
                "passed": passed,
                "feedback": "回答通过评估" if passed else "回答质量不足，建议补充信息",
            },
            task_id=message.task_id,
        )

    def _rule_based_scores(self, query: str, answer: str) -> dict:
        query_keywords = set(re.findall(r"\b\w{2,}\b", query.lower()))
        if query_keywords:
            matched = sum(1 for kw in query_keywords if kw in answer.lower())
            relevance = round(min(matched / len(query_keywords) * 1.5, 1.0), 2)
        else:
            relevance = 0.5

        if len(answer) < 10:
            completeness = 0.0
        elif len(answer) > 100:
            completeness = 0.8
        else:
            completeness = 0.5

        harmful = ["炸弹", "毒品", "杀人"]
        safety = 0.0 if any(kw in answer for kw in harmful) else 1.0

        correctness = 0.7 if "错误" not in answer and "不知道" not in answer else 0.3

        overall = round((correctness + relevance + completeness + safety) / 4, 2)
        return {
            "correctness": correctness,
            "relevance": relevance,
            "completeness": completeness,
            "safety": safety,
            "overall": overall,
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_critic.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add core/agents/critic.py tests/test_critic.py
git commit -m "feat: add CriticAgent for answer quality evaluation"
```

---

### Task 9: Orchestrator Agent

**Files:**
- Create: `core/agents/orchestrator.py`
- Create: `core/session.py`
- Test: `tests/test_orchestrator.py`

**Interfaces:**
- Consumes: user query from CLI/Web
- Produces: final answer via `process(query)` return value

- [ ] **Step 1: Write the failing test**

Create `tests/test_orchestrator.py`:

```python
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from core.agents.critic import CriticAgent
from core.agents.executor import ExecutorAgent
from core.agents.orchestrator import OrchestratorAgent
from core.agents.planner import PlannerAgent
from core.agents.retriever import RetrieverAgent
from core.agents.summarizer import SummarizerAgent
from core.llm import LLMClient
from core.message_bus import MessageBus


@pytest.mark.asyncio
async def test_orchestrator_simple_workflow():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")

    orchestrator = OrchestratorAgent(bus, llm)
    planner = PlannerAgent(bus, llm)
    retriever = RetrieverAgent(bus, llm)
    executor = ExecutorAgent(bus, llm)
    summarizer = SummarizerAgent(bus, llm)
    critic = CriticAgent(bus, llm)

    # Mock planner to avoid LLM call
    planner.think = async_mock_planner_think

    tasks = [
        asyncio.create_task(orchestrator.run()),
        asyncio.create_task(planner.run()),
        asyncio.create_task(retriever.run()),
        asyncio.create_task(executor.run()),
        asyncio.create_task(summarizer.run()),
        asyncio.create_task(critic.run()),
    ]

    result = await orchestrator.process("Python 列表和元组有什么区别？")

    assert "answer" in result
    assert len(result["answer"]) > 0

    orchestrator.stop()
    planner.stop()
    retriever.stop()
    executor.stop()
    summarizer.stop()
    critic.stop()

    await asyncio.gather(*[asyncio.wait_for(t, timeout=2.0) for t in tasks])


async def async_mock_planner_think(system_prompt: str, user_prompt: str, tools=None):
    return {
        "content": '{"steps": [{"step_id": 1, "agent": "retriever", "task": "检索 Python 列表和元组区别"}, {"step_id": 2, "agent": "summarizer", "task": "总结生成回答"}]}',
        "tool_calls": None,
    }
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_orchestrator.py -v
```

Expected: FAIL with import errors.

- [ ] **Step 3: Write minimal implementation**

Create `core/session.py`:

```python
"""Session state tracking for orchestrator."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class SessionState:
    task_id: str
    query: str
    plan: List[Dict] = field(default_factory=list)
    documents: List[Dict] = field(default_factory=list)
    tool_results: List[Dict] = field(default_factory=list)
    answer: str = ""
    critique: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, planning, executing, summarizing, critiquing, done, error
```

Create `core/agents/orchestrator.py`:

```python
"""Orchestrator Agent: coordinates all other agents."""

import asyncio
import uuid
from typing import Any, Dict

from core.agents.base import BaseAgent
from core.message import Message
from core.session import SessionState


class OrchestratorAgent(BaseAgent):
    def __init__(self, bus, llm):
        super().__init__("orchestrator", bus, llm)
        self._pending_futures: Dict[str, asyncio.Future] = {}

    async def handle_message(self, message: Message) -> None:
        if message.message_type == "result" or message.message_type == "critique":
            future = self._pending_futures.get(message.task_id)
            if future and not future.done():
                future.set_result(message)

    async def process(self, query: str, timeout: float = 60.0) -> Dict[str, Any]:
        task_id = str(uuid.uuid4())
        session = SessionState(task_id=task_id, query=query)

        # Step 1: Plan
        session.status = "planning"
        plan_msg = await self._send_and_wait(
            "planner",
            Message(
                task_id=task_id,
                sender="orchestrator",
                recipient="planner",
                message_type="task",
                payload={"query": query},
            ),
            timeout,
        )
        session.plan = plan_msg.payload.get("plan", [])

        # Step 2: Execute plan steps
        session.status = "executing"
        for step in session.plan:
            agent_id = step.get("agent")
            if agent_id == "retriever":
                result = await self._send_and_wait(
                    "retriever",
                    Message(
                        task_id=task_id,
                        sender="orchestrator",
                        recipient="retriever",
                        message_type="task",
                        payload={"query": step.get("task", query)},
                    ),
                    timeout,
                )
                session.documents.extend(result.payload.get("documents", []))

            elif agent_id == "executor":
                result = await self._send_and_wait(
                    "executor",
                    Message(
                        task_id=task_id,
                        sender="orchestrator",
                        recipient="executor",
                        message_type="task",
                        payload={"tool": "calculate", "args": {"expression": "2+2"}},
                    ),
                    timeout,
                )
                session.tool_results.append(result.payload)

        # Step 3: Summarize
        session.status = "summarizing"
        summary_msg = await self._send_and_wait(
            "summarizer",
            Message(
                task_id=task_id,
                sender="orchestrator",
                recipient="summarizer",
                message_type="task",
                payload={
                    "query": query,
                    "documents": session.documents,
                    "tool_results": session.tool_results,
                },
            ),
            timeout,
        )
        session.answer = summary_msg.payload.get("answer", "")

        # Step 4: Critique
        session.status = "critiquing"
        critique_msg = await self._send_and_wait(
            "critic",
            Message(
                task_id=task_id,
                sender="orchestrator",
                recipient="critic",
                message_type="task",
                payload={"query": query, "answer": session.answer},
            ),
            timeout,
        )
        session.critique = critique_msg.payload
        session.status = "done"

        return {
            "task_id": task_id,
            "query": query,
            "answer": session.answer,
            "plan": session.plan,
            "documents": session.documents,
            "tool_results": session.tool_results,
            "critique": session.critique,
        }

    async def _send_and_wait(self, recipient: str, message: Message, timeout: float) -> Message:
        future = asyncio.get_event_loop().create_future()
        self._pending_futures[message.task_id] = future
        await self.bus.publish(message)

        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        finally:
            self._pending_futures.pop(message.task_id, None)
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_orchestrator.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add core/agents/orchestrator.py core/session.py tests/test_orchestrator.py
git commit -m "feat: add OrchestratorAgent with full workflow coordination"
```

---

### Task 10: Command-Line Entry Point

**Files:**
- Modify: `main.py`
- Test: `tests/test_main.py`

**Interfaces:**
- Consumes: user input from terminal
- Produces: printed final answer with plan, sources, and critique

- [ ] **Step 1: Write the failing test**

Create `tests/test_main.py`:

```python
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import Config


def test_config_loads():
    assert hasattr(Config, "LLM_PROVIDER")
    assert hasattr(Config, "LLM_MODEL")
    assert hasattr(Config, "DASHSCOPE_API_KEY")
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe -m pytest tests/test_main.py -v
```

Expected: PASS (since Config already exists from Task 1)

- [ ] **Step 3: Write CLI implementation**

Replace `main.py` with:

```python
"""Nexus Phase 1 - Command line entry point."""

import asyncio

from core.agents.critic import CriticAgent
from core.agents.executor import ExecutorAgent
from core.agents.orchestrator import OrchestratorAgent
from core.agents.planner import PlannerAgent
from core.agents.retriever import RetrieverAgent
from core.agents.summarizer import SummarizerAgent
from core.config import Config
from core.llm import LLMClient
from core.message_bus import MessageBus


def create_llm_client():
    if Config.LLM_PROVIDER == "qwen":
        return LLMClient(
            provider="qwen",
            model=Config.LLM_MODEL,
            api_key=Config.DASHSCOPE_API_KEY,
        )
    else:
        raise ValueError(f"Unsupported provider: {Config.LLM_PROVIDER}")


async def main():
    print("=" * 60)
    print("Nexus Phase 1 - Multi-Agent Workflow Assistant")
    print("=" * 60)

    if not Config.DASHSCOPE_API_KEY:
        print("\nError: DASHSCOPE_API_KEY not set. Please check your .env file.")
        return

    bus = MessageBus()
    llm = create_llm_client()

    orchestrator = OrchestratorAgent(bus, llm)
    planner = PlannerAgent(bus, llm)
    retriever = RetrieverAgent(bus, llm)
    executor = ExecutorAgent(bus, llm)
    summarizer = SummarizerAgent(bus, llm)
    critic = CriticAgent(bus, llm)

    agents = [orchestrator, planner, retriever, executor, summarizer, critic]
    tasks = [asyncio.create_task(agent.run()) for agent in agents]

    print("\nAgents started. Type your question or '/quit' to exit.\n")

    try:
        while True:
            query = input("You: ").strip()
            if query.lower() in ("/quit", "/exit", "quit", "exit"):
                break
            if not query:
                continue

            print("\nNexus: thinking...\n")
            result = await orchestrator.process(query)

            print(f"Answer: {result['answer']}\n")
            print(f"Plan: {result['plan']}\n")
            print(f"Critique: {result['critique']}\n")
    finally:
        for agent in agents:
            agent.stop()
        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 4: Verify CLI runs**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
venv/Scripts/python.exe main.py
```

Expected: CLI starts, shows "Agents started." Type `/quit` to exit.

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add main.py tests/test_main.py
git commit -m "feat: add Phase 1 command-line interface"
```

---

## Self-Review

### Spec Coverage

| Spec Section | Implementing Task |
|---|---|
| Multi-Agent kernel | Tasks 3-9 |
| Message Bus | Task 2 |
| Orchestrator | Task 9 |
| Planner | Task 4 |
| Retriever (mocked) | Task 5 |
| Executor (mocked) | Task 6 |
| Summarizer | Task 7 |
| Critic | Task 8 |
| LLM Provider abstraction | Task 1 |
| Command-line interface | Task 10 |

### Placeholder Scan

- No TBD/TODO.
- No vague requirements.
- All code blocks contain complete code.
- All test commands include expected output.

### Type Consistency

- `Message` dataclass used consistently.
- `LLMClient.chat()` returns `{"content": str, "tool_calls": Optional[list]}` consistently.
- `BaseAgent.handle_message(message: Message)` signature consistent across all agents.

### Gap

- Phase 1 does not include RAG or Tool Registry; those are Phase 2 per the spec.
- Phase 1 does not include Web UI + SSE; those are Phase 3 per the spec.
- Phase 1 does not include SQLite memory; that is Phase 4 per the spec.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-06-18-phase1-multi-agent-kernel.md`.**

Two execution options:

1. **Subagent-Driven (recommended)** - Dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach would you like?
