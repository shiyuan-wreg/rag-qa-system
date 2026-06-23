"""Tests for Nexus FastAPI SSE backend."""

import pytest
from fastapi.testclient import TestClient

from backends.nexus_app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_sse():
    response = client.post("/chat", data={"query": "What is 2+2?"})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    body = response.text
    assert "event:" in body
