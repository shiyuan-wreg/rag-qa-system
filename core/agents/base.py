"""Base agent class."""

import asyncio
from abc import abstractmethod
from typing import Any, Dict, Optional

from core.llm import LLMClient
from core.message import Message
from core.message_bus import MessageBus


class BaseAgent:
    def __init__(self, agent_id: str, bus: MessageBus, llm: LLMClient):
        self.agent_id = agent_id
        self.bus = bus
        self.llm = llm
        self._running = False

    async def run(self) -> None:
        """Main message processing loop."""
        self._running = True
        queue = self.bus.subscribe(self.agent_id)

        while self._running:
            try:
                message = await asyncio.wait_for(queue.get(), timeout=0.5)
                await self.handle_message(message)
            except asyncio.TimeoutError:
                continue

    def stop(self) -> None:
        self._running = False

    @abstractmethod
    async def handle_message(self, message: Message) -> None:
        """Process incoming message. Must be implemented by subclasses."""
        pass

    async def send_message(
        self,
        recipient: str,
        message_type: str,
        payload: Dict[str, Any],
        task_id: str,
        in_reply_to: Optional[str] = None,
    ) -> None:
        msg = Message(
            task_id=task_id,
            sender=self.agent_id,
            recipient=recipient,
            message_type=message_type,
            payload=payload,
            in_reply_to=in_reply_to,
        )
        await self.bus.publish(msg)

    async def think(self, system_prompt: str, user_prompt: str, tools: Optional[list] = None) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return self.llm.chat(messages, tools=tools)
