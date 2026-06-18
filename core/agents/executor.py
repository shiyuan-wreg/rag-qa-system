"""Executor Agent: executes tools (mocked in Phase 1)."""

import ast
import operator

from core.agents.base import BaseAgent
from core.message import Message


class ExecutorAgent(BaseAgent):
    """
    Phase 1 mock executor.
    In Phase 2, this will connect to the real Tool Registry.
    """

    def __init__(self, bus, llm):
        super().__init__("executor", bus, llm)
        self._tools = {
            "calculate": self._calculate,
            "read_file": self._read_file,
        }

    async def handle_message(self, message: Message) -> None:
        tool_name = message.payload.get("tool", "")
        args = message.payload.get("args", {})

        handler = self._tools.get(tool_name)
        if handler is None:
            result = f"Error: unknown tool '{tool_name}'"
        else:
            result = handler(**args)

        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"result": result, "tool": tool_name, "args": args},
            task_id=message.task_id,
        )

    def _calculate(self, expression: str) -> str:
        try:
            tree = ast.parse(expression, mode='eval')
            result = self._eval_node(tree.body)
            return str(result)
        except Exception as e:
            return f"Error: {e}"

    def _eval_node(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.BinOp):
            ops = {
                ast.Add: operator.add,
                ast.Sub: operator.sub,
                ast.Mult: operator.mul,
                ast.Div: operator.truediv,
            }
            return ops[type(node.op)](self._eval_node(node.left), self._eval_node(node.right))
        raise ValueError(f"Unsupported node: {type(node).__name__}")

    def _read_file(self, path: str) -> str:
        return f"[Mock] Content of {path}"
