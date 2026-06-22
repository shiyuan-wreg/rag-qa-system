from fastapi import APIRouter
from app.core.agent_engine import agent_engine
from app.schemas import ChatRequest, ChatResponse

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    return agent_engine.chat(request)
