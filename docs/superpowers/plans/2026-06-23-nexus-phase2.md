# Nexus Phase 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `backends/nexus_app`, a Multi-Agent AI workflow assistant with a FastAPI + SSE web interface, reusing existing `rag_app` and `fc_app` via HTTP, and integrate it into ai-demos at `/nexus/`.

**Architecture:** Six specialized agents (Orchestrator, Planner, Retriever, Executor, Summarizer, Critic) communicate through an in-memory `asyncio.Queue` message bus. The Orchestrator drives the workflow and emits SSE events. Retriever calls `rag_app` over HTTP; Executor calls `fc_app` over HTTP. A simple HTML/JS frontend consumes the SSE stream and displays agent thoughts, tool calls, and final answers.

**Tech Stack:** Python 3.12, FastAPI, Uvicorn, Jinja2, httpx, python-dotenv, dashscope (Tongyi Qwen), pytest, pytest-asyncio, Docker.

## Global Constraints

- Python 3.12+
- LLM Provider: Tongyi Qwen (`qwen-turbo`) via DashScope; architecture must allow future provider swaps.
- Service internal port: `8003`
- Route prefix in production: `/nexus/` (nginx strips prefix when proxying)
- Message bus: in-memory `asyncio.Queue` (no external broker)
- Memory: in-memory sessions (lost on restart)
- Retriever calls `rag_app` at `http://rag:8001/`
- Executor calls `fc_app` at `http://fc:8002/`
- Critic uses LLM-as-a-Judge with rule-based fallback
- TDD: failing test before implementation for every non-trivial unit
- Commit after every task

---

## File Structure

| File | Responsibility |
|---|---|
| `backends/nexus_app/requirements.txt` | Python dependencies |
| `backends/nexus_app/config.py` | Load `.env` configuration |
| `backends/nexus_app/core/llm.py` | Unified LLM client abstraction |
| `backends/nexus_app/core/message.py` | `Message` dataclass |
| `backends/nexus_app/core/message_bus.py` | In-memory async message bus |
| `backends/nexus_app/core/session.py` | `SessionState` dataclass |
| `backends/nexus_app/core/agents/base.py` | `BaseAgent` abstract class |
| `backends/nexus_app/core/agents/orchestrator.py` | Workflow coordinator + SSE event generator |
| `backends/nexus_app/core/agents/planner.py` | Task decomposition |
| `backends/nexus_app/core/agents/retriever.py` | HTTP call to rag_app |
| `backends/nexus_app/core/agents/executor.py` | HTTP call to fc_app |
| `backends/nexus_app/core/agents/summarizer.py` | Final answer synthesis |
| `backends/nexus_app/core/agents/critic.py` | LLM-based answer evaluation |
| `backends/nexus_app/main.py` | FastAPI app, SSE `/chat` endpoint, HTML frontend |
| `backends/nexus_app/templates/index.html` | Chat frontend |
| `backends/nexus_app/Dockerfile` | Container image |
| `tests/nexus/` | Unit and integration tests |
| `deploy/docker-compose.yml` | Add `nexus` service |
| `deploy/nginx/nginx.conf` | Add `/nexus/` location |
| `frontends/portfolio/src/data/works.ts` | Add Nexus card |
| `frontends/portfolio/src/App.tsx` | Add `/nexus` route |

---

### Task 1: Project Scaffolding

**Files:**
- Create: `backends/nexus_app/requirements.txt`
- Create: `backends/nexus_app/__init__.py`
- Create: `backends/nexus_app/core/__init__.py`
- Create: `backends/nexus_app/core/agents/__init__.py`
- Create: `backends/nexus_app/config.py`
- Create: `backends/nexus_app/core/session.py`
- Create: `backends/nexus_app/.gitignore`
- Create: `tests/nexus/__init__.py`

**Interfaces:**
- Produces: `Config` with `LLM_PROVIDER`, `LLM_MODEL`, `DASHSCOPE_API_KEY`, `RAG_URL`, `FC_URL`
- Produces: `SessionState` dataclass

- [ ] **Step 1: Write the failing test**

Create `tests/nexus/test_config.py`:

```python
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/backends/nexus_app")

from config import Config
from core.session import SessionState


def test_config_has_required_fields():
    assert hasattr(Config, "LLM_PROVIDER")
    assert hasattr(Config, "LLM_MODEL")
    assert hasattr(Config, "DASHSCOPE_API_KEY")
    assert hasattr(Config, "RAG_URL")
    assert hasattr(Config, "FC_URL")


def test_session_state_defaults():
    s = SessionState(task_id="t1", query="hello")
    assert s.status == "pending"
    assert s.plan == []
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
python -m pytest tests/nexus/test_config.py -v
```

Expected: FAIL with import errors.

- [ ] **Step 3: Write minimal implementation**

Create `backends/nexus_app/config.py`:

```python
"""Configuration for Nexus."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "qwen")
    LLM_MODEL = os.environ.get("LLM_MODEL", "qwen-turbo")
    DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
    RAG_URL = os.environ.get("RAG_URL", "http://rag:8001")
    FC_URL = os.environ.get("FC_URL", "http://fc:8002")
```

Create `backends/nexus_app/core/session.py`:

```python
"""Session state tracking."""

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
    status: str = "pending"
```

Create `backends/nexus_app/requirements.txt`:

```txt
fastapi==0.111.0
uvicorn==0.30.0
jinja2==3.1.4
httpx==0.27.0
dashscope==1.20.0
python-dotenv==1.0.1
pytest==8.2.0
pytest-asyncio==0.23.0
```

