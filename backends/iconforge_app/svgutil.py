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


FILL_ANY_RE = re.compile(r'fill="[^"]*"')
STROKE_ANY_RE = re.compile(r'stroke="[^"]*"')


def is_near_white(rgb, threshold) -> bool:
    return all(c > threshold for c in rgb)


def _build_svg(paths: list[str], view_box: str, w: float, h: float) -> str:
    body = "".join(paths)
    return (
        "<?xml version='1.0' encoding='utf-8'?>\n"
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{view_box}" width="{w:.0f}" height="{h:.0f}" version="1.1">'
        f"{body}</svg>\n"
    )


def dewhite(svg: str, threshold, padding):
    paths = extract_paths(svg)
    dropped = 0
    kept_paths = []
    for p in paths:
        rgb = parse_fill(p)
        if rgb is not None and is_near_white(rgb, threshold):
            dropped += 1
            continue
        kept_paths.append(p)
    if not kept_paths:
        raise ValueError("去白边后没有剩余路径(可能整图都被判为背景)")
    minx, miny, maxx, maxy = bbox(kept_paths)
    view_box, w, h = tighten_viewbox(minx, miny, maxx, maxy, padding)
    return _build_svg(kept_paths, view_box, w, h), len(kept_paths), dropped


def _recolor_one(tag: str, color: str) -> str:
    if FILL_ANY_RE.search(tag):
        tag = FILL_ANY_RE.sub(f'fill="{color}"', tag, count=1)
    else:
        tag = tag.replace("<path", f'<path fill="{color}"', 1)
    if STROKE_ANY_RE.search(tag):
        tag = STROKE_ANY_RE.sub(f'stroke="{color}"', tag)
    return tag


def monochrome(svg: str, color: str) -> str:
    for tag in extract_paths(svg):
        svg = svg.replace(tag, _recolor_one(tag, color))
    return svg
