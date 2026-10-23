"""API 层测试:uid 校验 / 限流 / 缓存,digger 一律 mock,不碰网络。"""
import pytest
from fastapi.testclient import TestClient

from backends.biliseance_app import main


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(main, "_hits", {})
    monkeypatch.setattr(main, "_cache", {})
    return TestClient(main.app)


def test_healthz(client):
    assert client.get("/healthz").json() == {"status": "ok"}


@pytest.mark.parametrize("bad", ["", "abc", "12a34", "1" * 21, "-5", "12 34"])
def test_invalid_uid_rejected(client, bad):
    assert client.get("/api/dig", params={"uid": bad}).status_code == 400


def test_dig_success(monkeypatch, client):
    monkeypatch.setattr(
        main.digger, "dig",
        lambda uid, http: {"status": "sealed", "uid": uid, "nickname": "喵子魔法本"},
    )
    r = client.get("/api/dig", params={"uid": "3493135860631798"})
    assert r.status_code == 200
    assert r.json()["nickname"] == "喵子魔法本"


def test_dig_upstream_error_becomes_502(monkeypatch, client):
    def boom(uid, http):
        raise main.digger.DigError("Wayback CDX 查询失败: timeout")

    monkeypatch.setattr(main.digger, "dig", boom)
    assert client.get("/api/dig", params={"uid": "123"}).status_code == 502


def test_rate_limit(monkeypatch, client):
    monkeypatch.setattr(main.digger, "dig", lambda uid, http: {"status": "none", "uid": uid})
    for i in range(main.RATE_LIMIT):
        assert client.get("/api/dig", params={"uid": str(1000 + i)}).status_code == 200
    assert client.get("/api/dig", params={"uid": "9999"}).status_code == 429


def test_cache_hits_digger_once(monkeypatch, client):
    calls = []

    def fake_dig(uid, http):
        calls.append(uid)
        return {"status": "none", "uid": uid}

    monkeypatch.setattr(main.digger, "dig", fake_dig)
    client.get("/api/dig", params={"uid": "123"})
    client.get("/api/dig", params={"uid": "123"})
    assert calls == ["123"]