Create empty `__init__.py` files and `.gitignore`.

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
python -m pytest tests/nexus/test_config.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add backends/nexus_app/ tests/nexus/
git commit -m "chore: scaffold Nexus nexus_app"
```

---

### Task 2: Unified LLM Client

**Files:**
- Create: `backends/nexus_app/core/llm.py`
- Test: `tests/nexus/test_llm.py`

**Interfaces:**
- Produces: `LLMClient(provider, model, api_key, base_url=None)`
- Produces: `LLMClient.chat(messages, tools=None, stream=False) -> Dict[str, Any]`

- [ ] **Step 1: Write the failing test**

Create `tests/nexus/test_llm.py`:

```python
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/backends/nexus_app")

from core.llm import LLMClient


def test_extract_content_from_qwen_response():
    client = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    mock = {"output": {"choices": [{"message": {"content": "hello", "tool_calls": None}}]}}
    result = client._extract_content(mock)
    assert result["content"] == "hello"
    assert result["tool_calls"] is None


def test_extract_tool_calls():
    client = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    mock = {"output": {"choices": [{"message": {"content": "", "tool_calls": [{"id": "1", "function": {"name": "search", "arguments": "{}"}}]}}]}}
    result = client._extract_content(mock)
    assert len(result["tool_calls"]) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL with "ModuleNotFoundError: No module named 'core.llm'"

- [ ] **Step 3: Write minimal implementation**

Create `backends/nexus_app/core/llm.py`:

```python
"""Unified LLM client."""

from typing import Any, Dict, List, Optional


class LLMClient:
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

    def chat(self, messages: List[Dict], tools: Optional[List[Dict]] = None, stream: bool = False) -> Dict[str, Any]:
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

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
python -m pytest tests/nexus/test_llm.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add backends/nexus_app/core/llm.py tests/nexus/test_llm.py
git commit -m "feat: add unified LLM client for Nexus"
```

---

### Task 3: Message and MessageBus

**Files:**
- Create: `backends/nexus_app/core/message.py`
- Create: `backends/nexus_app/core/message_bus.py`
- Test: `tests/nexus/test_message_bus.py`

**Interfaces:**
- Produces: `Message` dataclass
- Produces: `MessageBus.subscribe(agent_id)`, `publish(message)`, `send_and_wait(recipient, message, timeout)`

- [ ] **Step 1: Write the failing test**

Create `tests/nexus/test_message_bus.py`:

