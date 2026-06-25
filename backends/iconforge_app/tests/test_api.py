import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


def test_healthz():
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

import json

DIRTY_SVG = (
    '<svg viewBox="0 0 500 500">'
    '<path fill="rgb(253,253,253)" d="M 0 0 L 500 0 L 500 500 Z"/>'
    '<path fill="rgb(23,24,23)" d="M 100 100 L 200 100 L 200 200 Z"/>'
    '</svg>'
)

def test_clean_svg_dewhite_mono():
    files = {"file": ("x.svg", DIRTY_SVG, "image/svg+xml")}
    data = {"ops": "dewhite,mono"}
    r = client.post("/api/clean", files=files, data=data)
    assert r.status_code == 200
    body = r.json()
    assert "#171817" in body["svg"]
    assert "rgb(253,253,253)" not in body["svg"]
    assert body["stats"]["pathsKept"] == 1

def test_clean_empty_ops_400():
    files = {"file": ("x.svg", DIRTY_SVG, "image/svg+xml")}
    r = client.post("/api/clean", files=files, data={"ops": ""})
    assert r.status_code in (400, 422)

def test_index_serves_html():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
