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
