"""Nexus FastAPI SSE backend."""

import asyncio
import json
import uuid
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, StreamingResponse

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

# Global state
bus = MessageBus()
llm: LLMClient | None = None
agents: Dict[str, Any] = {}
agent_tasks: list = []
sessions: Dict[str, list] = {}


@app.on_event("startup")
async def startup():
    global agents, agent_tasks, llm
    llm = LLMClient(provider=Config.LLM_PROVIDER, model=Config.LLM_MODEL, api_key=Config.DASHSCOPE_API_KEY or "")
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


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Nexus Chat</title></head>
    <body>
        <h1>Nexus Multi-Agent Chat</h1>
        <div id="chat"></div>
        <form id="form">
            <input type="text" id="query" name="query" placeholder="Ask something...">
            <button type="submit">Send</button>
        </form>
        <script>
            const form = document.getElementById('form');
            const chat = document.getElementById('chat');
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const query = document.getElementById('query').value;
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: 'query=' + encodeURIComponent(query)
                });
                const reader = response.body.getReader();
                const decoder = new TextDecoder();
                while (true) {
                    const {done, value} = await reader.read();
                    if (done) break;
                    const chunk = decoder.decode(value);
                    chat.innerHTML += '<pre>' + chunk + '</pre>';
                }
            });
        </script>
    </body>
    </html>
    """


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat")
async def chat(query: str = Form(...), session_id: str = Form("")):
    if not Config.DASHSCOPE_API_KEY:
        async def error_stream():
            yield f"event: error\ndata: {json.dumps({'message': 'DASHSCOPE_API_KEY not set'})}\n\n"
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
