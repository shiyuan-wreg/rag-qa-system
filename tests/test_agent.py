"""Unit tests for Agent core"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import Agent


def test_agent_basic():
    """Test that Agent can be created with correct structure."""
    agent = Agent()
    assert agent.max_turns == 5
    assert len(agent.messages) == 0
    print("[OK] Agent basic structure passed")


def test_agent_tool_handling():
    """Test tool call history handling logic."""
    agent = Agent()

    # Simulate a tool_calls message from model
    message = {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": "call_1",
                "function": {
                    "name": "execute_python",
                    "arguments": '{"code": "2+2"}'
                }
            }
        ]
    }

    agent._handle_tool_calls(message)

    # Verify history contains assistant tool_calls and tool result
    assert agent.messages[0]["role"] == "assistant"
    assert "tool_calls" in agent.messages[0]
    assert agent.messages[1]["role"] == "tool"
    print("[OK] Agent tool call handling passed")


def test_agent_clear_history():
    agent = Agent()
    agent.messages.append({"role": "user", "content": "hello"})
    agent.clear_history()
    assert len(agent.messages) == 0
    print("[OK] Agent clear history passed")


if __name__ == "__main__":
    test_agent_basic()
    test_agent_tool_handling()
    test_agent_clear_history()
    print("\nAll Agent tests passed!")
