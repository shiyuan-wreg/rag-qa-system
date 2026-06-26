import asyncio
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from core.agents.retriever import RetrieverAgent
from core.llm import LLMClient
from core.message import Message
from core.message_bus import MessageBus


@pytest.mark.asyncio
async def test_retriever_calls_rag_app_http():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    retriever = RetrieverAgent(bus, llm)

    # Mock httpx.AsyncClient.post to return a fake RAG response.
    # httpx 的 json()/raise_for_status() 是同步方法，必须用 MagicMock 而非 AsyncMock，
    # 否则就会重蹈那个 async bug（mock 与真实 httpx 行为不符，测试假通过）。
    mock_response = MagicMock()
    mock_response.json = MagicMock(return_value={"answer": "mock answer", "tool_calls": []})
    mock_response.raise_for_status = MagicMock()

    # Mock the async context manager properly
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
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
        assert len(result.payload["documents"]) == 1
        assert result.payload["documents"][0]["content"] == "mock answer"
        assert result.payload["documents"][0]["source"] == "rag_app"
        assert result.payload["documents"][0]["score"] == 0.9

        retriever.stop()
        await asyncio.wait_for(task, timeout=1.0)


@pytest.mark.asyncio
async def test_retriever_handles_http_error():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    retriever = RetrieverAgent(bus, llm)

    # Mock httpx.AsyncClient constructor consistently with happy-path test
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=Exception("Connection refused"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        task = asyncio.create_task(retriever.run())

        request = Message(
            task_id="t2",
            sender="orchestrator",
            recipient="retriever",
            message_type="task",
            payload={"query": "RAG 评估"},
        )

        result = await bus.send_and_wait("retriever", request, timeout=1.0)
        assert "documents" in result.payload
        assert len(result.payload["documents"]) == 1
        assert "检索失败" in result.payload["documents"][0]["content"]
        assert result.payload["documents"][0]["source"] == "rag_app"
        assert result.payload["documents"][0]["score"] == 0.0

        retriever.stop()
        await asyncio.wait_for(task, timeout=1.0)


@pytest.mark.asyncio
async def test_retriever_handles_non_2xx_status():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    retriever = RetrieverAgent(bus, llm)

    # Mock httpx.AsyncClient returning a 500 response that raises on raise_for_status()
    mock_response = MagicMock()
    mock_response.raise_for_status = MagicMock(side_effect=Exception("500 Internal Server Error"))

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("httpx.AsyncClient", return_value=mock_client):
        task = asyncio.create_task(retriever.run())

        request = Message(
            task_id="t3",
            sender="orchestrator",
            recipient="retriever",
            message_type="task",
            payload={"query": "HTTP 500 test"},
        )

        result = await bus.send_and_wait("retriever", request, timeout=1.0)
        assert "documents" in result.payload
        assert len(result.payload["documents"]) == 1
        assert "检索失败" in result.payload["documents"][0]["content"]
        assert result.payload["documents"][0]["source"] == "rag_app"
        assert result.payload["documents"][0]["score"] == 0.0

        retriever.stop()
        await asyncio.wait_for(task, timeout=1.0)
