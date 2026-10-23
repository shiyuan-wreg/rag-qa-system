"""招魂台核心逻辑:经 Wayback Machine 快照恢复已注销 B 站账号的身份。

恢复原理:B 站注销后 UID 不变,空间页标题从
  "<昵称>的个人空间-<昵称>个人主页-哔哩哔哩视频"
变为
  "的个人空间-个人主页-哔哩哔哩视频"
Wayback 的历史快照保留了注销前的标题,二分定位"最后一个有昵称 /
第一个空昵称"的快照对,即得注销时间窗口。
"""
from __future__ import annotations

import re
from dataclasses import dataclass

CDX_API = "https://web.archive.org/cdx/search/cdx"
SNAPSHOT = "https://web.archive.org/web/{ts}id_/https://space.bilibili.com/{uid}"
UA = {"User-Agent": "Mozilla/5.0 (compatible; bili-seance/1.0; +https://www.shiyuan-wreg.cloud)"}

# 快照标题:命名版 "<nick>的个人空间-<nick>个人主页-...",空昵称版 "的个人空间-个人主页-..."
_TITLE_RE = re.compile(r"<title>(.*?)</title>", re.S)
_NICK_RE = re.compile(r"^(.*?)的个人空间-")


class DigError(Exception):
    """上游(archive.org)不可用或返回异常。"""


def _get_with_retry(http_get, url: str, params: dict | None = None, attempts: int = 3) -> str:
    """Tor 出口抖动是常态(部分出口被 archive.org 间歇限制),失败换电路重试。"""
    import time
    last: Exception | None = None
    for i in range(attempts):
        try:
            return http_get(url, params=params)
        except Exception as exc:  # noqa: BLE001 - 统一由上层归类
            last = exc
            if i < attempts - 1:
                time.sleep(2 * (i + 1))
    raise last  # type: ignore[misc]


@dataclass
class Snap:
    ts: str          # CDX 时间戳 yyyyMMddHHmmss
    named: bool      # 该快照标题里是否还有昵称
    nick: str | None # named 时的昵称


def parse_nickname(html: str) -> str | None:
    """从空间页 HTML 提取昵称;空昵称或无法解析返回 None。"""
    m = _TITLE_RE.search(html)
    if not m:
        return None
    title = m.group(1).strip()
    nm = _NICK_RE.match(title)
    if not nm:
        return None
    nick = nm.group(1).strip()
    return nick or None


def _fmt_ts(ts: str) -> str:
    return f"{ts[0:4]}-{ts[4:6]}-{ts[6:8]}"


def dig(uid: str, http_get) -> dict:
    """对一个 UID 执行招魂。http_get(url, params=None) -> str,可注入以便测试。

    返回 dict:status 取值
      sealed       招魂成功:拿到昵称 + 注销时间窗
      sealed_early 首次存档前就已注销,拿不到昵称
      alive        最新快照里昵称仍在(注销发生在存档之后或无注销)
      none         Wayback 无任何存档
    """
    try:
        cdx_text = _get_with_retry(http_get, CDX_API, params={
            "url": f"space.bilibili.com/{uid}",
            "output": "json",
            "fl": "timestamp",
            "filter": "statuscode:200",
            "collapse": "digest",
        })
    except Exception as exc:  # noqa: BLE001 - 上游网络错误统一归类
        raise DigError(f"Wayback CDX 查询失败: {exc}") from exc

    import json
    try:
        rows = json.loads(cdx_text)
    except ValueError as exc:
        raise DigError("Wayback CDX 返回了非 JSON 内容") from exc
    # 首行是表头 ["timestamp"]
    timestamps = sorted(r[0] for r in rows[1:] if r) if rows else []
    if not timestamps:
        return {"status": "none", "uid": uid}

    probed: dict[str, Snap] = {}

    def probe(ts: str) -> Snap:
        if ts in probed:
            return probed[ts]
        try:
            html = _get_with_retry(http_get, SNAPSHOT.format(ts=ts, uid=uid))
        except Exception as exc:  # noqa: BLE001
            raise DigError(f"抓取快照 {_fmt_ts(ts)} 失败: {exc}") from exc
        nick = parse_nickname(html)
        snap = Snap(ts=ts, named=nick is not None, nick=nick)
        probed[ts] = snap
        return snap

    first = probe(timestamps[0])
    last = probe(timestamps[-1])

    if last.named:
        return {
            "status": "alive", "uid": uid, "nickname": last.nick,
            "last_seen": _fmt_ts(last.ts), "snaps": sorted(probed.values(), key=lambda s: s.ts),
        }
    if not first.named:
        return {
            "status": "sealed_early", "uid": uid,
            "first_blank": _fmt_ts(first.ts), "snaps": sorted(probed.values(), key=lambda s: s.ts),
        }

    # 二分:在 timestamps 中定位 [named ... | blank ...] 边界
    lo, hi = 0, len(timestamps) - 1  # probe(lo) named, probe(hi) blank 恒成立
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if probe(timestamps[mid]).named:
            lo = mid
        else:
            hi = mid
    boundary_named = probe(timestamps[lo])
    return {
        "status": "sealed", "uid": uid, "nickname": boundary_named.nick,
        "window": {"last_named": _fmt_ts(timestamps[lo]), "first_blank": _fmt_ts(timestamps[hi])},
        "snaps": sorted(probed.values(), key=lambda s: s.ts),
    }
