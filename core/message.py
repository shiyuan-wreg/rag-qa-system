"""Message definitions for inter-agent communication."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from uuid import uuid4


@dataclass
class Message:
    task_id: str
    sender: str
    recipient: str
    message_type: str  # task, result, plan, thought, critique, error
    payload: Dict[str, Any]
    message_id: str = field(default_factory=lambda: str(uuid4()))
    in_reply_to: Optional[str] = None
