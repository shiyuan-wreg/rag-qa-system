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
