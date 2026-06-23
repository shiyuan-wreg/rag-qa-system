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


def test_upload_md_file_conversion(tmp_path, monkeypatch):
    client = TestClient(app)

    # Login first
    response = client.post("/login", data={"password": "test-password"}, follow_redirects=False)
    assert response.status_code == 303
    cookies = response.cookies

    # Upload file
    md_content = b"# Test\n\nHello world."
    response = client.post(
        "/api/convert/upload",
        files={"file": ("test.md", md_content, "text/markdown")},
        cookies=cookies,
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "/browse/" in response.headers["location"]
