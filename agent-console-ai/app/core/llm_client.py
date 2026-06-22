import json
import time
from typing import List, Dict, Any, Optional
from zhipuai import ZhipuAI
from app.config import settings

class ZhipuClient:
    def __init__(self):
        self.client = ZhipuAI(api_key=settings.zhipu_api_key)
        self.default_model = settings.default_model

    def chat(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        model = model or self.default_model
        start = time.time()
        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
            }
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"

            response = self.client.chat.completions.create(**kwargs)
            duration_ms = int((time.time() - start) * 1000)

            choice = response.choices[0]
            message = choice.message

            result = {
                "content": message.content or "",
                "tool_calls": [],
                "usage": response.usage.model_dump() if response.usage else {},
                "duration_ms": duration_ms,
            }

            if hasattr(message, "tool_calls") and message.tool_calls:
                for tc in message.tool_calls:
                    result["tool_calls"].append({
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments),
                    })
            return result
        except Exception as e:
            return {
                "content": f"",
                "tool_calls": [],
                "error": str(e),
                "duration_ms": int((time.time() - start) * 1000),
            }

llm_client = ZhipuClient()
