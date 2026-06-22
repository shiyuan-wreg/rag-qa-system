import json
import time
from typing import List, Dict, Any
from app.core.llm_client import llm_client
from app.schemas import ChatRequest, ChatResponse, ChatData, Step, StepOutput

class AgentEngine:
    def chat(self, request: ChatRequest) -> ChatResponse:
        start = time.time()
        steps = []

        # 清空 ai-demos 全局历史，确保每次请求独立
        llm_client.clear_history()

        # Step 1: 生成初稿（把用户问题、系统提示、工具说明一起传给 ai-demos）
        draft_query = self._build_draft_query(request)
        draft_response = llm_client.chat(draft_query)
        draft = draft_response.get("answer", "")
        tool_calls = draft_response.get("tool_calls", [])
        steps.append(Step(
            step_type="draft",
            step_order=1,
            input={"query": draft_query},
            output=StepOutput(content=draft, tool_calls=tool_calls),
            duration_ms=draft_response.get("duration_ms", 0),
        ))

        if draft_response.get("error"):
            return ChatResponse(success=False, error=str(draft_response.get("error")))

        # Step 2: Reflection
        reflect_query = self._build_reflection_query(request.user_query, draft, tool_calls)
        reflect_response = llm_client.chat(reflect_query)
        reflection_text = reflect_response.get("answer", "")
        reflection = self._parse_reflection(reflection_text)
        steps.append(Step(
            step_type="reflect",
            step_order=2,
            input={"draft": draft},
            output=StepOutput(
                content=reflection_text,
                has_issue=reflection.get("has_issue"),
                issues=reflection.get("issues"),
                suggestions=reflection.get("suggestions"),
            ),
            duration_ms=reflect_response.get("duration_ms", 0),
        ))

        # Step 3: Revise
        revise_query = self._build_revise_query(draft, reflection_text)
        revise_response = llm_client.chat(revise_query)
        final = revise_response.get("answer", draft)
        steps.append(Step(
            step_type="revise",
            step_order=3,
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

    def _build_draft_query(self, request: ChatRequest) -> str:
        tool_desc = ""
        if request.tools:
            tool_desc = "可用工具：\n" + "\n".join([
                f"- {t.name}: {t.description}，参数：{json.dumps(t.parameters, ensure_ascii=False)}"
                for t in request.tools
            ])
        history_text = ""
        if request.history:
            history_text = "历史对话：\n" + "\n".join([
                f"{h.role}: {h.content}" for h in request.history
            ]) + "\n"
        return f"""{request.system_prompt}

{tool_desc}

{history_text}用户问题：{request.user_query}

请根据可用工具回答问题。如果需要调用工具，请在回答中说明调用了什么工具。"""

    def _build_reflection_query(self, user_query: str, draft: str, tool_results: List[Dict[str, Any]]) -> str:
        tool_text = "\n".join([f"工具 {r.get('name')} 调用参数：{r.get('arguments')}" for r in tool_results]) or "无工具调用"
        return f"""你是一位严格的回答质量检查员。请检查下面的初稿回答，指出是否存在以下问题：

1. 事实性错误
2. 遗漏了用户问题中的某个要求
3. 逻辑不自洽
4. 回答过于冗长或过于简短
5. 表达不清晰

用户问题：{user_query}
工具调用记录：{tool_text}
初稿回答：{draft}

请以 JSON 格式输出：
{{
  "has_issue": true/false,
  "issues": ["问题1", "问题2"],
  "suggestions": ["建议1", "建议2"]
}}"""

    def _parse_reflection(self, text: str) -> Dict[str, Any]:
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                return json.loads(text[start:end+1])
        except Exception:
            pass
        return {"has_issue": False, "issues": [], "suggestions": []}

    def _build_revise_query(self, draft: str, reflection: str) -> str:
        return f"""请根据以下反思意见，修正初稿回答并生成最终回答。

要求：
- 只输出最终回答，不要解释修改过程
- 确保回答准确、完整、简洁
- 如果反思认为没有 issue，可直接使用初稿

初稿：{draft}
反思意见：{reflection}

最终回答："""

agent_engine = AgentEngine()
