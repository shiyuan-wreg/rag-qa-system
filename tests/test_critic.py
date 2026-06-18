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
