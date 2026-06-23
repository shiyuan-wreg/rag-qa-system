"""Session state tracking."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class SessionState:
    task_id: str
    query: str
    plan: List[Dict] = field(default_factory=list)
    documents: List[Dict] = field(default_factory=list)
    tool_results: List[Dict] = field(default_factory=list)
    answer: str = ""
    critique: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
