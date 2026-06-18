"""Critic Agent: evaluates answer quality."""

import re

from core.agents.base import BaseAgent
from core.message import Message


class CriticAgent(BaseAgent):
    def __init__(self, bus, llm):
        super().__init__("critic", bus, llm)

    async def handle_message(self, message: Message) -> None:
        query = message.payload.get("query", "")
        answer = message.payload.get("answer", "")

        scores = self._rule_based_scores(query, answer)
        passed = scores["overall"] >= 0.6

        await self.send_message(
            recipient=message.sender,
            message_type="critique",
            payload={
                "scores": scores,
                "passed": passed,
                "feedback": "回答通过评估" if passed else "回答质量不足，建议补充信息",
            },
            task_id=message.task_id,
        )

    def _rule_based_scores(self, query: str, answer: str) -> dict:
        query_keywords = set(re.findall(r"\b\w{2,}\b", query.lower()))
        if query_keywords:
            matched = sum(1 for kw in query_keywords if kw in answer.lower())
            relevance = round(min(matched / len(query_keywords) * 1.5, 1.0), 2)
        else:
            relevance = 0.5

        if len(answer) < 10:
            completeness = 0.0
        elif len(answer) > 100:
            completeness = 0.8
        else:
            completeness = 0.5

        harmful = ["炸弹", "毒品", "杀人"]
        safety = 0.0 if any(kw in answer for kw in harmful) else 1.0

        correctness = 0.7 if "错误" not in answer and "不知道" not in answer else 0.3

        overall = round((correctness + relevance + completeness + safety) / 4, 2)
        return {
            "correctness": correctness,
            "relevance": relevance,
            "completeness": completeness,
            "safety": safety,
            "overall": overall,
        }
