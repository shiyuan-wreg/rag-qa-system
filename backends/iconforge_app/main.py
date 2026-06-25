"""FastAPI app for IconForge - 图标净化器。"""
import json

from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import cleaner
from config import APP_DIR, Config
from models import CleanResponse

app = FastAPI(title="IconForge - 图标净化器")
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "home.html", {})


@app.post("/api/clean", response_model=CleanResponse)
async def clean_endpoint(
    file: UploadFile = File(...),
    ops: str = Form(...),
    params: str = Form("{}"),
):
    data = await file.read()
    if len(data) > Config.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="文件超过 5 MiB 上限")
    op_list = [o.strip() for o in ops.split(",") if o.strip()]
    if not op_list:
        raise HTTPException(status_code=400, detail="请至少勾选一个操作")
    try:
        param_dict = json.loads(params or "{}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="params 不是合法 JSON")
    try:
        result = cleaner.clean(data, file.filename or "", op_list, param_dict)
    except cleaner.CleanError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result
