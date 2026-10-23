"""digger 纯逻辑测试:全程注入假 fetcher,不碰网络。"""
import json

import pytest

from backends.biliseance_app import digger

NAMED = "<html><title>喵子魔法本的个人空间-喵子魔法本个人主页-哔哩哔哩视频</title></html>"
BLANK = "<html><title>的个人空间-个人主页-哔哩哔哩视频</title></html>"


def make_http(cdx_ts, titles):
    """cdx_ts: 时间戳列表;titles: {ts: html}。返回 (http_get, calls)。"""
    calls = []

    def http_get(url, params=None):
        calls.append(url)
        if "cdx" in url:
            rows = [["timestamp"]] + [[t] for t in cdx_ts]
            return json.dumps(rows)
        ts = url.split("/web/")[1].split("id_")[0]
        return titles[ts]

    return http_get, calls


def test_parse_nickname_named():
    assert digger.parse_nickname(NAMED) == "喵子魔法本"


def test_parse_nickname_blank():
    assert digger.parse_nickname(BLANK) is None


def test_parse_nickname_no_title():
    assert digger.parse_nickname("<html><body>error</body></html>") is None


def test_no_snapshots():
    http, _ = make_http([], {})
    assert digger.dig("123", http)["status"] == "none"


def test_alive_when_last_snapshot_named():
    ts = ["20240910102533", "20240913185118"]
    http, _ = make_http(ts, {t: NAMED for t in ts})
    r = digger.dig("123", http)
    assert r["status"] == "alive"
    assert r["nickname"] == "喵子魔法本"
    assert r["last_seen"] == "2024-09-13"


def test_sealed_early_when_first_snapshot_blank():
    ts = ["20250218101317", "20250223105408"]
    http, _ = make_http(ts, {t: BLANK for t in ts})
    r = digger.dig("123", http)
    assert r["status"] == "sealed_early"
    assert "nickname" not in r


def test_sealed_window_binary_search():
    """4 个快照:前两个有昵称后两个空(真实案例),边界=0913/0218。"""
    ts = ["20240910102533", "20240913185118", "20250218101317", "20250223105408"]
    titles = {ts[0]: NAMED, ts[1]: NAMED, ts[2]: BLANK, ts[3]: BLANK}
    http, calls = make_http(ts, titles)
    r = digger.dig("3493135860631798", http)
    assert r["status"] == "sealed"
    assert r["nickname"] == "喵子魔法本"
    assert r["window"] == {"last_named": "2024-09-13", "first_blank": "2025-02-18"}
    # 二分:首+尾+1 次 mid+1 次边界,不应逐个抓取全部快照
    snap_fetches = [c for c in calls if "/web/" in c]
    assert len(snap_fetches) <= 4


def test_binary_search_larger_archive():
    """10 个快照,第 6 个起变空,验证二分找到精确边界且抓取数 O(log n)。"""
    ts = [f"2024{m:02d}01000000" for m in range(1, 11)]
    titles = {t: (NAMED if i < 5 else BLANK) for i, t in enumerate(ts)}
    http, calls = make_http(ts, titles)
    r = digger.dig("123", http)
    assert r["status"] == "sealed"
    assert r["window"] == {"last_named": "2024-05-01", "first_blank": "2024-06-01"}
    assert len([c for c in calls if "/web/" in c]) <= 5  # log2(10)≈3.3 + 首尾


def test_cdx_non_json_raises_digerror():
    def bad_http(url, params=None):
        return "<html>Wayback error page</html>"

    with pytest.raises(digger.DigError):
        digger.dig("123", bad_http)


def test_cdx_network_error_raises_digerror():
    def dead_http(url, params=None):
        raise ConnectionError("timeout")

    with pytest.raises(digger.DigError):
        digger.dig("123", dead_http)


def test_retry_recovers_from_transient_tor_failure():
    """前两次抓取失败、第三次成功(Tor 出口抖动场景),dig 应正常返回。"""
    ts = ["20240910102533"]
    attempts = []

    def flaky(url, params=None):
        if "cdx" in url:
            return json.dumps([["timestamp"]] + [[t] for t in ts])
        attempts.append(url)
        if len(attempts) < 3:
            raise OSError("General SOCKS server failure")
        return NAMED

    r = digger.dig("123", flaky)
    assert r["status"] == "alive"
    assert len(attempts) == 3


def test_retry_exhausted_raises_digerror():
    """持续失败应在 3 次尝试后抛 DigError,而不是无限重试。"""
    def always_dead(url, params=None):
        raise OSError("SOCKS failure")

    with pytest.raises(digger.DigError):
        digger.dig("123", always_dead)
