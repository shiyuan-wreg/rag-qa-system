"""In-memory async message bus for agent communication."""

import asyncio
from typing import Dict

from core.message import Message


class MessageBus:
    """
    In-memory message bus using asyncio.Queue.
    Each subscriber gets its own queue identified by agent_id.
    """

    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}

    def subscribe(self, agent_id: str) -> asyncio.Queue:
        if agent_id not in self._queues:
            self._queues[agent_id] = asyncio.Queue()
        return self._queues[agent_id]

    async def publish(self, message: Message) -> None:
        if message.recipient == "broadcast":
            for queue in self._queues.values():
                await queue.put(message)
        else:
            queue = self._queues.get(message.recipient)
            if queue is None:
                queue = self.subscribe(message.recipient)
            await queue.put(message)

    async def send_and_wait(
        self,
        recipient: str,
        message: Message,
        timeout: float = 30.0,
    ) -> Message:
        await self.publish(message)
        return await self.wait_for_result(message.task_id, recipient, timeout)

    async def wait_for_result(
        self,
        task_id: str,
        sender: str,
        timeout: float = 30.0,
    ) -> Message:
        queue = self.subscribe("orchestrator")
        deadline = asyncio.get_event_loop().time() + timeout

        while True:
            remaining = deadline - asyncio.get_event_loop().time()
            if remaining <= 0:
                raise asyncio.TimeoutError()

            try:
                msg = await asyncio.wait_for(queue.get(), timeout=remaining)
            except asyncio.TimeoutError:
                raise

            if msg.sender == sender and msg.task_id == task_id:
                return msg
            else:
                await queue.put(msg)
