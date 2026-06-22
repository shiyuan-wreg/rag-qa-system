from typing import Callable, Dict, Any
from app.schemas import ToolInfo

ToolFunction = Callable[..., str]

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolFunction] = {}

    def register(self, name: str, func: ToolFunction):
        self._tools[name] = func

    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        if tool_name not in self._tools:
            return f"错误：工具 '{tool_name}' 未注册"
        try:
            return self._tools[tool_name](**arguments)
        except Exception as e:
            return f"工具执行失败：{str(e)}"

    def get_available_tools(self) -> Dict[str, ToolFunction]:
        return self._tools.copy()

registry = ToolRegistry()
