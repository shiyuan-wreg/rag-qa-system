"""FastAPI app for DocHub."""

from pathlib import Path

from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from auth import AuthManager
from config import Config
from store import JobStore
from converter import build_global_index, convert_directory, convert_markdown_file, build_dir_index

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


@app.post("/api/convert/upload")
async def convert_upload(request: Request, file: UploadFile = File(...)):
    if not is_authenticated(request):
        return RedirectResponse("/login", status_code=307)

    if not file.filename or not file.filename.lower().endswith(".md"):
        raise HTTPException(status_code=400, detail="只支持 .md 文件")

    content = await file.read()
    if len(content) > Config.MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="文件超过 10MB 限制")

    Config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    job = job_store.create("upload", file.filename, "")
    job_dir = Config.UPLOAD_DIR / job.job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    md_path = job_dir / file.filename
    md_path.write_bytes(content)

    out_dir = Config.OUTPUT_DIR / "uploads" / job.job_id
    out_dir.mkdir(parents=True, exist_ok=True)

    job_store.update_status(job.job_id, "running")
    try:
        convert_markdown_file(md_path, out_dir / md_path.with_suffix(".html").name, index_link="index.html")
        build_dir_index(out_dir, list(out_dir.glob("*.html")), out_dir)
        job.output_dir = str(out_dir.relative_to(Config.OUTPUT_DIR))
        job_store.update_status(job.job_id, "done")
        build_global_index(Config.OUTPUT_DIR)
    except Exception as e:
        job_store.update_status(job.job_id, "error", str(e))
        import shutil
        shutil.rmtree(out_dir, ignore_errors=True)
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=500, detail=str(e))

    return RedirectResponse("/doctomd/browse/", status_code=303)


@app.post("/api/convert/path")
async def convert_path(request: Request, path: str = Form(...)):
    if not is_authenticated(request):
        return RedirectResponse("/login", status_code=307)

    if not Config.DOCHUB_ALLOW_PATH_CONVERT:
        raise HTTPException(status_code=403, detail="路径转换功能已禁用")

    if ".." in path:
        raise HTTPException(status_code=400, detail="非法路径")

    src_path = Path(path).resolve()
    if not src_path.exists() or not src_path.is_dir():
        raise HTTPException(status_code=400, detail="路径不存在或不是目录")

    Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    job = job_store.create("path", src_path.name, "")
    out_dir = Config.OUTPUT_DIR / "paths" / job.job_id
    out_dir.mkdir(parents=True, exist_ok=True)

    job_store.update_status(job.job_id, "running")
    try:
        convert_directory(src_path, out_dir, job.job_id)
        job.output_dir = str(out_dir.relative_to(Config.OUTPUT_DIR))
        job_store.update_status(job.job_id, "done")
        build_global_index(Config.OUTPUT_DIR)
    except Exception as e:
        job_store.update_status(job.job_id, "error", str(e))
        raise HTTPException(status_code=500, detail=str(e))

    return RedirectResponse("/doctomd/browse/", status_code=303)
