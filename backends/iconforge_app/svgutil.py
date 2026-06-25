"""SVG 文本 ↔ 路径 / 颜色 / 几何 工具。仅处理自闭合 <path> 标签。"""
import re

PATH_RE = re.compile(r"<path\b[^>]*?/>", re.S)
FILL_RGB_RE = re.compile(r'fill="rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)"')
FILL_HEX_RE = re.compile(r'fill="(#[0-9a-fA-F]{3,6})"')
D_RE = re.compile(r'\bd="([^"]*)"')
NUM_RE = re.compile(r"-?\d+\.?\d*")


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def parse_fill(tag: str):
    m = FILL_RGB_RE.search(tag)
    if m:
        return tuple(int(x) for x in m.groups())
    m = FILL_HEX_RE.search(tag)
    if m:
        return _hex_to_rgb(m.group(1))
    return None


def extract_paths(svg: str) -> list[str]:
    return PATH_RE.findall(svg)


def path_coords(d: str):
    nums = [float(n) for n in NUM_RE.findall(d)]
    return nums[0::2], nums[1::2]


def bbox(paths: list[str]):
    xs, ys = [], []
    for p in paths:
        m = D_RE.search(p)
        if not m:
            continue
        px, py = path_coords(m.group(1))
        xs += px
        ys += py
    if not xs or not ys:
        raise ValueError("no coordinates found")
    return min(xs), min(ys), max(xs), max(ys)


def tighten_viewbox(minx, miny, maxx, maxy, padding):
    w, h = maxx - minx, maxy - miny
    pad = max(w, h) * padding
    minx -= pad
    miny -= pad
    w += 2 * pad
    h += 2 * pad
    return f"{minx:.1f} {miny:.1f} {w:.1f} {h:.1f}", w, h
