import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import Config


def test_config_loads():
    assert hasattr(Config, "LLM_PROVIDER")
    assert hasattr(Config, "LLM_MODEL")
    assert hasattr(Config, "DASHSCOPE_API_KEY")
