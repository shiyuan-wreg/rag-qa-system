"""Executor Agent: executes tools via HTTP call to fc_app."""

import httpx

from core.agents.base import BaseAgent
from core.config import Config
from core.message import Message


class ExecutorAgent(BaseAgent):
    """
    Phase 2 executor.
    Calls fc_app /execute endpoint over HTTP.
    """

    def __init__(self, bus, llm):
        super().__init__("executor", bus, llm)

    async def handle_message(self, message: Message) -> None:
        tool_name = message.payload.get("tool", "")
        args = message.payload.get("args", {})

        result = await self._execute(tool_name, args)

        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"result": result, "tool": tool_name, "args": args},
            task_id=message.task_id,
        )

    async def _execute(self, tool: str, args: dict) -> str:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{Config.FC_URL}/execute",
                    json={"tool": tool, "args": args},
                )
                response.raise_for_status()
                data = response.json()
                return data.get("result", "")
        except Exception as e:
            return f"工具执行失败：{e}"
