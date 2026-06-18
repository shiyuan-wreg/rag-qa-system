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
