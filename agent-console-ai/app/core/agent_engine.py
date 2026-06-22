import json
import time
from typing import List, Dict, Any
from app.core.llm_client import llm_client
from app.core.tool_executor import tools_to_schema, execute_tool_call
from app.schemas import ChatRequest, ChatResponse, ChatData, Step, StepOutput, ChatMessage

class AgentEngine:
    def chat(self, request: ChatRequest) -> ChatResponse:
        start = time.time()
        steps = []

        messages = self._build_messages(request)
        tools_schema = tools_to_schema(request.tools)

        # Step 1: 初始 LLM 调用，判断是否需要工具
        response = llm_client.chat(
            messages=messages,
            tools=tools_schema if tools_schema else None,
            model=request.model_name,
            temperature=request.temperature,
        )
        steps.append(Step(
            step_type="llm",
            step_order=1,
            input={"messages": messages, "tools": tools_schema},
            output=StepOutput(tool_calls=response.get("tool_calls")),
            duration_ms=response.get("duration_ms", 0),
        ))

        if response.get("error"):
            return self._error_response(response["error"])

        # Step 2: 执行工具调用
        tool_results = []
        if response.get("tool_calls"):
            for tc in response["tool_calls"]:
                result = execute_tool_call(tc)
                tool_results.append({"tool_call": tc, "result": result})
                steps.append(Step(
                    step_type="tool",
                    step_order=len(steps) + 1,
                    input=tc,
                    output=StepOutput(result=result),
                    duration_ms=0,
                ))
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.get("id"),
                    "content": result,
                })

        # Step 3: 生成初稿
        draft_messages = messages.copy()
        if response.get("tool_calls"):
            # 如果已经调用工具，需要把 assistant 的 tool_calls 消息也加入
            draft_messages.append({
                "role": "assistant",
                "content": response.get("content", ""),
                "tool_calls": [
                    {
                        "id": tc.get("id"),
                        "type": "function",
                        "function": {
                            "name": tc.get("name"),
                            "arguments": json.dumps(tc.get("arguments", {})),
                        },
                    }
                    for tc in response.get("tool_calls", [])
                ],
            })

        draft_response = llm_client.chat(
            messages=draft_messages,
            model=request.model_name,
            temperature=request.temperature,
        )
        draft = draft_response.get("content", "")
        steps.append(Step(
            step_type="draft",
            step_order=len(steps) + 1,
            input={"messages": draft_messages},
            output=StepOutput(content=draft),
            duration_ms=draft_response.get("duration_ms", 0),
        ))

        # Step 4: Reflection
        reflect_prompt = self._build_reflection_prompt(
            request.user_query, draft, tool_results
        )
        reflect_response = llm_client.chat(
            messages=reflect_prompt,
            model=request.model_name,
            temperature=0.3,
        )
        reflection_text = reflect_response.get("content", "")
        reflection = self._parse_reflection(reflection_text)
        steps.append(Step(
            step_type="reflect",
            step_order=len(steps) + 1,
            input={"draft": draft},
            output=StepOutput(
                content=reflection_text,
                has_issue=reflection.get("has_issue"),
                issues=reflection.get("issues"),
                suggestions=reflection.get("suggestions"),
            ),
            duration_ms=reflect_response.get("duration_ms", 0),
        ))

        # Step 5: Revise
        revise_prompt = self._build_revise_prompt(draft, reflection_text)
        revise_response = llm_client.chat(
            messages=revise_prompt,
            model=request.model_name,
            temperature=request.temperature,
        )
        final = revise_response.get("content", draft)
        steps.append(Step(
            step_type="revise",
            step_order=len(steps) + 1,
            input={"draft": draft, "reflection": reflection_text},
            output=StepOutput(content=final),
            duration_ms=revise_response.get("duration_ms", 0),
        ))

        total_duration = int((time.time() - start) * 1000)
        return ChatResponse(
            success=True,
            data=ChatData(
                final_response=final,
                total_tokens=0,
                duration_ms=total_duration,
                steps=steps,
            ),
        )

    def _build_messages(self, request: ChatRequest) -> List[Dict[str, str]]:
        messages = [{"role": "system", "content": request.system_prompt}]
        for h in request.history:
            messages.append({"role": h.role, "content": h.content})
        messages.append({"role": "user", "content": request.user_query})
        return messages

    def _build_reflection_prompt(self, user_query: str, draft: str, tool_results: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        tool_text = "\n".join([f"工具 {r['tool_call']['name']} 返回：{r['result']}" for r in tool_results]) or "无工具调用"
        content = f"""你是一位严格的回答质量检查员。请检查下面的初稿回答，指出是否存在以下问题：

1. 事实性错误（与工具返回结果矛盾）
2. 遗漏了用户问题中的某个要求
3. 逻辑不自洽
4. 回答过于冗长或过于简短
5. 表达不清晰

用户问题：{user_query}
工具返回：{tool_text}
初稿回答：{draft}

请以 JSON 格式输出：
{{
  "has_issue": true/false,
  "issues": ["问题1", "问题2"],
  "suggestions": ["建议1", "建议2"]
}}"""
        return [{"role": "user", "content": content}]

    def _parse_reflection(self, text: str) -> Dict[str, Any]:
        try:
            # 简单提取 JSON 块
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                return json.loads(text[start:end+1])
        except Exception:
            pass
        return {"has_issue": False, "issues": [], "suggestions": []}

    def _build_revise_prompt(self, draft: str, reflection: str) -> List[Dict[str, str]]:
        content = f"""请根据以下反思意见，修正初稿回答并生成最终回答。

要求：
- 只输出最终回答，不要解释修改过程
- 确保回答准确、完整、简洁
- 如果反思认为没有 issue，可直接使用初稿

初稿：{draft}
反思意见：{reflection}

最终回答："""
        return [{"role": "user", "content": content}]

    def _error_response(self, error: str) -> ChatResponse:
        return ChatResponse(success=False, error=error)

agent_engine = AgentEngine()
