from fastapi import FastAPI, Request, HTTPException
from app.config import settings
from app.api.agent import router as agent_router

app = FastAPI(title="Agent Console AI Service", version="1.0.0")

@app.middleware("http")
async def internal_auth_middleware(request: Request, call_next):
    if request.url.path in ["/health", "/docs", "/openapi.json"]:
        return await call_next(request)
    internal_key = request.headers.get("X-Internal-Key")
    if internal_key != settings.internal_key:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await call_next(request)

app.include_router(agent_router, prefix="/agent", tags=["agent"])

@app.get("/health")
def health():
    return {"status": "ok"}
