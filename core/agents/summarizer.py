"""Summarizer Agent: synthesizes final answers from intermediate results."""

from core.agents.base import BaseAgent
from core.message import Message


class SummarizerAgent(BaseAgent):
    def __init__(self, bus, llm):
        super().__init__("summarizer", bus, llm)

    async def handle_message(self, message: Message) -> None:
        query = message.payload.get("query", "")
        documents = message.payload.get("documents", [])
        tool_results = message.payload.get("tool_results", [])

        system_prompt = """你是一个总结专家。请根据检索到的文档和工具执行结果，生成准确、简洁的中文回答。
如果文档中没有相关内容，请明确说明。不要编造信息。"""

        context = self._build_context(documents, tool_results)
        user_prompt = f"用户问题：{query}\n\n参考资料：\n{context}\n\n请生成最终回答："

        response = await self.think(system_prompt, user_prompt)
        answer = response.get("content", "抱歉，无法生成回答。")

        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"answer": answer},
            task_id=message.task_id,
        )

    def _build_context(self, documents: list, tool_results: list) -> str:
        parts = []
        for i, doc in enumerate(documents, 1):
            parts.append(f"[文档 {i}] {doc.get('content', '')}")
        for i, result in enumerate(tool_results, 1):
            parts.append(f"[工具结果 {i}] {result.get('result', '')}")
        return "\n\n".join(parts) if parts else "无参考资料"
