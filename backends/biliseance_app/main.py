"""招魂台 BiliSéance - 已注销 B 站账号身份恢复工具。

唯一对外接口 GET /api/dig?uid=<纯数字>:
经 Wayback Machine 快照恢复昵称与注销时间窗。不含任何 B 站登录态。
"""
import re
import threading
import time
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.concurrency import run_in_threadpool

try:
    from . import digger
except ImportError:  # pragma: no cover - Docker CMD main:app 直跑
    import digger

APP_DIR = Path(__file__).resolve().parent
UID_RE = re.compile(r"^\d{1,20}$")

RATE_LIMIT = 10        # 次
RATE_WINDOW = 60       # 秒
CACHE_TTL = 24 * 3600  # 秒

app = FastAPI(title="招魂台 BiliSéance")
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")

_lock = threading.Lock()
_hits: dict[str, list[float]] = {}   # ip -> 请求时间戳
_cache: dict[str, tuple[float, dict]] = {}  # uid -> (过期时间, 结果)


def _check_rate(ip: str) -> bool:
    now = time.time()
    with _lock:
        ts = [t for t in _hits.get(ip, []) if now - t < RATE_WINDOW]
        if len(ts) >= RATE_LIMIT:
            _hits[ip] = ts
            return False
        ts.append(now)
        _hits[ip] = ts
        return True


def _http_get(url: str, params: dict | None = None) -> str:
    with httpx.Client(timeout=20.0, headers=digger.UA, follow_redirects=True) as client:
        resp = client.get(url, params=params)
        resp.raise_for_status()
        # archive.org 响应常不带 charset,httpx 自动嗅探会把中文误判成 GBK,强制 UTF-8
        return resp.content.decode("utf-8", errors="replace")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "home.html", {})


@app.get("/api/dig")
async def api_dig(request: Request, uid: str = ""):
    if not UID_RE.match(uid):
        raise HTTPException(status_code=400, detail="uid 必须是 1-20 位纯数字")
    ip = request.client.host if request.client else "unknown"
    if not _check_rate(ip):
        raise HTTPException(status_code=429, detail="查询太频繁,歇一分钟再招")

    now = time.time()
    with _lock:
        cached = _cache.get(uid)
    if cached and cached[0] > now:
        return cached[1]

    try:
        result = await run_in_threadpool(digger.dig, uid, _http_get)
    except digger.DigError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    with _lock:
        _cache[uid] = (now + CACHE_TTL, result)
    return result
