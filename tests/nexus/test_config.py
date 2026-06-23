import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/backends/nexus_app")

from config import Config
from core.session import SessionState


def test_config_has_required_fields():
    assert hasattr(Config, "LLM_PROVIDER")
    assert hasattr(Config, "LLM_MODEL")
    assert hasattr(Config, "DASHSCOPE_API_KEY")
    assert hasattr(Config, "RAG_URL")
    assert hasattr(Config, "FC_URL")


def test_session_state_defaults():
    s = SessionState(task_id="t1", query="hello")
    assert s.status == "pending"
    assert s.plan == []
