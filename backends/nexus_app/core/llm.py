"""Unified LLM client."""

from typing import Any, Dict, List, Optional


class LLMClient:
    def __init__(self, provider: str, model: str, api_key: str, base_url: Optional[str] = None):
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self._raw_client = self._create_client()

    def _create_client(self):
        if self.provider == "qwen":
            import dashscope
            dashscope.api_key = self.api_key
            return dashscope.Generation
        else:
            from openai import OpenAI
            return OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(self, messages: List[Dict], tools: Optional[List[Dict]] = None, stream: bool = False) -> Dict[str, Any]:
        if self.provider == "qwen":
            response = self._raw_client.call(
                model=self.model,
                messages=messages,
                tools=tools,
                result_format="message",
            )
        else:
            response = self._raw_client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                stream=stream,
            )
        return self._extract_content(response)

    def _extract_content(self, response: Any) -> Dict[str, Any]:
        if self.provider == "qwen":
            if isinstance(response, dict):
                message = response["output"]["choices"][0]["message"]
            else:
                message = response.output.choices[0].message
            return {
                "content": message.get("content", ""),
                "tool_calls": message.get("tool_calls"),
            }
        else:
            message = response.choices[0].message
            tool_calls = []
            if message.tool_calls:
                for tc in message.tool_calls:
                    tool_calls.append({
                        "id": tc.id,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    })
            return {
                "content": message.content or "",
                "tool_calls": tool_calls or None,
            }
