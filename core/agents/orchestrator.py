"""Orchestrator Agent: coordinates all other agents."""

import asyncio
import re
import uuid
from typing import Any, AsyncGenerator, Dict, Tuple

from core.agents.base import BaseAgent
from core.message import Message
from core.session import SessionState


class OrchestratorAgent(BaseAgent):
    def __init__(self, bus, llm):
        super().__init__("orchestrator", bus, llm)
        self._pending_futures: Dict[str, asyncio.Future] = {}

    async def handle_message(self, message: Message) -> None:
        if message.message_type == "result" or message.message_type == "critique":
            future = self._pending_futures.get(message.task_id)
            if future and not future.done():
                future.set_result(message)

    async def process_stream(self, query: str, session_id: str = None) -> AsyncGenerator[Dict[str, Any], None]:
        try:
            task_id = session_id or str(uuid.uuid4())
            session = SessionState(task_id=task_id, query=query)

            # Step 1: Plan
            session.status = "planning"
            yield {"type": "agent_thought", "data": {"agent": "orchestrator", "content": "Starting planning phase"}}
            plan_msg = await self._send_and_wait(
                "planner",
                Message(
                    task_id=task_id,
                    sender="orchestrator",
                    recipient="planner",
                    message_type="task",
                    payload={"query": query},
                ),
                60.0,
            )
            session.plan = plan_msg.payload.get("plan", [])
            yield {"type": "planner_thought", "data": {"content": f"Plan generated: {session.plan}"}}

            # Step 2: Execute plan steps
            session.status = "executing"
            for step in session.plan:
                agent_id = step.get("agent")
                if agent_id == "retriever":
                    yield {"type": "tool_call", "data": {"agent": "retriever", "tool": "search", "args": {"query": step.get("task", query)}}}
                    result = await self._send_and_wait(
                        "retriever",
                        Message(
                            task_id=task_id,
                            sender="orchestrator",
                            recipient="retriever",
                            message_type="task",
                            payload={"query": step.get("task", query)},
                        ),
                        60.0,
                    )
                    docs = result.payload.get("documents", [])
                    session.documents.extend(docs)
                    yield {"type": "tool_result", "data": {"agent": "retriever", "result": docs}}

                elif agent_id == "executor":
                    tool, args = self._resolve_executor_call(step, query)
                    yield {"type": "tool_call", "data": {"agent": "executor", "tool": tool, "args": args}}
                    result = await self._send_and_wait(
                        "executor",
                        Message(
                            task_id=task_id,
                            sender="orchestrator",
                            recipient="executor",
                            message_type="task",
                            payload={"tool": tool, "args": args},
                        ),
                        60.0,
                    )
                    session.tool_results.append(result.payload)
                    yield {"type": "tool_result", "data": {"agent": "executor", "result": result.payload}}

            # Step 3: Summarize
            session.status = "summarizing"
            yield {"type": "agent_thought", "data": {"agent": "orchestrator", "content": "Starting summarization phase"}}
            summary_msg = await self._send_and_wait(
                "summarizer",
                Message(
                    task_id=task_id,
                    sender="orchestrator",
                    recipient="summarizer",
                    message_type="task",
                    payload={
                        "query": query,
                        "documents": session.documents,
                        "tool_results": session.tool_results,
                    },
                ),
                60.0,
            )
            session.answer = summary_msg.payload.get("answer", "")

            # Step 4: Critique
            session.status = "critiquing"
            yield {"type": "agent_thought", "data": {"agent": "orchestrator", "content": "Starting critique phase"}}
            critique_msg = await self._send_and_wait(
                "critic",
                Message(
                    task_id=task_id,
                    sender="orchestrator",
                    recipient="critic",
                    message_type="task",
                    payload={"query": query, "answer": session.answer},
                ),
                60.0,
            )
            session.critique = critique_msg.payload
            session.status = "done"

            yield {
                "type": "final_answer",
                "data": {
                    "content": session.answer,
                    "sources": [doc.get("source") for doc in session.documents if doc.get("source")],
                    "critique": session.critique,
                    "session_id": task_id,
                },
            }
        except Exception as e:
            yield {"type": "error", "data": {"message": str(e)}}

    async def process(self, query: str, timeout: float = 60.0) -> Dict[str, Any]:
        task_id = str(uuid.uuid4())
        session = SessionState(task_id=task_id, query=query)

        # Step 1: Plan
        session.status = "planning"
        plan_msg = await self._send_and_wait(
            "planner",
            Message(
                task_id=task_id,
                sender="orchestrator",
                recipient="planner",
                message_type="task",
                payload={"query": query},
            ),
            timeout,
        )
        session.plan = plan_msg.payload.get("plan", [])

        # Step 2: Execute plan steps
        session.status = "executing"
        for step in session.plan:
            agent_id = step.get("agent")
            if agent_id == "retriever":
                result = await self._send_and_wait(
                    "retriever",
                    Message(
                        task_id=task_id,
                        sender="orchestrator",
                        recipient="retriever",
                        message_type="task",
                        payload={"query": step.get("task", query)},
                    ),
                    timeout,
                )
                session.documents.extend(result.payload.get("documents", []))

            elif agent_id == "executor":
                tool, args = self._resolve_executor_call(step, query)
                result = await self._send_and_wait(
                    "executor",
                    Message(
                        task_id=task_id,
                        sender="orchestrator",
                        recipient="executor",
                        message_type="task",
                        payload={"tool": tool, "args": args},
                    ),
                    timeout,
                )
                session.tool_results.append(result.payload)

        # Step 3: Summarize
        session.status = "summarizing"
        summary_msg = await self._send_and_wait(
            "summarizer",
            Message(
                task_id=task_id,
                sender="orchestrator",
                recipient="summarizer",
                message_type="task",
                payload={
                    "query": query,
                    "documents": session.documents,
                    "tool_results": session.tool_results,
                },
            ),
            timeout,
        )
        session.answer = summary_msg.payload.get("answer", "")

        # Step 4: Critique
        session.status = "critiquing"
        critique_msg = await self._send_and_wait(
            "critic",
            Message(
                task_id=task_id,
                sender="orchestrator",
                recipient="critic",
                message_type="task",
                payload={"query": query, "answer": session.answer},
            ),
            timeout,
        )
        session.critique = critique_msg.payload
        session.status = "done"

        return {
            "task_id": task_id,
            "query": query,
            "answer": session.answer,
            "plan": session.plan,
            "documents": session.documents,
            "tool_results": session.tool_results,
            "critique": session.critique,
        }

    async def _send_and_wait(self, recipient: str, message: Message, timeout: float) -> Message:
        future = asyncio.get_running_loop().create_future()
        self._pending_futures[message.task_id] = future
        await self.bus.publish(message)

        try:
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        finally:
            self._pending_futures.pop(message.task_id, None)

    def _resolve_executor_call(self, step: Dict[str, Any], query: str) -> Tuple[str, Dict[str, Any]]:
        """Determine which tool to call and with what args.

        Uses explicit tool/args from planner if present; otherwise falls back to
        inferring from task/query text for legacy/Phase 2 plans.
        """
        tool = step.get("tool")
        args = step.get("args")
        if tool and isinstance(args, dict):
            return tool, args

        task = step.get("task", "")
        combined = f"{query} {task}".lower()

        # Weather query
        if any(k in combined for k in ("天气", "weather", "温度", "气温")):
            return "get_weather", {"city": self._extract_city(query, task)}

        # Math calculation
        return "calculate", {"expression": self._extract_expression(query, task)}

    def _extract_city(self, query: str, task: str) -> str:
        known_cities = ["北京", "上海", "广州", "深圳", "杭州"]
        for text in (query, task):
            if not text:
                continue
            for city in known_cities:
                if city in text:
                    return city
        return "北京"

    def _extract_expression(self, query: str, task: str) -> str:
        for text in (task, query):
            if not text:
                continue
            # Keep digits, decimal points, operators, parens, spaces
            cleaned = re.sub(r"[^\d+\-*/().\s]", "", text)
            cleaned = re.sub(r"\s+", " ", cleaned).strip()
            if cleaned and any(op in cleaned for op in "+-*/"):
                return cleaned
        return "0"
