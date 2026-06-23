import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from core.agents.executor import ExecutorAgent
from core.llm import LLMClient
from core.message import Message
from core.message_bus import MessageBus


@pytest.mark.asyncio
async def test_executor_calculate_via_http():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    executor = ExecutorAgent(bus, llm)

    # Mock httpx.AsyncClient constructor
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "4"}
    mock_response.raise_for_status = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("core.agents.executor.httpx.AsyncClient", return_value=mock_client):
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
async def test_executor_http_error():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    executor = ExecutorAgent(bus, llm)

    # Mock httpx.AsyncClient to raise exception
    mock_client = MagicMock()
    mock_client.post = AsyncMock(side_effect=Exception("Connection refused"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("core.agents.executor.httpx.AsyncClient", return_value=mock_client):
        task = asyncio.create_task(executor.run())

        request = Message(
            task_id="t2",
            sender="orchestrator",
            recipient="executor",
            message_type="task",
            payload={"tool": "calculate", "args": {"expression": "2 + 2"}},
        )

        result = await bus.send_and_wait("executor", request, timeout=1.0)
        assert "工具执行失败" in result.payload["result"]

        executor.stop()
        await asyncio.wait_for(task, timeout=1.0)


@pytest.mark.asyncio
async def test_executor_http_500():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    executor = ExecutorAgent(bus, llm)

    # Mock httpx.AsyncClient to return 500 response
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock(side_effect=Exception("500 Internal Server Error"))
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("core.agents.executor.httpx.AsyncClient", return_value=mock_client):
        task = asyncio.create_task(executor.run())

        request = Message(
            task_id="t3",
            sender="orchestrator",
            recipient="executor",
            message_type="task",
            payload={"tool": "calculate", "args": {"expression": "2 + 2"}},
        )

        result = await bus.send_and_wait("executor", request, timeout=1.0)
        assert "工具执行失败" in result.payload["result"]

        executor.stop()
        await asyncio.wait_for(task, timeout=1.0)
