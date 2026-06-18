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