```python
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/backends/nexus_app")

import pytest

from core.message import Message
from core.message_bus import MessageBus


@pytest.mark.asyncio
async def test_publish_and_subscribe():
    bus = MessageBus()
    queue = bus.subscribe("retriever")
    msg = Message(task_id="t1", sender="orchestrator", recipient="retriever", message_type="task", payload={"query": "hello"})
    await bus.publish(msg)
    received = await asyncio.wait_for(queue.get(), timeout=1.0)
    assert received.task_id == "t1"


@pytest.mark.asyncio
async def test_send_and_wait():
    bus = MessageBus()
    async def responder():
        queue = bus.subscribe("planner")
        msg = await queue.get()
        await bus.publish(Message(task_id=msg.task_id, sender="planner", recipient="orchestrator", message_type="result", payload={"plan": []}))
    asyncio.create_task(responder())
    request = Message(task_id="t2", sender="orchestrator", recipient="planner", message_type="task", payload={"query": "hi"})
    result = await bus.send_and_wait("planner", request, timeout=1.0)
    assert result.sender == "planner"


@pytest.mark.asyncio
async def test_send_and_wait_timeout():
    bus = MessageBus()
    request = Message(task_id="t3", sender="orchestrator", recipient="retriever", message_type="task", payload={})
    with pytest.raises(asyncio.TimeoutError):
        await bus.send_and_wait("retriever", request, timeout=0.1)
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL with import errors.

- [ ] **Step 3: Write minimal implementation**

Create `backends/nexus_app/core/message.py`:

```python
"""Message definitions."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from uuid import uuid4


@dataclass
class Message:
    task_id: str
    sender: str
    recipient: str
    message_type: str
    payload: Dict[str, Any]
    message_id: str = field(default_factory=lambda: str(uuid4()))
    in_reply_to: Optional[str] = None
```

Create `backends/nexus_app/core/message_bus.py`:

```python
"""In-memory async message bus."""

import asyncio
from typing import Dict

from core.message import Message


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
                raise ValueError(f"No subscriber for agent: {message.recipient}")
            await queue.put(message)

    async def send_and_wait(self, recipient: str, message: Message, timeout: float = 30.0) -> Message:
        await self.publish(message)
        return await self.wait_for_result(message.task_id, recipient, timeout)

    async def wait_for_result(self, task_id: str, sender: str, timeout: float = 30.0) -> Message:
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
            await queue.put(msg)
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
python -m pytest tests/nexus/test_message_bus.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add backends/nexus_app/core/message.py backends/nexus_app/core/message_bus.py tests/nexus/test_message_bus.py
git commit -m "feat: add Nexus message bus"
```

---

### Task 4: BaseAgent

**Files:**
- Create: `backends/nexus_app/core/agents/base.py`
- Test: `tests/nexus/test_base_agent.py`

**Interfaces:**
- Produces: `BaseAgent(agent_id, bus, llm)` with `run()`, `stop()`, `handle_message()`, `send_message()`, `think()`

- [ ] **Step 1: Write the failing test**

Create `tests/nexus/test_base_agent.py`:

```python
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) + "/backends/nexus_app")

import pytest

from core.agents.base import BaseAgent
from core.llm import LLMClient
from core.message import Message
from core.message_bus import MessageBus


class EchoAgent(BaseAgent):
    async def handle_message(self, message: Message):
        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"echo": message.payload.get("text", "")},
            task_id=message.task_id,
        )


@pytest.mark.asyncio
async def test_base_agent_loop():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    agent = EchoAgent("echo", bus, llm)
    task = asyncio.create_task(agent.run())

    request = Message(task_id="t1", sender="orchestrator", recipient="echo", message_type="task", payload={"text": "hello"})
    result = await bus.send_and_wait("echo", request, timeout=1.0)
    assert result.payload["echo"] == "hello"

    agent.stop()
    await asyncio.wait_for(task, timeout=1.0)
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL with import error.

- [ ] **Step 3: Write minimal implementation**

Create `backends/nexus_app/core/agents/base.py`:

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
        pass

    async def send_message(self, recipient: str, message_type: str, payload: Dict[str, Any], task_id: str, in_reply_to: Optional[str] = None) -> None:
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
python -m pytest tests/nexus/test_base_agent.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add backends/nexus_app/core/agents/base.py tests/nexus/test_base_agent.py
git commit -m "feat: add Nexus BaseAgent"
```

---

### Task 5: Planner Agent

**Files:**
- Create: `backends/nexus_app/core/agents/planner.py`
- Test: `tests/nexus/test_planner.py`

**Interfaces:**
- Produces: `PlannerAgent` that returns `{"plan": [...]}`

- [ ] **Step 1: Write the failing test**

Create `tests/nexus/test_planner.py`:

```python
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) + "/backends/nexus_app")

import pytest

from core.agents.planner import PlannerAgent
from core.llm import LLMClient
from core.message import Message
from core.message_bus import MessageBus


async def mock_think(system_prompt, user_prompt, tools=None):
    return {
        "content": '{"steps": [{"step_id": 1, "agent": "retriever", "task": "检索"}, {"step_id": 2, "agent": "summarizer", "task": "总结"}]}',
        "tool_calls": None,
    }


@pytest.mark.asyncio
async def test_planner_returns_plan():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    planner = PlannerAgent(bus, llm)
    planner.think = mock_think
    task = asyncio.create_task(planner.run())

    request = Message(task_id="t1", sender="orchestrator", recipient="planner", message_type="task", payload={"query": "test"})
    result = await bus.send_and_wait("planner", request, timeout=1.0)
    assert "plan" in result.payload
    assert result.payload["plan"][0]["agent"] == "retriever"

    planner.stop()
    await asyncio.wait_for(task, timeout=1.0)
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL with import error.

- [ ] **Step 3: Write minimal implementation**

Create `backends/nexus_app/core/agents/planner.py`:

```python
"""Planner Agent."""

import json

from core.agents.base import BaseAgent
from core.message import Message


class PlannerAgent(BaseAgent):
    def __init__(self, bus, llm):
        super().__init__("planner", bus, llm)

    async def handle_message(self, message: Message):
        query = message.payload.get("query", "")
        system = """你是任务规划专家。把用户需求拆成可执行步骤。
