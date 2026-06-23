import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from core.agents.critic import CriticAgent
from core.agents.executor import ExecutorAgent
from core.agents.orchestrator import OrchestratorAgent
from core.agents.planner import PlannerAgent
from core.agents.retriever import RetrieverAgent
from core.agents.summarizer import SummarizerAgent
from core.llm import LLMClient
from core.message_bus import MessageBus


@pytest.mark.asyncio
async def test_orchestrator_process_stream():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")

    orchestrator = OrchestratorAgent(bus, llm)
    planner = PlannerAgent(bus, llm)
    retriever = RetrieverAgent(bus, llm)
    executor = ExecutorAgent(bus, llm)
    summarizer = SummarizerAgent(bus, llm)
    critic = CriticAgent(bus, llm)

    # Mock planner and summarizer to avoid LLM calls
    planner.think = async_mock_planner_think
    summarizer.think = async_mock_summarizer_think

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

    # Assert expected event types
    types = [e["type"] for e in events]
    assert "agent_thought" in types
    assert "planner_thought" in types
    assert "tool_call" in types
    assert "tool_result" in types
    assert "final_answer" in types

    orchestrator.stop()
    planner.stop()
    retriever.stop()
    executor.stop()
    summarizer.stop()
    critic.stop()

    await asyncio.gather(*[asyncio.wait_for(t, timeout=2.0) for t in tasks])


@pytest.mark.asyncio
async def test_orchestrator_simple_workflow():
    bus = MessageBus()
    llm = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")

    orchestrator = OrchestratorAgent(bus, llm)
    planner = PlannerAgent(bus, llm)
    retriever = RetrieverAgent(bus, llm)
    executor = ExecutorAgent(bus, llm)
    summarizer = SummarizerAgent(bus, llm)
    critic = CriticAgent(bus, llm)

    # Mock planner and summarizer to avoid LLM calls
    planner.think = async_mock_planner_think
    summarizer.think = async_mock_summarizer_think

    tasks = [
        asyncio.create_task(orchestrator.run()),
        asyncio.create_task(planner.run()),
        asyncio.create_task(retriever.run()),
        asyncio.create_task(executor.run()),
        asyncio.create_task(summarizer.run()),
        asyncio.create_task(critic.run()),
    ]

    result = await orchestrator.process("Python 列表和元组有什么区别？")

    assert "answer" in result
    assert len(result["answer"]) > 0

    orchestrator.stop()
    planner.stop()
    retriever.stop()
    executor.stop()
    summarizer.stop()
    critic.stop()

    await asyncio.gather(*[asyncio.wait_for(t, timeout=2.0) for t in tasks])


async def async_mock_planner_think(system_prompt: str, user_prompt: str, tools=None):
    return {
        "content": '{"steps": [{"step_id": 1, "agent": "retriever", "task": "检索 Python 列表和元组区别"}, {"step_id": 2, "agent": "summarizer", "task": "总结生成回答"}]}',
        "tool_calls": None,
    }


async def async_mock_summarizer_think(system_prompt: str, user_prompt: str, tools=None):
    return {
        "content": "列表是可变的，元组是不可变的。",
        "tool_calls": None,
    }
