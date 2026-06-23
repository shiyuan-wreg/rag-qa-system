import os
import sys

# Ensure backends/ is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "backends"))

import pytest
from fastapi.testclient import TestClient

# Patch env before importing main
os.environ.setdefault("DASHSCOPE_API_KEY", "")

from fc_app.main import app

client = TestClient(app)


def test_execute_calculate():
    response = client.post("/execute", json={"tool": "calculate", "args": {"expression": "2+2"}})
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "4"


def test_execute_get_weather():
    response = client.post("/execute", json={"tool": "get_weather", "args": {"city": "北京"}})
    assert response.status_code == 200
    data = response.json()
    assert "晴天" in data["result"]


def test_execute_unknown_tool():
    response = client.post("/execute", json={"tool": "unknown_tool", "args": {}})
    assert response.status_code == 200
    data = response.json()
    assert "未知工具" in data["result"]