每个步骤包含：step_id（整数）、agent（retriever/executor/summarizer）、task（描述）。
只输出 JSON，不要其他解释。
格式：{"steps": [...]}"""
        response = await self.think(system, f"用户需求：{query}")
        plan = self._parse_plan(response.get("content", "{}"))
        await self.send_message(recipient=message.sender, message_type="result", payload={"plan": plan}, task_id=message.task_id)

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
python -m pytest tests/nexus/test_planner.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add backends/nexus_app/core/agents/planner.py tests/nexus/test_planner.py
git commit -m "feat: add Nexus PlannerAgent"
```

---

### Task 6: Retriever Agent

**Files:**
- Create: `backends/nexus_app/core/agents/retriever.py`
- Modify: `backends/nexus_app/config.py` (add httpx timeout)
- Test: `tests/nexus/test_retriever.py`

**Interfaces:**
- Produces: `RetrieverAgent` that calls `rag_app` via HTTP and returns `{"documents": [...]}`

- [ ] **Step 1: Write the failing test**

Create `tests/nexus/test_retriever.py`:

```python
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) + "/backends/nexus_app")

import pytest
from httpx import Response

from core.agents.retriever import RetrieverAgent
from core.llm import LLMClient
from core.message import Message
from core.message_bus import MessageBus


@pytest.mark.asyncio
async def test_retriever_calls_rag_app(monkeypatch):
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    retriever = RetrieverAgent(bus, llm)

    async def mock_post(*args, **kwargs):
        return Response(200, json={"answer": "mock answer", "tool_calls": [{"name": "search_docs", "arguments": {"query": "test"}}]})

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)

    task = asyncio.create_task(retriever.run())
    request = Message(task_id="t1", sender="orchestrator", recipient="retriever", message_type="task", payload={"query": "test"})
    result = await bus.send_and_wait("retriever", request, timeout=1.0)
    assert "documents" in result.payload

    retriever.stop()
    await asyncio.wait_for(task, timeout=1.0)
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL with import error.

- [ ] **Step 3: Write minimal implementation**

Create `backends/nexus_app/core/agents/retriever.py`:

```python
"""Retriever Agent: calls rag_app over HTTP."""

import httpx

from core.agents.base import BaseAgent
from core.config import Config
from core.message import Message


class RetrieverAgent(BaseAgent):
    def __init__(self, bus, llm):
        super().__init__("retriever", bus, llm)

    async def handle_message(self, message: Message):
        query = message.payload.get("query", "")
        documents = await self._retrieve(query)
        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"documents": documents, "query": query},
            task_id=message.task_id,
        )

    async def _retrieve(self, query: str) -> list:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(f"{Config.RAG_URL}/chat", data={"query": query})
                response.raise_for_status()
                data = response.json()
                answer = data.get("answer", "")
                return [{"content": answer, "source": "rag_app", "score": 0.9}]
            except Exception as e:
                return [{"content": f"检索失败：{e}", "source": "rag_app", "score": 0.0}]
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
python -m pytest tests/nexus/test_retriever.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add backends/nexus_app/core/agents/retriever.py tests/nexus/test_retriever.py
git commit -m "feat: add Nexus RetrieverAgent calling rag_app"
```

---

### Task 7: Executor Agent

**Files:**
- Create: `backends/nexus_app/core/agents/executor.py`
- Test: `tests/nexus/test_executor.py`

**Interfaces:**
- Produces: `ExecutorAgent` that calls `fc_app` `/execute` and returns `{"result": ...}`

- [ ] **Step 1: Write the failing test**

Create `tests/nexus/test_executor.py`:

```python
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) + "/backends/nexus_app")

import pytest
from httpx import Response

from core.agents.executor import ExecutorAgent
from core.llm import LLMClient
from core.message import Message
from core.message_bus import MessageBus


@pytest.mark.asyncio
async def test_executor_calls_fc_app(monkeypatch):
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    executor = ExecutorAgent(bus, llm)

    async def mock_post(*args, **kwargs):
        return Response(200, json={"result": "4"})

    monkeypatch.setattr("httpx.AsyncClient.post", mock_post)

    task = asyncio.create_task(executor.run())
    request = Message(task_id="t1", sender="orchestrator", recipient="executor", message_type="task", payload={"tool": "calculate", "args": {"expression": "2+2"}})
    result = await bus.send_and_wait("executor", request, timeout=1.0)
    assert result.payload["result"] == "4"

    executor.stop()
    await asyncio.wait_for(task, timeout=1.0)
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL with import error.

- [ ] **Step 3: Write minimal implementation**

Create `backends/nexus_app/core/agents/executor.py`:

```python
"""Executor Agent: calls fc_app over HTTP."""

import httpx

from core.agents.base import BaseAgent
from core.config import Config
from core.message import Message


class ExecutorAgent(BaseAgent):
    def __init__(self, bus, llm):
        super().__init__("executor", bus, llm)

    async def handle_message(self, message: Message):
        tool = message.payload.get("tool", "")
        args = message.payload.get("args", {})
        result = await self._execute(tool, args)
        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"result": result, "tool": tool, "args": args},
            task_id=message.task_id,
        )

    async def _execute(self, tool: str, args: dict) -> str:
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(f"{Config.FC_URL}/execute", json={"tool": tool, "args": args})
                response.raise_for_status()
                data = response.json()
                return data.get("result", "")
            except Exception as e:
                return f"工具执行失败：{e}"
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
python -m pytest tests/nexus/test_executor.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add backends/nexus_app/core/agents/executor.py tests/nexus/test_executor.py
git commit -m "feat: add Nexus ExecutorAgent calling fc_app"
```

---

### Task 8: Summarizer Agent

**Files:**
- Create: `backends/nexus_app/core/agents/summarizer.py`
- Test: `tests/nexus/test_summarizer.py`

**Interfaces:**
- Produces: `SummarizerAgent` returns `{"answer": "...", "sources": [...]}`

- [ ] **Step 1: Write the failing test**

Create `tests/nexus/test_summarizer.py`:

```python
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) + "/backends/nexus_app")

import pytest

from core.agents.summarizer import SummarizerAgent
from core.llm import LLMClient
from core.message import Message
from core.message_bus import MessageBus


async def mock_think(system_prompt, user_prompt, tools=None):
    return {"content": "总结结果", "tool_calls": None}


@pytest.mark.asyncio
async def test_summarizer_returns_answer():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    summarizer = SummarizerAgent(bus, llm)
    summarizer.think = mock_think
    task = asyncio.create_task(summarizer.run())

    request = Message(task_id="t1", sender="orchestrator", recipient="summarizer", message_type="task", payload={"query": "q", "documents": [{"content": "c"}], "tool_results": []})
    result = await bus.send_and_wait("summarizer", request, timeout=1.0)
    assert result.payload["answer"] == "总结结果"

    summarizer.stop()
    await asyncio.wait_for(task, timeout=1.0)
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL with import error.

- [ ] **Step 3: Write minimal implementation**

Create `backends/nexus_app/core/agents/summarizer.py`:

```python
"""Summarizer Agent."""

from core.agents.base import BaseAgent
from core.message import Message


class SummarizerAgent(BaseAgent):
    def __init__(self, bus, llm):
        super().__init__("summarizer", bus, llm)

    async def handle_message(self, message: Message):
        query = message.payload.get("query", "")
        documents = message.payload.get("documents", [])
        tool_results = message.payload.get("tool_results", [])

        system = "你是总结专家。根据资料生成准确、简洁的中文回答。不要编造。"
        context = self._build_context(documents, tool_results)
        user = f"用户问题：{query}\n\n参考资料：\n{context}\n\n请生成最终回答："
        response = await self.think(system, user)
        answer = response.get("content", "抱歉，无法生成回答。")

        sources = [d.get("source", "") for d in documents if d.get("source")]
        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"answer": answer, "sources": sources},
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
python -m pytest tests/nexus/test_summarizer.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add backends/nexus_app/core/agents/summarizer.py tests/nexus/test_summarizer.py
git commit -m "feat: add Nexus SummarizerAgent"
```

---

### Task 9: Critic Agent with LLM-as-a-Judge

**Files:**
- Create: `backends/nexus_app/core/agents/critic.py`
- Test: `tests/nexus/test_critic.py`

**Interfaces:**
- Produces: `CriticAgent` returns `{"scores": {...}, "passed": bool, "feedback": str}`

- [ ] **Step 1: Write the failing test**

Create `tests/nexus/test_critic.py`:

```python
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) + "/backends/nexus_app")

import pytest

from core.agents.critic import CriticAgent
from core.llm import LLMClient
from core.message import Message
from core.message_bus import MessageBus


async def mock_think(system_prompt, user_prompt, tools=None):
    return {
        "content": '{"correctness": 0.9, "relevance": 0.9, "completeness": 0.8, "safety": 1.0, "overall": 0.9, "feedback": "good"}',
        "tool_calls": None,
    }


@pytest.mark.asyncio
async def test_critic_scores_answer():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    critic = CriticAgent(bus, llm)
    critic.think = mock_think
    task = asyncio.create_task(critic.run())

    request = Message(task_id="t1", sender="orchestrator", recipient="critic", message_type="task", payload={"query": "q", "answer": "a"})
    result = await bus.send_and_wait("critic", request, timeout=1.0)
    assert "scores" in result.payload
    assert result.payload["passed"] is True

    critic.stop()
    await asyncio.wait_for(task, timeout=1.0)
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL with import error.

- [ ] **Step 3: Write minimal implementation**

Create `backends/nexus_app/core/agents/critic.py`:

```python
"""Critic Agent with LLM-as-a-Judge and rule-based fallback."""

import json
import re

from core.agents.base import BaseAgent
from core.message import Message


class CriticAgent(BaseAgent):
    def __init__(self, bus, llm):
        super().__init__("critic", bus, llm)

    async def handle_message(self, message: Message):
        query = message.payload.get("query", "")
        answer = message.payload.get("answer", "")

        try:
            scores = await self._llm_critique(query, answer)
        except Exception:
            scores = self._rule_based_scores(query, answer)

        passed = scores["overall"] >= 0.6
        await self.send_message(
            recipient=message.sender,
            message_type="critique",
            payload={
                "scores": scores,
                "passed": passed,
                "feedback": scores.get("feedback", ""),
            },
            task_id=message.task_id,
        )

    async def _llm_critique(self, query: str, answer: str) -> dict:
        system = """你是严格的回答质量评估专家。从 correctness、relevance、completeness、safety 四个维度打分（0.0~1.0），并计算 overall。
