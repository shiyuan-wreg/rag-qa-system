import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/backends/md_converter_app")

from fastapi.testclient import TestClient
from main import app


def test_public_root():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200


def test_login_page():
    client = TestClient(app)
    response = client.get("/login")
    assert response.status_code == 200


def test_protected_jobs_redirects_when_not_logged_in():
    client = TestClient(app)
    response = client.get("/api/jobs", follow_redirects=False)
    assert response.status_code == 307
    assert "/login" in response.headers["location"]


def test_path_conversion_when_enabled(tmp_path, monkeypatch):
    from config import Config
    monkeypatch.setattr(Config, "DOCHUB_ALLOW_PATH_CONVERT", True)

    client = TestClient(app)
    response = client.post("/login", data={"password": "test-password"}, follow_redirects=False)
    cookies = response.cookies

    src = tmp_path / "src"
    src.mkdir()
    (src / "doc.md").write_text("# Doc", encoding="utf-8")

    response = client.post(
        "/api/convert/path",
        data={"path": str(src)},
        cookies=cookies,
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "/browse/" in response.headers["location"]
