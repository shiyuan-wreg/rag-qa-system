from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class ToolInfo(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    agent_code: str
    system_prompt: str
    model_name: str = "glm-4-flash"
    temperature: float = 0.7
    max_rounds: int = 10
    user_query: str
    history: List[ChatMessage] = []
    tools: List[ToolInfo] = []

class StepOutput(BaseModel):
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    result: Optional[str] = None
    has_issue: Optional[bool] = None
    issues: Optional[List[str]] = None
    suggestions: Optional[List[str]] = None

class Step(BaseModel):
    step_type: str
    step_order: int
    input: Optional[Dict[str, Any]] = None
    output: Optional[StepOutput] = None
    duration_ms: int = 0

class ChatData(BaseModel):
    final_response: str
    total_tokens: int = 0
    duration_ms: int = 0
    steps: List[Step] = []

class ChatResponse(BaseModel):
    success: bool
    data: Optional[ChatData] = None
    error: Optional[str] = None
