from app.core.agent_engine import AgentEngine
from app.schemas import ChatRequest, ToolInfo

engine = AgentEngine()

def test_chat_without_tools():
    req = ChatRequest(
        agent_code="test",
        system_prompt="你是一个 helpful assistant",
        model_name="glm-4-flash",
        user_query="你好",
        tools=[],
    )
    resp = engine.chat(req)
    assert resp.success
    assert resp.data.final_response
    assert len(resp.data.steps) >= 3
