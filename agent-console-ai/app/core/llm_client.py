import time
import requests
from typing import Dict, Any, List
from app.config import settings

class AiDemosClient:
    """调用 ai-demos 的 /fc/chat 接口，无需本地 LLM API Key。"""

    def __init__(self):
        self.base_url = settings.ai_demos_base_url.rstrip("/")
        self.timeout = settings.max_timeout

    def chat(self, query: str) -> Dict[str, Any]:
        url = f"{self.base_url}/chat"
        start = time.time()
        try:
            response = requests.post(
                url,
                data={"query": query},
                timeout=self.timeout,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            duration_ms = int((time.time() - start) * 1000)
            response.raise_for_status()
            result = response.json()
            result["duration_ms"] = duration_ms
            return result
        except requests.exceptions.RequestException as e:
            return {
                "answer": f"",
                "tool_calls": [],
                "error": str(e),
                "duration_ms": int((time.time() - start) * 1000),
            }

    def clear_history(self) -> None:
        """清空 ai-demos 全局会话历史，避免多次调用互相干扰。"""
        try:
            requests.post(
                f"{self.base_url}/clear",
                timeout=5,
            )
        except Exception:
            pass

llm_client = AiDemosClient()