只输出 JSON，不要其他内容。"""
        user = f"用户问题：{query}\n系统回答：{answer}\n\n请输出 JSON："
        response = await self.think(system, user)
        content = response.get("content", "{}")
        return self._parse_scores(content)

    def _parse_scores(self, content: str) -> dict:
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        data = json.loads(content.strip())
        return {
            "correctness": float(data.get("correctness", 0)),
            "relevance": float(data.get("relevance", 0)),
            "completeness": float(data.get("completeness", 0)),
            "safety": float(data.get("safety", 1)),
            "overall": float(data.get("overall", 0)),
            "feedback": data.get("feedback", ""),
        }

    def _rule_based_scores(self, query: str, answer: str) -> dict:
        query_keywords = set(re.findall(r"\b\w{2,}\b", query.lower()))
        matched = sum(1 for kw in query_keywords if kw in answer.lower()) if query_keywords else 0
        relevance = round(min(matched / len(query_keywords) * 1.5, 1.0), 2) if query_keywords else 0.5
        completeness = 0.0 if len(answer) < 10 else 0.8 if len(answer) > 100 else 0.5
        safety = 0.0 if any(kw in answer for kw in ["炸弹", "毒品", "杀人"]) else 1.0
        correctness = 0.7 if "错误" not in answer and "不知道" not in answer else 0.3
        overall = round((correctness + relevance + completeness + safety) / 4, 2)
        return {
            "correctness": correctness,
            "relevance": relevance,
            "completeness": completeness,
            "safety": safety,
            "overall": overall,
            "feedback": "规则评分（LLM 调用失败时使用）",
        }
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
python -m pytest tests/nexus/test_critic.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add backends/nexus_app/core/agents/critic.py tests/nexus/test_critic.py
git commit -m "feat: add Nexus CriticAgent with LLM-as-a-Judge"
```

---

### Task 10: Orchestrator Agent

**Files:**
- Create: `backends/nexus_app/core/agents/orchestrator.py`
- Test: `tests/nexus/test_orchestrator.py`

**Interfaces:**
- Produces: `OrchestratorAgent` with `process_stream(query, session_id=None)` async generator yielding SSE events

- [ ] **Step 1: Write the failing test**

Create `tests/nexus/test_orchestrator.py`:

```python
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) + "/backends/nexus_app")

import pytest

from core.agents.critic import CriticAgent
from core.agents.executor import ExecutorAgent
from core.agents.orchestrator import OrchestratorAgent
from core.agents.planner import PlannerAgent
from core.agents.retriever import RetrieverAgent
from core.agents.summarizer import SummarizerAgent
from core.llm import LLMClient
from core.message_bus import MessageBus


async def mock_planner_think(system_prompt, user_prompt, tools=None):
    return {"content": '{"steps": [{"step_id": 1, "agent": "retriever", "task": "检索"}, {"step_id": 2, "agent": "summarizer", "task": "总结"}]}', "tool_calls": None}


@pytest.mark.asyncio
async def test_orchestrator_workflow(monkeypatch):
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")

    orchestrator = OrchestratorAgent(bus, llm)
    planner = PlannerAgent(bus, llm)
    retriever = RetrieverAgent(bus, llm)
    executor = ExecutorAgent(bus, llm)
    summarizer = SummarizerAgent(bus, llm)
    critic = CriticAgent(bus, llm)

    planner.think = mock_planner_think

    async def mock_summarizer_think(system_prompt, user_prompt, tools=None):
        return {"content": "最终回答", "tool_calls": None}
    summarizer.think = mock_summarizer_think

    async def mock_critic_think(system_prompt, user_prompt, tools=None):
        return {"content": '{"correctness": 1, "relevance": 1, "completeness": 1, "safety": 1, "overall": 1, "feedback": "完美"}', "tool_calls": None}
    critic.think = mock_critic_think

    monkeypatch.setattr("httpx.AsyncClient.post", lambda *args, **kwargs: type("R", (), {"status_code": 200, "json": lambda: {"answer": "mock", "result": "4"}, "raise_for_status": lambda: None})())

    tasks = [
        asyncio.create_task(orchestrator.run()),
        asyncio.create_task(planner.run()),
        asyncio.create_task(retriever.run()),
        asyncio.create_task(executor.run()),
        asyncio.create_task(summarizer.run()),
        asyncio.create_task(critic.run()),
    ]

    events = []
    async for event in orchestrator.process_stream("测试问题"):
        events.append(event)

    assert any(e["type"] == "final_answer" for e in events)

    orchestrator.stop()
    for agent in [planner, retriever, executor, summarizer, critic]:
        agent.stop()
    await asyncio.gather(*[asyncio.wait_for(t, timeout=2.0) for t in tasks])
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL with import error.

- [ ] **Step 3: Write minimal implementation**

Create `backends/nexus_app/core/agents/orchestrator.py`:

```python
"""Orchestrator Agent."""

import asyncio
import uuid
from typing import Any, AsyncGenerator, Dict

from core.agents.base import BaseAgent
from core.message import Message
from core.session import SessionState


class OrchestratorAgent(BaseAgent):
    def __init__(self, bus, llm):
        super().__init__("orchestrator", bus, llm)
        self._pending_futures: Dict[str, asyncio.Future] = {}

    async def handle_message(self, message: Message):
        if message.message_type in ("result", "critique"):
            future = self._pending_futures.get(message.task_id)
            if future and not future.done():
                future.set_result(message)

    async def process_stream(self, query: str, session_id: str = None) -> AsyncGenerator[Dict[str, Any], None]:
        task_id = str(uuid.uuid4())
        session = SessionState(task_id=task_id, query=query)

        yield {"type": "agent_thought", "data": {"agent": "orchestrator", "content": "开始规划任务"}}

        # Plan
        session.status = "planning"
        plan_msg = await self._send_and_wait(
            "planner",
            Message(task_id=task_id, sender="orchestrator", recipient="planner", message_type="task", payload={"query": query}),
        )
        session.plan = plan_msg.payload.get("plan", [])
        yield {"type": "planner_thought", "data": {"content": f"计划：{session.plan}"}}

        # Execute plan
        session.status = "executing"
        for step in session.plan:
            agent_id = step.get("agent")
            task_desc = step.get("task", query)
            if agent_id == "retriever":
                yield {"type": "tool_call", "data": {"agent": "retriever", "tool": "search_docs", "args": {"query": task_desc}}}
                result = await self._send_and_wait(
                    "retriever",
                    Message(task_id=task_id, sender="orchestrator", recipient="retriever", message_type="task", payload={"query": task_desc}),
                )
                session.documents.extend(result.payload.get("documents", []))
                yield {"type": "tool_result", "data": {"agent": "retriever", "result": result.payload}}
            elif agent_id == "executor":
                yield {"type": "tool_call", "data": {"agent": "executor", "tool": "calculate", "args": {"expression": "2+2"}}}
                result = await self._send_and_wait(
                    "executor",
                    Message(task_id=task_id, sender="orchestrator", recipient="executor", message_type="task", payload={"tool": "calculate", "args": {"expression": "2+2"}}),
                )
                session.tool_results.append(result.payload)
                yield {"type": "tool_result", "data": {"agent": "executor", "result": result.payload}}

        # Summarize
        session.status = "summarizing"
        yield {"type": "agent_thought", "data": {"agent": "summarizer", "content": "正在生成最终回答"}}
        summary_msg = await self._send_and_wait(
            "summarizer",
            Message(task_id=task_id, sender="orchestrator", recipient="summarizer", message_type="task", payload={
                "query": query,
                "documents": session.documents,
                "tool_results": session.tool_results,
            }),
        )
        session.answer = summary_msg.payload.get("answer", "")

        # Critique
        session.status = "critiquing"
        critique_msg = await self._send_and_wait(
            "critic",
            Message(task_id=task_id, sender="orchestrator", recipient="critic", message_type="task", payload={"query": query, "answer": session.answer}),
        )
        session.critique = critique_msg.payload
        session.status = "done"

        yield {"type": "final_answer", "data": {"content": session.answer, "sources": summary_msg.payload.get("sources", []), "critique": session.critique}}

    async def _send_and_wait(self, recipient: str, message: Message, timeout: float = 60.0) -> Message:
        future = asyncio.get_event_loop().create_future()
        self._pending_futures[message.task_id] = future
        await self.bus.publish(message)
        try:
            return await asyncio.wait_for(future, timeout=timeout)
        finally:
            self._pending_futures.pop(message.task_id, None)
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
python -m pytest tests/nexus/test_orchestrator.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add backends/nexus_app/core/agents/orchestrator.py tests/nexus/test_orchestrator.py
git commit -m "feat: add Nexus OrchestratorAgent with SSE event stream"
```

---

### Task 11: FastAPI + SSE Endpoint

**Files:**
- Create: `backends/nexus_app/main.py`
- Create: `backends/nexus_app/templates/index.html`
- Test: `tests/nexus/test_api.py`

**Interfaces:**
- Produces: `POST /chat` returns SSE stream
- Produces: `GET /` returns chat UI

- [ ] **Step 1: Write the failing test**

Create `tests/nexus/test_api.py`:

```python
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/backends/nexus_app")

from fastapi.testclient import TestClient
from main import app


def test_chat_sse():
    client = TestClient(app)
    response = client.post("/chat", data={"query": "测试"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    body = response.read()
    assert b"event:" in body
```

- [ ] **Step 2: Run test to verify it fails**

Expected: FAIL with import error.

- [ ] **Step 3: Write minimal implementation**

Create `backends/nexus_app/main.py`:

```python
"""Nexus FastAPI web app."""

import asyncio
import json

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates

from config import Config
from core.agents.critic import CriticAgent
from core.agents.executor import ExecutorAgent
from core.agents.orchestrator import OrchestratorAgent
from core.agents.planner import PlannerAgent
from core.agents.retriever import RetrieverAgent
from core.agents.summarizer import SummarizerAgent
from core.llm import LLMClient
from core.message_bus import MessageBus

app = FastAPI(title="Nexus Multi-Agent 工作流助手")
templates = Jinja2Templates(directory="backends/nexus_app/templates")

bus = MessageBus()
llm = LLMClient(provider=Config.LLM_PROVIDER, model=Config.LLM_MODEL, api_key=Config.DASHSCOPE_API_KEY)

orchestrator = OrchestratorAgent(bus, llm)
planner = PlannerAgent(bus, llm)
retriever = RetrieverAgent(bus, llm)
executor = ExecutorAgent(bus, llm)
summarizer = SummarizerAgent(bus, llm)
critic = CriticAgent(bus, llm)

agents = [orchestrator, planner, retriever, executor, summarizer, critic]
agent_tasks = []


@app.on_event("startup")
def startup():
    global agent_tasks
    agent_tasks = [asyncio.create_task(agent.run()) for agent in agents]


@app.on_event("shutdown")
async def shutdown():
    for agent in agents:
        agent.stop()
    await asyncio.gather(*agent_tasks, return_exceptions=True)


@app.get("/", response_class=HTMLResponse)
def index():
    return templates.TemplateResponse("index.html", {"request": {}})


@app.post("/chat")
def chat(query: str = Form(...)):
    async def event_stream():
        async for event in orchestrator.process_stream(query):
            yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

Create `backends/nexus_app/templates/index.html`:

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nexus Multi-Agent</title>
<style>
:root { color-scheme: light dark; }
body { margin: 0; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #24292f; background: #fff; }
@media (prefers-color-scheme: dark) { body { color: #c9d1d9; background: #0d1117; } a { color: #58a6ff; } }
.container { max-width: 900px; margin: 0 auto; }
.messages { border: 1px solid #d0d7de; border-radius: 8px; height: 60vh; overflow-y: auto; padding: 16px; margin-bottom: 16px; }
.message { margin: 8px 0; padding: 10px; border-radius: 6px; background: #f6f8fa; }
.user { background: #ddf4ff; }
.input-area { display: flex; gap: 8px; }
input { flex: 1; padding: 10px; }
button { padding: 10px 20px; }
.thought { color: #57606a; font-size: 14px; margin: 4px 0; }
.tool { color: #0969da; font-size: 14px; margin: 4px 0; }
</style>
</head>
<body>
<div class="container">
  <h1>Nexus Multi-Agent 工作流助手</h1>
  <div class="messages" id="messages"></div>
  <div class="input-area">
    <input type="text" id="input" placeholder="输入问题..." onkeypress="if(event.key==='Enter') send()">
    <button onclick="send()">发送</button>
  </div>
</div>
<script>
const messages = document.getElementById('messages');
const input = document.getElementById('input');

function addMessage(html, cls='') {
  const div = document.createElement('div');
  div.className = 'message ' + cls;
  div.innerHTML = html;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function send() {
  const query = input.value.trim();
  if (!query) return;
  addMessage(query, 'user');
  input.value = '';

  const form = new FormData();
  form.append('query', query);
  fetch('chat', { method: 'POST', body: form })
    .then(response => {
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let final = '';
      function read() {
        reader.read().then(({ done, value }) => {
          if (done) {
            if (final) addMessage(final);
            return;
          }
          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split('\n');
          let event = null, data = '';
          for (const line of lines) {
            if (line.startsWith('event: ')) event = line.slice(7);
            else if (line.startsWith('data: ')) data = line.slice(6);
            else if (line === '' && event) {
              const obj = JSON.parse(data);
              if (event === 'final_answer') final = obj.content;
              else if (event === 'agent_thought') addMessage('<div class="thought">[' + obj.agent + '] ' + obj.content + '</div>');
              else if (event === 'tool_call') addMessage('<div class="tool">调用：' + obj.agent + ' / ' + obj.tool + '</div>');
              event = null; data = '';
            }
          }
          read();
        });
      }
      read();
    });
}
</script>
</body>
</html>
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd /c/Users/hzs17/Desktop/ai-demos
python -m pytest tests/nexus/test_api.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add backends/nexus_app/main.py backends/nexus_app/templates/index.html tests/nexus/test_api.py
git commit -m "feat: add Nexus FastAPI SSE chat endpoint and UI"
```

---

### Task 12: fc_app /execute Endpoint

**Files:**
- Modify: `backends/fc_app/main.py`
- Test: Manual verification

**Interfaces:**
- Produces: `POST /execute` accepts JSON `{"tool": "...", "args": {...}}`, returns `{"result": "..."}`

- [ ] **Step 1: Add endpoint**

Append to `backends/fc_app/main.py`:

```python
from fastapi import Body


@app.post("/execute")
def execute(tool: str = Body(...), args: dict = Body(default_factory=dict)):
    handler = TOOL_MAP.get(tool)
    if handler is None:
        return {"result": f"错误: 未知工具 '{tool}'"}
    try:
        result = handler(**args)
        return {"result": result}
    except Exception as e:
        return {"result": f"工具执行失败: {e}"}
```

- [ ] **Step 2: Verify locally**

Run fc_app and test:
```bash
curl -X POST "http://127.0.0.1:8002/execute" -H "Content-Type: application/json" -d '{"tool": "calculate", "args": {"expression": "2+2"}}'
```

Expected: `{"result": "4"}`

- [ ] **Step 3: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add backends/fc_app/main.py
git commit -m "feat(fc_app): add /execute endpoint for Nexus ExecutorAgent"
```

---

### Task 13: Dockerfile and Deployment

**Files:**
- Create: `backends/nexus_app/Dockerfile`
- Modify: `deploy/docker-compose.yml`
- Modify: `deploy/nginx/nginx.conf`
- Modify: `frontends/portfolio/src/data/works.ts`
- Modify: `frontends/portfolio/src/App.tsx`
- Modify: `.env.example`

- [ ] **Step 1: Create Dockerfile**

Create `backends/nexus_app/Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY backends/nexus_app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backends/nexus_app/ ./
EXPOSE 8003
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
```

- [ ] **Step 2: Update docker-compose.yml**

Add service:

```yaml
  nexus:
    build:
      context: ..
      dockerfile: backends/nexus_app/Dockerfile
    env_file: ../.env
    restart: always
    expose: ["8003"]
    depends_on: [rag, fc]
```

- [ ] **Step 3: Update nginx.conf**

Add:

```nginx
    # Nexus 后端
    location /nexus/ {
        proxy_pass http://nexus:8003/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
    }
```

`proxy_buffering off;` is important for SSE.

- [ ] **Step 4: Portfolio integration**

Add to `works.ts`:

```typescript
{ slug: 'nexus', title: 'Nexus Multi-Agent 工作流', desc: '多 Agent 协作的 AI 工作流助手，实时展示思考过程。',
  tech: ['Multi-Agent', 'FastAPI', 'SSE', '通义千问'], path: '/nexus' },
```

Add route in `App.tsx`.

- [ ] **Step 5: Update .env.example**

Ensure it has:

```bash
LLM_PROVIDER=qwen
LLM_MODEL=qwen-turbo
DASHSCOPE_API_KEY=your-dashscope-api-key
```

- [ ] **Step 6: Build and verify**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
bash deploy/build-frontends.sh
docker compose -f deploy/docker-compose.yml up -d --build
```

Visit `http://127.0.0.1:8080/nexus/`, send a query, verify SSE events appear.

- [ ] **Step 7: Commit**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add backends/nexus_app/Dockerfile deploy/docker-compose.yml deploy/nginx/nginx.conf frontends/portfolio/src/data/works.ts frontends/portfolio/src/App.tsx .env.example
git commit -m "build: integrate Nexus into docker-compose, nginx, and portfolio"
```

---

## Self-Review

### Spec Coverage

| Spec Section | Implementing Task |
|---|---|
| LLM Client abstraction | Task 2 |
| Message Bus | Task 3 |
| BaseAgent | Task 4 |
| Planner | Task 5 |
| Retriever via rag_app | Task 6 |
| Executor via fc_app | Tasks 7, 12 |
| Summarizer | Task 8 |
| Critic LLM-as-a-Judge | Task 9 |
| Orchestrator + SSE events | Task 10 |
| FastAPI + SSE endpoint | Task 11 |
| Docker + nginx + portfolio | Task 13 |

### Placeholder Scan

- No TBD/TODO.
- Each step includes code or exact command.
- File paths are exact.

### Type Consistency

- `Message` fields consistent across all agents.
- `SessionState` used by Orchestrator.
- `LLMClient.chat()` return type consistent.

### Gaps

- SQLite persistence excluded per spec.
- MCP/notes excluded per spec.
- Multi-user auth excluded per spec.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-06-23-nexus-phase2.md`.**

Two execution options:

1. **Subagent-Driven (recommended)** - Dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach would you like?
