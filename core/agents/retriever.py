"""Retriever Agent: retrieves relevant knowledge via HTTP to rag_app."""

import httpx

from core.agents.base import BaseAgent
from core.config import Config
from core.message import Message


class RetrieverAgent(BaseAgent):
    """
    Phase 2 retriever: calls rag_app HTTP endpoint for real retrieval.
    """

    def __init__(self, bus, llm):
        super().__init__("retriever", bus, llm)

    async def handle_message(self, message: Message) -> None:
        query = message.payload.get("query", "")

        documents = await self._retrieve(query)

        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"documents": documents, "query": query},
            task_id=message.task_id,
        )

    async def _retrieve(self, query: str) -> list:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{Config.RAG_URL}/chat",
                    data={"query": query}
                )
                await response.aread()
                await response.raise_for_status()
                result = await response.json()
                answer = result.get("answer", "")
                return [
                    {"content": answer, "source": "rag_app", "score": 0.9}
                ]
        except Exception as e:
            return [
                {"content": f"检索失败：{e}", "source": "rag_app", "score": 0.0}
            ]
