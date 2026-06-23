"""Tests for Nexus FastAPI SSE backend."""

import json
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from backends.nexus_app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Nexus" in response.text


def test_chat_sse():
    async def mock_stream(*args, **kwargs):
        yield {"type": "agent_thought", "data": {"agent": "orchestrator", "content": "Starting planning phase"}}
        yield {"type": "planner_thought", "data": {"content": "Plan generated"}}
        yield {"type": "tool_call", "data": {"agent": "executor", "tool": "calculate", "args": {"expression": "2+2"}}}
        yield {"type": "tool_result", "data": {"agent": "executor", "result": "4"}}
        yield {"type": "final_answer", "data": {"content": "4", "sources": [], "critique": {}, "session_id": "test-session-123"}}

    mock_orchestrator = AsyncMock()
    mock_orchestrator.process_stream = mock_stream

    with patch("backends.nexus_app.main.agents", {"orchestrator": mock_orchestrator}):
        response = client.post("/chat", data={"query": "What is 2+2?"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    body = response.text
    assert "event:" in body
    # Parse at least one event line and verify final_answer is present
    assert "event: final_answer" in body
    events = []
    for line in body.strip().split("\n\n"):
        event_type = None
        event_data = None
        for subline in line.split("\n"):
            if subline.startswith("event: "):
                event_type = subline[len("event: "):]
            elif subline.startswith("data: "):
                event_data = json.loads(subline[len("data: "):])
        if event_type:
            events.append((event_type, event_data))
    event_types = [et for et, _ in events]
    assert "final_answer" in event_types
    # Verify session_id is included in final_answer
    final_answer_data = events[event_types.index("final_answer")][1]
    assert "session_id" in final_answer_data


def test_chat_sse_missing_api_key():
    with patch("backends.nexus_app.main.Config.DASHSCOPE_API_KEY", None):
        response = client.post("/chat", data={"query": "hello"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    body = response.text
    assert "event: error" in body
    # Parse error event
    for line in body.strip().split("\n\n"):
        event_type = None
        event_data = None
        for subline in line.split("\n"):
            if subline.startswith("event: "):
                event_type = subline[len("event: "):]
            elif subline.startswith("data: "):
                event_data = json.loads(subline[len("data: "):])
        if event_type == "error":
            assert "DASHSCOPE_API_KEY" in event_data.get("message", "")
            break
    else:
        raise AssertionError("Expected error event not found")
