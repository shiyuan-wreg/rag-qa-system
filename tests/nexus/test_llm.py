import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/backends/nexus_app")

from core.llm import LLMClient


def test_extract_content_from_qwen_response():
    client = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    mock = {"output": {"choices": [{"message": {"content": "hello", "tool_calls": None}}]}}
    result = client._extract_content(mock)
    assert result["content"] == "hello"
    assert result["tool_calls"] is None


def test_extract_tool_calls():
    client = LLMClient(provider="qwen", model="qwen-turbo", api_key="fake")
    mock = {"output": {"choices": [{"message": {"content": "", "tool_calls": [{"id": "1", "function": {"name": "search", "arguments": "{}"}}]}}]}}
    result = client._extract_content(mock)
    assert len(result["tool_calls"]) == 1
