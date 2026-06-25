"""Nexus FastAPI SSE backend."""

import asyncio
import json
import uuid
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI, Form, Request
from fastapi.responses import StreamingResponse
from fastapi.templating import Jinja2Templates

from core.agents.orchestrator import OrchestratorAgent
from core.agents.planner import PlannerAgent
from core.agents.retriever import RetrieverAgent
from core.agents.executor import ExecutorAgent
from core.agents.summarizer import SummarizerAgent
from core.agents.critic import CriticAgent
from core.llm import LLMClient
from core.message_bus import MessageBus
from core.config import Config

app = FastAPI(title="Nexus Multi-Agent API")

# Templates
templates = Jinja2Templates(directory="backends/nexus_app/templates")

# Global state
bus = MessageBus()
llm: LLMClient | None = None
agents: Dict[str, Any] = {}
agent_tasks: list = []
sessions: Dict[str, list] = {}


@app.on_event("startup")
async def startup():
    global agents, agent_tasks, llm
    llm = LLMClient.from_config()
    agents = {
        "planner": PlannerAgent(bus, llm),
        "retriever": RetrieverAgent(bus, llm),
        "executor": ExecutorAgent(bus, llm),
        "summarizer": SummarizerAgent(bus, llm),
        "critic": CriticAgent(bus, llm),
        "orchestrator": OrchestratorAgent(bus, llm),
    }
    for agent in agents.values():
        task = asyncio.create_task(agent.run())
        agent_tasks.append(task)


@app.on_event("shutdown")
async def shutdown():
    for agent in agents.values():
        agent.stop()
    for task in agent_tasks:
        task.cancel()
    await asyncio.gather(*agent_tasks, return_exceptions=True)


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(query: str = Form(...), session_id: str = Form("")):
    if not Config.LLM_API_KEY:
        async def error_stream():
            yield f"event: error\ndata: {json.dumps({'message': 'LLM_API_KEY not set'})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    orchestrator = agents.get("orchestrator")
    if orchestrator is None:
        async def error_stream():
            yield f"event: error\ndata: {json.dumps({'message': 'Agents not initialized'})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    if not session_id:
        session_id = str(uuid.uuid4())

    async def event_stream() -> AsyncGenerator[str, None]:
        try:
            async for event in orchestrator.process_stream(query, session_id=session_id):
                yield f"event: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
            # Include session_id in final_answer data by patching it in sessions
            sessions.setdefault(session_id, []).append({"query": query, "final_answer": True})
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
