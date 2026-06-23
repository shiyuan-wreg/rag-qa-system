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


@pytest.mark.asyncio
async def test_critic_llm_critique_parsed():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    critic = CriticAgent(bus, llm)

    # Monkeypatch think to return valid LLM JSON
    async def fake_think(system, user):
        return '{"correctness": 0.9, "relevance": 0.85, "completeness": 0.8, "safety": 1.0, "overall": 0.88, "feedback": "Good answer"}'

    critic.think = fake_think

    scores, feedback = await critic._llm_critique("query", "answer")
    assert scores["correctness"] == 0.9
    assert scores["overall"] == 0.88
    assert feedback == "Good answer"


@pytest.mark.asyncio
async def test_critic_fallback_on_llm_failure():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    critic = CriticAgent(bus, llm)

    # Monkeypatch think to raise exception
    async def fake_think(system, user):
        raise RuntimeError("LLM failed")

    critic.think = fake_think

    task = asyncio.create_task(critic.run())

    request = Message(
        task_id="t2",
        sender="orchestrator",
        recipient="critic",
        message_type="task",
        payload={
            "query": "test",
            "answer": "test answer",
        },
    )

    result = await bus.send_and_wait("critic", request, timeout=1.0)
    assert "scores" in result.payload
    assert "passed" in result.payload
    assert 0.0 <= result.payload["scores"]["overall"] <= 1.0
    # Should be fallback rule-based scores
    assert result.payload["feedback"] == "回答通过评估" or result.payload["feedback"] == "回答质量不足，建议补充信息"

    critic.stop()
    await asyncio.wait_for(task, timeout=1.0)
