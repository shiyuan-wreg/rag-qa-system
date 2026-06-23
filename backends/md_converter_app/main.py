"""FastAPI app for DocHub."""

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from auth import AuthManager
from config import Config
from store import JobStore

app = FastAPI(title="DocHub - Markdown 文档站")
app.mount("/static", StaticFiles(directory="backends/md_converter_app/static"), name="static")

templates = Jinja2Templates(directory="backends/md_converter_app/templates")
auth_manager = AuthManager(Config.DOCHUB_PASSWORD, Config.SECRET_KEY)
job_store = JobStore()


def is_authenticated(request: Request) -> bool:
    session_token = request.cookies.get("dochub_session")
    return auth_manager.verify_session(session_token)


def require_auth(request: Request):
    if not is_authenticated(request):
        return RedirectResponse("/login", status_code=307)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    if is_authenticated(request):
        return templates.TemplateResponse(request, "home.html", {
            "jobs": job_store.list(),
            "allow_path": Config.DOCHUB_ALLOW_PATH_CONVERT,
        })
    return templates.TemplateResponse(request, "login.html", {"error": ""})


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html", {"error": ""})


@app.post("/login")
def login(request: Request, password: str = Form(...)):
    if auth_manager.verify(password):
        response = RedirectResponse("/", status_code=303)
        response.set_cookie("dochub_session", auth_manager.create_session(), httponly=True)
        return response
    return templates.TemplateResponse(request, "login.html", {"error": "密码错误"})


@app.post("/logout")
def logout():
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("dochub_session")
    return response


@app.get("/api/jobs")
def list_jobs(request: Request):
    if not is_authenticated(request):
        return RedirectResponse("/login", status_code=307)
    return [{"job_id": j.job_id, "source_type": j.source_type, "source_name": j.source_name, "status": j.status} for j in job_store.list()]
