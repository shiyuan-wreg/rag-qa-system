"""FastAPI app for IconForge - 图标净化器."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import APP_DIR

app = FastAPI(title="IconForge - 图标净化器")
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
