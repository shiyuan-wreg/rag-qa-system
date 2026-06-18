"""Nexus Phase 1 - Command line entry point."""

import asyncio

from core.agents.critic import CriticAgent
from core.agents.executor import ExecutorAgent
from core.agents.orchestrator import OrchestratorAgent
from core.agents.planner import PlannerAgent
from core.agents.retriever import RetrieverAgent
from core.agents.summarizer import SummarizerAgent
from core.config import Config
from core.llm import LLMClient
from core.message_bus import MessageBus


def create_llm_client():
    if Config.LLM_PROVIDER == "qwen":
        return LLMClient(
            provider="qwen",
            model=Config.LLM_MODEL,
            api_key=Config.DASHSCOPE_API_KEY,
        )
    else:
        raise ValueError(f"Unsupported provider: {Config.LLM_PROVIDER}")


async def main():
    print("=" * 60)
    print("Nexus Phase 1 - Multi-Agent Workflow Assistant")
    print("=" * 60)

    if not Config.DASHSCOPE_API_KEY:
        print("\nError: DASHSCOPE_API_KEY not set. Please check your .env file.")
        return

    bus = MessageBus()
    llm = create_llm_client()

    orchestrator = OrchestratorAgent(bus, llm)
    planner = PlannerAgent(bus, llm)
    retriever = RetrieverAgent(bus, llm)
    executor = ExecutorAgent(bus, llm)
    summarizer = SummarizerAgent(bus, llm)
    critic = CriticAgent(bus, llm)

    agents = [orchestrator, planner, retriever, executor, summarizer, critic]
    tasks = [asyncio.create_task(agent.run()) for agent in agents]

    print("\nAgents started. Type your question or '/quit' to exit.\n")

    try:
        while True:
            query = input("You: ").strip()
            if query.lower() in ("/quit", "/exit", "quit", "exit"):
                break
            if not query:
                continue

            print("\nNexus: thinking...\n")
            result = await orchestrator.process(query)

            print(f"Answer: {result['answer']}\n")
            print(f"Plan: {result['plan']}\n")
            print(f"Critique: {result['critique']}\n")
    finally:
        for agent in agents:
            agent.stop()
        await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
