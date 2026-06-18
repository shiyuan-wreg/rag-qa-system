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
