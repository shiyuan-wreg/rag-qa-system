"""Planner Agent: decomposes user requests into executable steps."""

import json
from typing import Any, Dict

from core.agents.base import BaseAgent
from core.message import Message


class PlannerAgent(BaseAgent):
    def __init__(self, bus, llm):
        super().__init__("planner", bus, llm)

    async def handle_message(self, message: Message) -> None:
        query = message.payload.get("query", "")

        system_prompt = """你是一个任务规划专家。请将用户的需求拆解为可执行的步骤。
每个步骤必须包含：step_id（整数）、agent（执行该步骤的 Agent 名称）、task（具体任务描述）。
可用 Agent：retriever（检索知识库）、executor（执行工具）、summarizer（总结生成）。
请只输出 JSON 格式，不要输出其他解释。

输出格式示例：
{
  "steps": [
    {"step_id": 1, "agent": "retriever", "task": "检索知识库中关于 xxx 的内容"},
    {"step_id": 2, "agent": "executor", "task": "调用工具执行 xxx"},
    {"step_id": 3, "agent": "summarizer", "task": "总结结果并生成回答"}
  ]
}"""

        response = await self.think(system_prompt, f"用户需求：{query}")
        plan = self._parse_plan(response.get("content", "{}"))

        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"plan": plan},
            task_id=message.task_id,
        )

    def _parse_plan(self, content: str) -> list:
        try:
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            data = json.loads(content.strip())
            return data.get("steps", [])
        except json.JSONDecodeError:
            return [
                {"step_id": 1, "agent": "retriever", "task": "检索相关知识"},
                {"step_id": 2, "agent": "summarizer", "task": "总结生成回答"},
            ]
