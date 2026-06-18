"""Retriever Agent: retrieves relevant knowledge (mocked in Phase 1)."""

from core.agents.base import BaseAgent
from core.message import Message


class RetrieverAgent(BaseAgent):
    """
    Phase 1 mock retriever.
    In Phase 2, this will connect to Chroma vector store.
    """

    def __init__(self, bus, llm):
        super().__init__("retriever", bus, llm)

    async def handle_message(self, message: Message) -> None:
        query = message.payload.get("query", "")

        # Mock retrieval based on keywords
        documents = self._mock_retrieve(query)

        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"documents": documents, "query": query},
            task_id=message.task_id,
        )

    def _mock_retrieve(self, query: str) -> list:
        query_lower = query.lower()
        if "python" in query_lower and ("list" in query_lower or "列表" in query_lower):
            return [
                {"content": "列表（list）是可变序列，支持增删改。", "source": "mock_notes/python_basics.md", "score": 0.95},
                {"content": "元组（tuple）是不可变序列，通常用于固定数据。", "source": "mock_notes/python_basics.md", "score": 0.93},
            ]
        elif "rag" in query_lower or "评估" in query_lower:
            return [
                {"content": "RAG 评估可以从正确性、相关性、完整性等维度进行。", "source": "mock_notes/rag_eval.md", "score": 0.91},
            ]
        else:
            return [
                {"content": f"关于 '{query}' 的模拟检索结果。", "source": "mock_notes/general.md", "score": 0.80},
            ]
