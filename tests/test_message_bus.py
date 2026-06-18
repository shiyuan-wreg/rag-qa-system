import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from core.message import Message
from core.message_bus import MessageBus


@pytest.mark.asyncio
async def test_publish_and_subscribe():
    bus = MessageBus()
    queue = bus.subscribe("retriever")

    msg = Message(
        task_id="t1",
        sender="orchestrator",
        recipient="retriever",
        message_type="task",
        payload={"query": "hello"},
    )

    await bus.publish(msg)
    received = await asyncio.wait_for(queue.get(), timeout=1.0)

    assert received.task_id == "t1"
    assert received.sender == "orchestrator"
    assert received.payload["query"] == "hello"


@pytest.mark.asyncio
async def test_send_and_wait():
    bus = MessageBus()

    async def responder():
        queue = bus.subscribe("retriever")
        msg = await queue.get()
        await bus.publish(Message(
            task_id=msg.task_id,
            sender="retriever",
            recipient="orchestrator",
            message_type="result",
            payload={"result": "found"},
        ))

    asyncio.create_task(responder())

    # Ensure subscriber is registered before sending
    bus.subscribe("retriever")

    request = Message(
        task_id="t2",
        sender="orchestrator",
        recipient="retriever",
        message_type="task",
        payload={"query": "hello"},
    )

    result = await bus.send_and_wait("retriever", request, timeout=1.0)
    assert result.payload["result"] == "found"


@pytest.mark.asyncio
async def test_send_and_wait_timeout():
    bus = MessageBus()

    # Ensure subscriber is registered before sending
    bus.subscribe("retriever")

    request = Message(
        task_id="t3",
        sender="orchestrator",
        recipient="retriever",
        message_type="task",
        payload={},
    )

    with pytest.raises(asyncio.TimeoutError):
        await bus.send_and_wait("retriever", request, timeout=0.1)
