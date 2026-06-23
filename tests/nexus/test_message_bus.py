import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/backends/nexus_app")

import pytest

from core.message import Message
from core.message_bus import MessageBus


@pytest.mark.asyncio
async def test_publish_and_subscribe():
    bus = MessageBus()
    queue = bus.subscribe("retriever")
    msg = Message(task_id="t1", sender="orchestrator", recipient="retriever", message_type="task", payload={"query": "hello"})
    await bus.publish(msg)
    received = await asyncio.wait_for(queue.get(), timeout=1.0)
    assert received.task_id == "t1"


@pytest.mark.asyncio
async def test_send_and_wait():
    bus = MessageBus()
    async def responder():
        queue = bus.subscribe("planner")
        msg = await queue.get()
        await bus.publish(Message(task_id=msg.task_id, sender="planner", recipient="orchestrator", message_type="result", payload={"plan": []}))
    asyncio.create_task(responder())
    request = Message(task_id="t2", sender="orchestrator", recipient="planner", message_type="task", payload={"query": "hi"})
    result = await bus.send_and_wait("planner", request, timeout=1.0)
    assert result.sender == "planner"


@pytest.mark.asyncio
async def test_send_and_wait_timeout():
    bus = MessageBus()
    request = Message(task_id="t3", sender="orchestrator", recipient="retriever", message_type="task", payload={})
    with pytest.raises(asyncio.TimeoutError):
        await bus.send_and_wait("retriever", request, timeout=0.1)
