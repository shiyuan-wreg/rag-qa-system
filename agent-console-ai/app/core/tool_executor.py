from typing import Dict, Any, List
from app.schemas import ToolInfo
from app.tools.registry import registry

def tools_to_schema(tools: List[ToolInfo]) -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description,
                "parameters": t.parameters,
            },
        }
        for t in tools
    ]

def execute_tool_call(tool_call: Dict[str, Any]) -> str:
    name = tool_call.get("name")
    arguments = tool_call.get("arguments", {})
    return registry.execute(name, arguments)
