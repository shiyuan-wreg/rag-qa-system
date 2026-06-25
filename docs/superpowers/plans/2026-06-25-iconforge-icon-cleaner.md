# IconForge 图标净化器 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 ai-demos 新增第 6 个无状态 web demo `/iconforge/`,让用户上传图标(PNG/JPG/SVG)、自选净化操作(位图转矢量 / 去除白边 / 彩色转黑色),实时预览并下载干净的单色 SVG。

**Architecture:** FastAPI 服务(端口 8005),核心净化逻辑与 HTTP 解耦。**SVG 输入**走 `svgutil`(正则解析路径、按亮度剥近白、重算紧贴 viewBox、单色化);**位图输入**走 `tracer`(Pillow 裁到内容 + 二值化 → potrace 描摹 → 改色),裁剪保证 viewBox 天然紧贴,绕开 potrace 变换坐标的坑。`cleaner` 按 A→B→C 顺序编排被勾选的操作。接线 100% 照搬 DocHub(`md_converter_app`)。

**Tech Stack:** Python 3.12、FastAPI、uvicorn、Pillow、potrace(系统二进制,apt)、Jinja2、原生 JS 前端、Docker/compose/nginx。

## Global Constraints

- 目标单色 = `#171817`(= `rgb(23,24,23)`),与门户 `.demo-icon` 暗色反白逻辑一致 —— 来自 spec。
- 去白边亮度阈值默认 `120`(三通道均 > 阈值视为白/背景,丢弃);padding 默认 `0.06`;最大上传 `5 MiB` —— 来自 spec。
- 无状态:处理完即返回 JSON,服务端不落盘,无账号/无 store —— 来自 spec。
- 服务端口 `8005`,路由 `/iconforge/`,服务名 `iconforge` —— 来自 spec。
- 操作顺序固定 **A(trace)→ B(dewhite)→ C(mono)**,跑不跑由前端勾选传 `ops` 决定 —— 来自 spec。
- 所有新文件遵循 DocHub 现有结构与命名;shell/Dockerfile/conf 用 LF(仓库 `.gitattributes` 已强制)。
- 工作区:redesign worktree `C:\Users\hzs17\Desktop\ai-demos\.claude\worktrees\feat+portfolio-ui-redesign`,分支 `worktree-feat+portfolio-ui-redesign`。所有命令 `cd` 到该 worktree 根执行。

---

## File Structure

```
backends/iconforge_app/
  __init__.py
  config.py            常量(默认色/阈值/padding/上限)
  models.py            CleanStats / CleanResponse (pydantic)
  svgutil.py           SVG 文本↔路径/颜色/几何:extract_paths/parse_fill/bbox/tighten/dewhite/monochrome
  tracer.py            位图→SVG:Pillow 裁内容+二值化 → potrace → 改色
  cleaner.py           编排:按 ops 分派 svg/raster 分支,A→B→C,产出 CleanResult
  main.py              FastAPI:POST /api/clean、首页、/healthz;挂 static、模板
  static/app.js        前端逻辑(上传、勾选、请求、预览、下载、复制)
  static/style.css     mono 主题样式
  templates/home.html  单页 UI
  tests/__init__.py
  tests/test_svgutil.py
  tests/test_tracer.py
  tests/test_cleaner.py
  tests/test_api.py
  requirements.txt
  Dockerfile

deploy/docker-compose.yml          + iconforge 服务、nginx depends_on
deploy/nginx/nginx.conf            + location /iconforge/
deploy/nginx/nginx.local.conf      + location /iconforge/
frontends/portfolio/src/data/works.ts          + 第 6 张卡
frontends/portfolio/public/icons/iconforge.svg + 卡片图标(先占位,后 dogfood 替换)
```

---

### Task 1: Scaffold `iconforge_app` 包 + 配置 + 应用启动

**Files:**
- Create: `backends/iconforge_app/__init__.py`(空)
- Create: `backends/iconforge_app/config.py`
- Create: `backends/iconforge_app/requirements.txt`
- Create: `backends/iconforge_app/main.py`(本任务只含 app + /healthz)
- Create: `backends/iconforge_app/tests/__init__.py`(空)
- Create: `backends/iconforge_app/tests/test_api.py`(本任务只测 /healthz)

**Interfaces:**
- Produces: `config.Config`(`DEFAULT_COLOR`, `DEFAULT_THRESHOLD`, `DEFAULT_PADDING`, `MAX_UPLOAD_BYTES`, `RASTER_THRESHOLD`),`config.APP_DIR`;FastAPI `app`,`GET /healthz -> {"status":"ok"}`。

- [ ] **Step 1: 写 config.py**

```python
"""IconForge configuration constants."""
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent


class Config:
    DEFAULT_COLOR = "#171817"        # = rgb(23,24,23)
    DEFAULT_THRESHOLD = 120          # dewhite: 三通道均 > 此值视为白/背景
    DEFAULT_PADDING = 0.06           # 紧贴 viewBox 外扩比例
    RASTER_THRESHOLD = 128           # 位图二值化:像素 < 此值算墨(前景)
    MAX_UPLOAD_BYTES = 5 * 1024 * 1024
```

- [ ] **Step 2: 写 requirements.txt**

```
fastapi==0.111.0
uvicorn==0.30.0
jinja2==3.1.4
python-multipart==0.0.9
Pillow==10.3.0
pytest==8.2.0
httpx==0.27.0
```

- [ ] **Step 3: 写 main.py(最小可启动)**

```python
"""FastAPI app for IconForge - 图标净化器."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import APP_DIR

app = FastAPI(title="IconForge - 图标净化器")
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}
```

- [ ] **Step 4: 建占位前端目录(让 StaticFiles/模板挂载不报错)**

```bash
cd "C:/Users/hzs17/Desktop/ai-demos/.claude/worktrees/feat+portfolio-ui-redesign"
mkdir -p backends/iconforge_app/static backends/iconforge_app/templates backends/iconforge_app/tests
printf '' > backends/iconforge_app/static/.gitkeep
printf '<!doctype html><title>IconForge</title>' > backends/iconforge_app/templates/home.html
printf '' > backends/iconforge_app/__init__.py
printf '' > backends/iconforge_app/tests/__init__.py
```

- [ ] **Step 5: 写 tests/test_api.py(只测 healthz)**

```python
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
```

- [ ] **Step 6: 装依赖并跑测试,确认通过**

Run:
```bash
cd "C:/Users/hzs17/Desktop/ai-demos/.claude/worktrees/feat+portfolio-ui-redesign/backends/iconforge_app"
pip install -r requirements.txt
python -m pytest tests/test_api.py -v
```
Expected: `test_healthz PASSED`

- [ ] **Step 7: 提交**

```bash
cd "C:/Users/hzs17/Desktop/ai-demos/.claude/worktrees/feat+portfolio-ui-redesign"
git add backends/iconforge_app
git commit -m "feat(iconforge): scaffold FastAPI app with config and healthz"
```

---

### Task 2: `svgutil` 路径解析 + 几何(extract/parse_fill/bbox/tighten)

**Files:**
- Create: `backends/iconforge_app/svgutil.py`
- Test: `backends/iconforge_app/tests/test_svgutil.py`

**Interfaces:**
- Produces:
  - `extract_paths(svg: str) -> list[str]` —— 返回所有自闭合 `<path .../>` 标签原文。
  - `parse_fill(tag: str) -> tuple[int,int,int] | None` —— 解析 `fill` 为 (r,g,b),支持 `rgb(r,g,b)` 与 `#rgb`/`#rrggbb`,无则 None。
  - `path_coords(d: str) -> tuple[list[float], list[float]]` —— 从 `d` 提取 xs, ys(全部数字按对)。
  - `bbox(paths: list[str]) -> tuple[float,float,float,float]` —— (minx,miny,maxx,maxy);空则 ValueError。
  - `tighten_viewbox(minx,miny,maxx,maxy,padding) -> tuple[str, float, float]` —— 返回 (viewBox 字符串, w, h)。

- [ ] **Step 1: 写 tests/test_svgutil.py(本任务部分)**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import svgutil


def test_parse_fill_rgb():
    assert svgutil.parse_fill('<path fill="rgb(23,24,23)" d="M0 0"/>') == (23, 24, 23)

def test_parse_fill_hex():
    assert svgutil.parse_fill('<path fill="#171817" d="M0 0"/>') == (23, 24, 23)
    assert svgutil.parse_fill('<path fill="#fff" d="M0 0"/>') == (255, 255, 255)

def test_parse_fill_none():
    assert svgutil.parse_fill('<path d="M0 0"/>') is None

def test_extract_paths_counts():
    svg = '<svg><path fill="#000" d="M0 0"/><path fill="#fff" d="M1 1"/></svg>'
    assert len(svgutil.extract_paths(svg)) == 2

def test_path_coords():
    xs, ys = svgutil.path_coords("M 10 20 L 30 40 Q 5 6 7 8")
    assert xs == [10, 30, 5, 7]
    assert ys == [20, 40, 6, 8]

def test_bbox():
    paths = ['<path d="M 10 20 L 30 5"/>', '<path d="M 0 50 L 7 8"/>']
    assert svgutil.bbox(paths) == (0, 5, 30, 50)

def test_tighten_viewbox():
    vb, w, h = svgutil.tighten_viewbox(0, 0, 100, 50, 0.0)
    assert vb == "0.0 0.0 100.0 50.0"
    assert (w, h) == (100.0, 50.0)
    vb2, w2, h2 = svgutil.tighten_viewbox(0, 0, 100, 100, 0.1)
    assert w2 == 120.0 and h2 == 120.0  # 0.1*100 padding each side
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python -m pytest tests/test_svgutil.py -v`
Expected: FAIL,`ModuleNotFoundError: No module named 'svgutil'`

- [ ] **Step 3: 写 svgutil.py(本任务部分)**

```python
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
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python -m pytest tests/test_svgutil.py -v`
Expected: 7 passed

- [ ] **Step 5: 提交**

```bash
git add backends/iconforge_app/svgutil.py backends/iconforge_app/tests/test_svgutil.py
git commit -m "feat(iconforge): svgutil path parsing, fill parsing, bbox, viewBox tighten"
```

---

### Task 3: `svgutil` 去白边(dewhite)+ 单色化(monochrome)

**Files:**
- Modify: `backends/iconforge_app/svgutil.py`
- Test: `backends/iconforge_app/tests/test_svgutil.py`(追加)

**Interfaces:**
- Consumes: `extract_paths`, `parse_fill`, `bbox`, `tighten_viewbox`(Task 2)。
- Produces:
  - `is_near_white(rgb, threshold) -> bool` —— 三通道均 > threshold。
  - `dewhite(svg, threshold, padding) -> tuple[str, int, int]` —— 丢弃近白 `<path>`,用保留路径重算紧贴 viewBox 重建 SVG;返回 (新 svg, kept, dropped)。无保留路径则 raise `ValueError`。
  - `monochrome(svg, color) -> str` —— 把所有 `<path>` 的 `fill`/`stroke` 改成 color(无 fill 的补上 fill)。

- [ ] **Step 1: 追加测试**

```python
def test_is_near_white():
    assert svgutil.is_near_white((250, 251, 250), 120) is True
    assert svgutil.is_near_white((23, 24, 23), 120) is False

def test_dewhite_drops_white_keeps_dark_and_tightens():
    svg = (
        '<svg width="500" height="500" viewBox="0 0 500 500">'
        '<path fill="rgb(253,253,253)" d="M 0 0 L 500 0 L 500 500 Z"/>'
        '<path fill="rgb(23,24,23)" d="M 100 100 L 200 100 L 200 200 Z"/>'
        '</svg>'
    )
    out, kept, dropped = svgutil.dewhite(svg, 120, 0.0)
    assert kept == 1 and dropped == 1
    assert "rgb(253,253,253)" not in out
    assert "rgb(23,24,23)" in out
    assert 'viewBox="100.0 100.0 100.0 100.0"' in out

def test_dewhite_all_white_raises():
    svg = '<svg><path fill="#fefefe" d="M0 0 L1 1"/></svg>'
    try:
        svgutil.dewhite(svg, 120, 0.06)
        assert False, "expected ValueError"
    except ValueError:
        pass

def test_monochrome_recolors_all_paths():
    svg = '<svg><path fill="rgb(200,10,10)" d="M0 0"/><path fill="#0a0" d="M1 1"/></svg>'
    out = svgutil.monochrome(svg, "#171817")
    assert out.count('fill="#171817"') == 2
    assert "rgb(200,10,10)" not in out and "#0a0" not in out
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python -m pytest tests/test_svgutil.py -k "dewhite or monochrome or near_white" -v`
Expected: FAIL,`AttributeError: module 'svgutil' has no attribute 'is_near_white'`

- [ ] **Step 3: 追加实现到 svgutil.py**

```python
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
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python -m pytest tests/test_svgutil.py -v`
Expected: 全部 passed(含 Task 2 的 7 个 + 新增 4 个)

- [ ] **Step 5: 提交**

```bash
git add backends/iconforge_app/svgutil.py backends/iconforge_app/tests/test_svgutil.py
git commit -m "feat(iconforge): svgutil dewhite (strip near-white + tighten) and monochrome"
```

---

### Task 4: `tracer` 位图→矢量(Pillow 裁内容 + 二值化 + potrace + 改色)

**Files:**
- Create: `backends/iconforge_app/tracer.py`
- Test: `backends/iconforge_app/tests/test_tracer.py`

**Interfaces:**
- Produces:
  - `class TraceError(Exception)`
  - `potrace_available() -> bool`
  - `trace(image_bytes: bytes, *, color="#171817", threshold=128, invert=False, padding=0.06) -> str` —— 返回一个 viewBox 已紧贴、单色为 color 的 SVG 字符串;potrace 缺失或失败时 raise `TraceError`。

**说明:** 先用 Pillow 把图二值化、`getbbox()` 裁到墨迹范围(+padding)再喂 potrace,因此 potrace 输出的 viewBox 天然等于裁剪尺寸(紧贴),无需解析 potrace 的变换坐标。改色只需把 `<g>` 上的 `fill="#000000"` 替换为目标色。

- [ ] **Step 1: 写 tests/test_tracer.py**

```python
import sys
from pathlib import Path
from io import BytesIO
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
from PIL import Image
import tracer


def _png_with_black_square() -> bytes:
    img = Image.new("L", (64, 64), 255)        # 白底
    for y in range(20, 44):
        for x in range(20, 44):
            img.putpixel((x, y), 0)             # 居中黑方块
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_potrace_available_is_bool():
    assert isinstance(tracer.potrace_available(), bool)


@pytest.mark.skipif(not tracer.potrace_available(), reason="potrace 未安装")
def test_trace_emits_colored_path():
    svg = tracer.trace(_png_with_black_square(), color="#171817")
    assert "<path" in svg
    assert "#171817" in svg
    assert "viewBox" in svg


def test_trace_without_potrace_raises(monkeypatch):
    monkeypatch.setattr(tracer, "potrace_available", lambda: False)
    with pytest.raises(tracer.TraceError):
        tracer.trace(b"not-an-image")
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python -m pytest tests/test_tracer.py -v`
Expected: FAIL,`ModuleNotFoundError: No module named 'tracer'`

- [ ] **Step 3: 写 tracer.py**

```python
"""位图 → 矢量:Pillow 预处理(裁内容 + 二值化) → potrace 描摹 → 改色。"""
import re
import shutil
import subprocess
import tempfile
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps

GFILL_RE = re.compile(r'(<g[^>]*\bfill=")#[0-9a-fA-F]{3,6}(")')


class TraceError(Exception):
    pass


def potrace_available() -> bool:
    return shutil.which("potrace") is not None


def trace(image_bytes, *, color="#171817", threshold=128, invert=False, padding=0.06) -> str:
    if not potrace_available():
        raise TraceError("服务器未安装 potrace,无法位图转矢量")
    try:
        img = Image.open(BytesIO(image_bytes)).convert("L")
    except Exception as exc:  # noqa: BLE001
        raise TraceError(f"无法读取图片:{exc}") from exc

    if invert:
        img = ImageOps.invert(img)

    # 墨迹(前景)= 暗像素。掩膜:墨=255 便于 getbbox 求范围。
    mask = img.point(lambda p: 255 if p < threshold else 0)
    box = mask.getbbox()
    if box is None:
        raise TraceError("图片里没有可描摹的前景(整图过亮或过暗)")
    w, h = img.size
    pad = int(max(box[2] - box[0], box[3] - box[1]) * padding)
    box = (max(0, box[0] - pad), max(0, box[1] - pad),
           min(w, box[2] + pad), min(h, box[3] + pad))

    # 喂 potrace 的位图:墨=黑(0),底=白(255),再裁剪
    bitmap = img.point(lambda p: 0 if p < threshold else 255).convert("1").crop(box)

    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "in.pbm"
        out = Path(td) / "out.svg"
        bitmap.save(src)
        try:
            subprocess.run(["potrace", str(src), "-s", "-o", str(out)],
                           check=True, capture_output=True)
        except subprocess.CalledProcessError as exc:
            raise TraceError(f"potrace 执行失败:{exc.stderr.decode(errors='ignore')}") from exc
        svg = out.read_text(encoding="utf-8")

    # potrace 默认 fill="#000000" 在 <g> 上,改成目标色
    svg = GFILL_RE.sub(rf"\g<1>{color}\g<2>", svg)
    return svg
```

- [ ] **Step 4: 跑测试确认通过(potrace 没装则 trace 用例 skip)**

Run: `python -m pytest tests/test_tracer.py -v`
Expected: `test_potrace_available_is_bool PASSED`、`test_trace_without_potrace_raises PASSED`;描摹用例 PASSED 或 SKIPPED(取决于本机是否装了 potrace)

- [ ] **Step 5: 提交**

```bash
git add backends/iconforge_app/tracer.py backends/iconforge_app/tests/test_tracer.py
git commit -m "feat(iconforge): tracer raster->svg via Pillow crop-to-content + potrace + recolor"
```

---

### Task 5: `cleaner` 编排(按 ops 分派 svg/raster,A→B→C)

**Files:**
- Create: `backends/iconforge_app/cleaner.py`
- Test: `backends/iconforge_app/tests/test_cleaner.py`

**Interfaces:**
- Consumes: `svgutil.extract_paths/dewhite/monochrome`(Task 2/3)、`tracer.trace/TraceError`(Task 4)、`config.Config`。
- Produces:
  - `class CleanError(Exception)`
  - `clean(file_bytes: bytes, filename: str, ops: list[str], params: dict) -> dict` —— 返回 `{"svg": str, "stats": {...}, "warnings": [str]}`。`ops` 取值子集 `{"trace","dewhite","mono"}`,内部强制按 A→B→C 顺序。`params` 可含 `color/threshold/padding/raster_threshold/invert`,缺省取 Config。

**分派规则(与 spec 一致,并锁定健壮性约定):**
- `is_svg`(扩展名 `.svg` 或内容以 `<?xml`/`<svg` 开头)。
- 位图输入:必须含 `trace`,否则 `CleanError`。`trace` 已产出"紧贴 + 单色"结果,故对位图分支 `dewhite` 视为已满足(不再二次跑路径几何),`mono` 体现在 trace 的 color 参数。
- SVG 输入:含 `trace` 时忽略并加 warning;按勾选跑 `dewhite`、`mono`。
- 空 `ops`:`CleanError`(前端也会拦)。

- [ ] **Step 1: 写 tests/test_cleaner.py**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest
import cleaner

DIRTY_SVG = (
    '<svg viewBox="0 0 500 500">'
    '<path fill="rgb(253,253,253)" d="M 0 0 L 500 0 L 500 500 Z"/>'
    '<path fill="rgb(200,10,10)" d="M 100 100 L 200 100 L 200 200 Z"/>'
    '</svg>'
).encode()


def test_svg_dewhite_only():
    r = cleaner.clean(DIRTY_SVG, "x.svg", ["dewhite"], {})
    assert "rgb(253,253,253)" not in r["svg"]
    assert r["stats"]["pathsDropped"] == 1
    assert r["stats"]["pathsKept"] == 1

def test_svg_mono_only_recolors():
    r = cleaner.clean(DIRTY_SVG, "x.svg", ["mono"], {})
    assert r["svg"].count('fill="#171817"') == 2  # 不去白,两条都改色

def test_svg_dewhite_and_mono_order():
    r = cleaner.clean(DIRTY_SVG, "x.svg", ["mono", "dewhite"], {})
    # 强制 A→B→C:先去白(剩1条)再单色 -> 只剩1条且为目标色
    assert r["svg"].count('fill="#171817"') == 1
    assert "rgb(253,253,253)" not in r["svg"]

def test_empty_ops_raises():
    with pytest.raises(cleaner.CleanError):
        cleaner.clean(DIRTY_SVG, "x.svg", [], {})

def test_raster_without_trace_raises():
    with pytest.raises(cleaner.CleanError):
        cleaner.clean(b"\x89PNG\r\n\x1a\n", "x.png", ["dewhite"], {})

def test_svg_with_trace_warns():
    r = cleaner.clean(DIRTY_SVG, "x.svg", ["trace", "dewhite"], {})
    assert any("矢量" in w for w in r["warnings"])
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python -m pytest tests/test_cleaner.py -v`
Expected: FAIL,`ModuleNotFoundError: No module named 'cleaner'`

- [ ] **Step 3: 写 cleaner.py**

```python
"""编排层:按勾选的 ops(强制 A→B→C 顺序)对输入施加净化操作。"""
import svgutil
import tracer
from config import Config


class CleanError(Exception):
    pass


def _looks_like_svg(file_bytes: bytes, filename: str) -> bool:
    if filename.lower().endswith(".svg"):
        return True
    head = file_bytes.lstrip()[:5].lower()
    return head.startswith(b"<?xml") or head.startswith(b"<svg")


def clean(file_bytes, filename, ops, params):
    if not ops:
        raise CleanError("请至少勾选一个操作")

    color = params.get("color") or Config.DEFAULT_COLOR
    threshold = int(params.get("threshold", Config.DEFAULT_THRESHOLD))
    padding = float(params.get("padding", Config.DEFAULT_PADDING))
    raster_threshold = int(params.get("raster_threshold", Config.RASTER_THRESHOLD))
    invert = bool(params.get("invert", False))

    warnings = []
    is_svg = _looks_like_svg(file_bytes, filename)
    bytes_in = len(file_bytes)
    dropped = 0

    if is_svg:
        if "trace" in ops:
            warnings.append("输入已是矢量图,已跳过“位图转矢量”")
        svg = file_bytes.decode("utf-8", "ignore")
        if "dewhite" in ops:
            svg, kept, dropped = svgutil.dewhite(svg, threshold, padding)
        if "mono" in ops:
            svg = svgutil.monochrome(svg, color)
    else:
        if "trace" not in ops:
            raise CleanError("位图输入需要勾选“位图转矢量”")
        try:
            svg = tracer.trace(file_bytes, color=color, threshold=raster_threshold,
                               invert=invert, padding=padding)
        except tracer.TraceError as exc:
            raise CleanError(str(exc)) from exc
        if "dewhite" in ops or "mono" in ops:
            warnings.append("位图描摹结果已是紧贴的单色图,去白边/彩色转黑已自动满足")

    kept_paths = svgutil.extract_paths(svg)
    try:
        minx, miny, maxx, maxy = svgutil.bbox(kept_paths)
        bbox_wh = [round(maxx - minx, 1), round(maxy - miny, 1)]
    except ValueError:
        bbox_wh = [0, 0]

    out = svg.encode("utf-8")
    return {
        "svg": svg,
        "stats": {
            "pathsKept": len(kept_paths),
            "pathsDropped": dropped,
            "bbox": bbox_wh,
            "bytesIn": bytes_in,
            "bytesOut": len(out),
        },
        "warnings": warnings,
    }
```

- [ ] **Step 4: 跑测试确认通过**

Run: `python -m pytest tests/test_cleaner.py -v`
Expected: 6 passed

- [ ] **Step 5: 提交**

```bash
git add backends/iconforge_app/cleaner.py backends/iconforge_app/tests/test_cleaner.py
git commit -m "feat(iconforge): cleaner orchestration (svg/raster dispatch, A->B->C ops)"
```

---

### Task 6: `models` + `POST /api/clean` 端点

**Files:**
- Create: `backends/iconforge_app/models.py`
- Modify: `backends/iconforge_app/main.py`
- Test: `backends/iconforge_app/tests/test_api.py`(追加)

**Interfaces:**
- Consumes: `cleaner.clean/CleanError`、`config.Config`。
- Produces:
  - `models.CleanStats`、`models.CleanResponse`(pydantic,字段同 cleaner 返回的 stats/svg/warnings)。
  - `GET /` 返回 home.html;`POST /api/clean`(multipart:`file`,`ops` 逗号分隔字符串,`params` 可选 JSON 字符串)→ `CleanResponse`。超限/错误返回 400。

- [ ] **Step 1: 追加 API 测试**

```python
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
    assert r.status_code == 400

def test_index_serves_html():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
```

- [ ] **Step 2: 跑测试确认失败**

Run: `python -m pytest tests/test_api.py -v`
Expected: FAIL(`/api/clean` 404 / `/` 不是预期 HTML)

- [ ] **Step 3: 写 models.py**

```python
"""Pydantic 响应模型。"""
from pydantic import BaseModel


class CleanStats(BaseModel):
    pathsKept: int
    pathsDropped: int
    bbox: list[float]
    bytesIn: int
    bytesOut: int


class CleanResponse(BaseModel):
    svg: str
    stats: CleanStats
    warnings: list[str] = []
```

- [ ] **Step 4: 改写 main.py(加首页与 /api/clean)**

```python
"""FastAPI app for IconForge - 图标净化器."""
import json

from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import cleaner
from config import APP_DIR, Config
from models import CleanResponse

app = FastAPI(title="IconForge - 图标净化器")
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
templates = Jinja2Templates(directory=APP_DIR / "templates")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request, "home.html", {})


@app.post("/api/clean", response_model=CleanResponse)
async def clean_endpoint(
    file: UploadFile = File(...),
    ops: str = Form(...),
    params: str = Form("{}"),
):
    data = await file.read()
    if len(data) > Config.MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="文件超过 5 MiB 上限")
    op_list = [o.strip() for o in ops.split(",") if o.strip()]
    try:
        param_dict = json.loads(params or "{}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="params 不是合法 JSON")
    try:
        result = cleaner.clean(data, file.filename or "", op_list, param_dict)
    except cleaner.CleanError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result
```

- [ ] **Step 5: 跑全部测试确认通过**

Run: `python -m pytest -v`
Expected: 全部 passed(svgutil 11 + tracer 2~3 + cleaner 6 + api 4)

- [ ] **Step 6: 提交**

```bash
git add backends/iconforge_app/models.py backends/iconforge_app/main.py backends/iconforge_app/tests/test_api.py
git commit -m "feat(iconforge): models + POST /api/clean endpoint and index page"
```

---

### Task 7: 前端单页 UI(上传 / 勾选 / 预览亮暗 / 下载复制)

**Files:**
- Modify: `backends/iconforge_app/templates/home.html`(替换占位)
- Create: `backends/iconforge_app/static/app.js`
- Create: `backends/iconforge_app/static/style.css`

**Interfaces:**
- Consumes: `POST /api/clean`(返回 `{svg, stats, warnings}`)。
- 静态资源用相对路径 `static/...`(经 nginx 走 `/iconforge/static/...`)。

**说明:** 纯原生 JS,无构建步骤;套黑白 mono 观感。上传后按文件类型自动禁用不适用勾选(SVG 禁用「位图转矢量」)。结果在亮底与暗底各渲染一遍(暗底容器对 `.demo-icon` 套 `filter:invert(1)` 模拟门户暗色主题)。

- [ ] **Step 1: 写 templates/home.html**

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>IconForge 图标净化器</title>
  <link rel="stylesheet" href="static/style.css" />
</head>
<body>
  <main class="wrap">
    <header><span class="num">06</span><h1>IconForge 图标净化器</h1>
      <p class="sub">上传图标 → 自选净化操作 → 下载干净的单色 SVG</p></header>

    <section class="panel">
      <div class="drop" id="drop">
        <input type="file" id="file" accept=".png,.jpg,.jpeg,.svg,image/png,image/jpeg,image/svg+xml" hidden />
        <p id="dropText">拖拽或点击上传<br /><small>PNG / JPG / SVG</small></p>
      </div>
      <div class="ops">
        <label><input type="checkbox" id="op-trace" value="trace" /> A 位图转矢量 <small>(PNG/JPG)</small></label>
        <label><input type="checkbox" id="op-dewhite" value="dewhite" checked /> B 去除白边</label>
        <label><input type="checkbox" id="op-mono" value="mono" checked /> C 彩色转黑色</label>
        <details><summary>高级参数</summary>
          <label>亮度阈值 <input type="number" id="p-threshold" value="120" min="0" max="255" /></label>
          <label>padding <input type="number" id="p-padding" value="0.06" step="0.01" /></label>
          <label><input type="checkbox" id="p-invert" /> 位图反相(浅底深字请勾)</label>
        </details>
        <button id="run">净化</button>
        <p class="msg" id="msg"></p>
      </div>
    </section>

    <section class="result" id="result" hidden>
      <div class="previews">
        <figure><figcaption>原图</figcaption><div class="cell" id="cellOrig"></div></figure>
        <figure><figcaption>结果(亮底)</figcaption><div class="cell light" id="cellLight"></div></figure>
        <figure><figcaption>结果(暗底)</figcaption><div class="cell dark" id="cellDark"></div></figure>
      </div>
      <p class="stats" id="stats"></p>
      <div class="actions">
        <button id="download">下载 SVG</button>
        <button id="copy">复制 SVG 源码</button>
      </div>
    </section>
  </main>
  <script src="static/app.js"></script>
</body>
</html>
```

- [ ] **Step 2: 写 static/style.css**

```css
:root { --ink:#171817; --line:#d9d9d6; --muted:#6b6b68; --bg:#f5f5f3; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--ink);
  font-family:"Inter",system-ui,"Segoe UI",sans-serif; }
.wrap { max-width:920px; margin:0 auto; padding:48px 24px; }
header .num { font-family:"JetBrains Mono",monospace; color:var(--muted); letter-spacing:.2em; }
h1 { margin:.2em 0; font-size:1.7rem; letter-spacing:-.01em; }
.sub { color:var(--muted); margin-top:0; }
.panel { display:grid; grid-template-columns:1fr 1fr; gap:24px; margin-top:24px; }
.drop { border:1px dashed var(--line); border-radius:10px; min-height:180px;
  display:flex; align-items:center; justify-content:center; text-align:center;
  cursor:pointer; background:#fff; transition:border-color .2s; }
.drop.hover { border-color:var(--ink); }
.ops { display:flex; flex-direction:column; gap:12px; }
.ops label { display:flex; align-items:center; gap:8px; font-size:.95rem; }
.ops small { color:var(--muted); }
details summary { cursor:pointer; color:var(--muted); font-size:.85rem; }
details label { margin:8px 0; }
details input[type=number] { width:80px; }
button { font-family:"JetBrains Mono",monospace; text-transform:uppercase;
  letter-spacing:.08em; font-size:.8rem; padding:10px 18px; border:1px solid var(--ink);
  background:var(--ink); color:#fff; border-radius:8px; cursor:pointer; }
button:disabled { opacity:.4; cursor:not-allowed; }
.msg { font-size:.85rem; color:#b00; min-height:1.2em; }
.result { margin-top:36px; }
.previews { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
figure { margin:0; text-align:center; }
figcaption { font-family:"JetBrains Mono",monospace; font-size:.72rem;
  color:var(--muted); margin-bottom:8px; }
.cell { aspect-ratio:1; display:flex; align-items:center; justify-content:center;
  border:1px solid var(--line); border-radius:10px; padding:18%; }
.cell.light { background:#fff; }
.cell.dark { background:#0f0f0e; }
.cell svg, .cell img { width:100%; height:100%; object-fit:contain; }
.cell.dark svg { filter:invert(1); }
.stats { font-family:"JetBrains Mono",monospace; font-size:.78rem; color:var(--muted); margin-top:16px; }
.actions { display:flex; gap:12px; margin-top:12px; }
@media (max-width:680px){ .panel{grid-template-columns:1fr;} .previews{grid-template-columns:1fr;} }
```

- [ ] **Step 3: 写 static/app.js**

```javascript
const $ = (id) => document.getElementById(id);
let currentFile = null;
let currentSvg = "";

const drop = $("drop"), fileInput = $("file");
drop.addEventListener("click", () => fileInput.click());
["dragover", "dragenter"].forEach((e) =>
  drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.add("hover"); }));
["dragleave", "drop"].forEach((e) =>
  drop.addEventListener(e, (ev) => { ev.preventDefault(); drop.classList.remove("hover"); }));
drop.addEventListener("drop", (ev) => { if (ev.dataTransfer.files[0]) setFile(ev.dataTransfer.files[0]); });
fileInput.addEventListener("change", () => { if (fileInput.files[0]) setFile(fileInput.files[0]); });

function setFile(f) {
  currentFile = f;
  $("dropText").innerHTML = `已选:<br/><small>${f.name}</small>`;
  const isSvg = /\.svg$/i.test(f.name) || f.type === "image/svg+xml";
  const trace = $("op-trace");
  trace.disabled = isSvg;
  if (isSvg) trace.checked = false; else trace.checked = true;
  // 原图预览
  const reader = new FileReader();
  reader.onload = () => { $("cellOrig").innerHTML = `<img src="${reader.result}" alt=""/>`; };
  reader.readAsDataURL(f);
}

$("run").addEventListener("click", async () => {
  $("msg").textContent = "";
  if (!currentFile) { $("msg").textContent = "请先上传一张图"; return; }
  const ops = ["op-trace", "op-dewhite", "op-mono"].filter((id) => $(id).checked && !$(id).disabled)
    .map((id) => $(id).value);
  if (ops.length === 0) { $("msg").textContent = "请至少勾选一个操作"; return; }
  const params = {
    threshold: Number($("p-threshold").value),
    padding: Number($("p-padding").value),
    invert: $("p-invert").checked,
  };
  const fd = new FormData();
  fd.append("file", currentFile);
  fd.append("ops", ops.join(","));
  fd.append("params", JSON.stringify(params));
  $("run").disabled = true; $("run").textContent = "处理中…";
  try {
    const resp = await fetch("api/clean", { method: "POST", body: fd });
    const body = await resp.json();
    if (!resp.ok) { $("msg").textContent = body.detail || "处理失败"; return; }
    currentSvg = body.svg;
    $("cellLight").innerHTML = body.svg;
    $("cellDark").innerHTML = body.svg;
    const s = body.stats;
    $("stats").textContent =
      `路径 ${s.pathsKept + s.pathsDropped}→${s.pathsKept} · ` +
      `${(s.bytesIn / 1024).toFixed(1)}KB→${(s.bytesOut / 1024).toFixed(1)}KB · ` +
      `bbox ${s.bbox[0]}×${s.bbox[1]}` + (body.warnings.length ? ` · ⚠ ${body.warnings.join("; ")}` : "");
    $("result").hidden = false;
  } catch (e) {
    $("msg").textContent = "请求出错:" + e.message;
  } finally {
    $("run").disabled = false; $("run").textContent = "净化";
  }
});

$("download").addEventListener("click", () => {
  if (!currentSvg) return;
  const blob = new Blob([currentSvg], { type: "image/svg+xml" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = (currentFile ? currentFile.name.replace(/\.[^.]+$/, "") : "icon") + ".clean.svg";
  a.click();
  URL.revokeObjectURL(a.href);
});

$("copy").addEventListener("click", async () => {
  if (!currentSvg) return;
  await navigator.clipboard.writeText(currentSvg);
  $("copy").textContent = "已复制!";
  setTimeout(() => ($("copy").textContent = "复制 SVG 源码"), 1500);
});
```

- [ ] **Step 4: 手动冒烟(本地直跑后端)**

Run:
```bash
cd "C:/Users/hzs17/Desktop/ai-demos/.claude/worktrees/feat+portfolio-ui-redesign/backends/iconforge_app"
uvicorn main:app --port 8005 &
sleep 2
curl -s -o /dev/null -w "index=%{http_code}\n" http://127.0.0.1:8005/
curl -s -o /dev/null -w "js=%{http_code}\n" http://127.0.0.1:8005/static/app.js
```
Expected: `index=200`、`js=200`(随后 `kill %1` 关掉)

- [ ] **Step 5: 提交**

```bash
cd "C:/Users/hzs17/Desktop/ai-demos/.claude/worktrees/feat+portfolio-ui-redesign"
git add backends/iconforge_app/templates/home.html backends/iconforge_app/static/app.js backends/iconforge_app/static/style.css
git commit -m "feat(iconforge): single-page UI (upload, ops, light/dark preview, download/copy)"
```

---

### Task 8: Dockerfile(含 potrace)+ 容器内自测

**Files:**
- Create: `backends/iconforge_app/Dockerfile`

**Interfaces:**
- Consumes: `requirements.txt`(Task 1)。
- Produces: 监听 8005 的镜像;系统装 `potrace`。

- [ ] **Step 1: 写 Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends potrace \
    && rm -rf /var/lib/apt/lists/*

COPY backends/iconforge_app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backends/iconforge_app/ ./

EXPOSE 8005

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8005"]
```

- [ ] **Step 2: 单独构建镜像验证(Docker Desktop 需已启动)**

Run:
```bash
cd "C:/Users/hzs17/Desktop/ai-demos/.claude/worktrees/feat+portfolio-ui-redesign"
docker build -f backends/iconforge_app/Dockerfile -t iconforge-test .
```
Expected: 构建成功,无报错

- [ ] **Step 3: 跑容器并在容器内确认 potrace + 测试**

Run:
```bash
docker run --rm iconforge-test sh -c "potrace --version && python -m pytest -q"
```
Expected: 打印 potrace 版本;pytest 全绿(此时描摹用例不再 skip)

- [ ] **Step 4: 提交**

```bash
git add backends/iconforge_app/Dockerfile
git commit -m "build(iconforge): Dockerfile with potrace, expose 8005"
```

---

### Task 9: 集成接线(compose + nginx ×2 + 门户作品卡 + 占位图标)

**Files:**
- Modify: `deploy/docker-compose.yml`
- Modify: `deploy/nginx/nginx.conf`
- Modify: `deploy/nginx/nginx.local.conf`
- Modify: `frontends/portfolio/src/data/works.ts`
- Create: `frontends/portfolio/public/icons/iconforge.svg`(占位,Task 10 用 dogfood 产物替换)

**Interfaces:**
- Consumes: `iconforge` 镜像(Task 8)。
- Produces: 路由 `/iconforge/` 反代到 `iconforge:8005`;门户首页第 6 张卡。

- [ ] **Step 1: compose 加 iconforge 服务**

在 `deploy/docker-compose.yml` 的 `md_converter:` 服务块之后、`nginx:` 之前插入:

```yaml
  iconforge:
    build:
      context: ..
      dockerfile: backends/iconforge_app/Dockerfile
    env_file: ../.env
    restart: always
    expose: ["8005"]
```

并把 nginx 的 `depends_on` 改为:

```yaml
    depends_on: [rag, fc, nexus, md_converter, iconforge]
```

- [ ] **Step 2: 生产 nginx.conf 加路由**

在 `deploy/nginx/nginx.conf` 的 `/doctomd/` location 块之后(`}` 之前)插入:

```nginx
    # IconForge 图标净化器
    location /iconforge/ {
        set $ico http://iconforge:8005;
        rewrite ^/iconforge/(.*) /$1 break;
        proxy_pass $ico;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
```

- [ ] **Step 3: 本地 nginx.local.conf 加路由**

在 `deploy/nginx/nginx.local.conf` 的 `/doctomd/` location 块之后插入:

```nginx
    # IconForge 图标净化器
    location /iconforge/ {
        proxy_pass http://iconforge:8005/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
```

- [ ] **Step 4: 门户作品卡(works.ts 末尾追加第 6 项)**

在 `frontends/portfolio/src/data/works.ts` 的 `WORKS` 数组末尾、`doctomd` 项之后追加:

```typescript
  {
    slug: 'iconforge',
    index: '06',
    title: 'IconForge 图标净化器',
    desc: '上传图标自选净化:位图转矢量 / 去除白边 / 彩色转黑色,导出干净单色 SVG。',
    tech: ['FastAPI', 'Pillow', 'potrace', 'SVG'],
    path: '/iconforge',
    icon: '/icons/iconforge.svg',
    changelog: [
      { version: '0.1', date: '2026-06-25', items: ['IconForge 图标净化器上线'] },
    ],
  },
```

- [ ] **Step 5: 占位图标(Task 10 替换)**

```bash
cd "C:/Users/hzs17/Desktop/ai-demos/.claude/worktrees/feat+portfolio-ui-redesign"
cat > frontends/portfolio/public/icons/iconforge.svg <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#171817" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21l6-6"/><path d="M14 4l6 6-9 9H5v-6z"/><path d="M13 5l6 6"/></svg>
SVG
```

- [ ] **Step 6: 提交**

```bash
git add deploy/docker-compose.yml deploy/nginx/nginx.conf deploy/nginx/nginx.local.conf frontends/portfolio/src/data/works.ts frontends/portfolio/public/icons/iconforge.svg
git commit -m "build(iconforge): wire compose service, nginx routes, portfolio work card"
```

---

### Task 10: dogfood 图标 + 本地全栈验证

**Files:**
- Modify: `frontends/portfolio/public/icons/iconforge.svg`(用工具产物替换占位)

**Interfaces:**
- Consumes: 运行中的本地 stack。

- [ ] **Step 1: 从 worktree 启动全栈(关键:必须从 worktree 跑 compose)**

```bash
cd "C:/Users/hzs17/Desktop/ai-demos/.claude/worktrees/feat+portfolio-ui-redesign"
bash deploy/build-frontends.sh
docker compose -f deploy/docker-compose.yml up -d --build
```

- [ ] **Step 2: 验证所有路由 + 新端点**

```bash
for p in / /me /changelog /rag/ /fc/ /nexus/ /doctomd/ /learn/ /iconforge/; do
  printf "%s " "$p"; curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:8080$p"; done
curl -s -o /dev/null -w "clean=%{http_code}\n" -F "file=@frontends/portfolio/public/icons/iconforge.svg;type=image/svg+xml" -F "ops=dewhite,mono" "http://127.0.0.1:8080/iconforge/api/clean"
```
Expected: 所有路径 `200`;`clean=200`

- [ ] **Step 3: dogfood —— 用工具清洗一张图当作 iconforge 卡片图标**

在浏览器打开 `http://127.0.0.1:8080/iconforge/`,上传一张能代表"净化/魔棒"含义的图标(或先用占位的 wand SVG 走一遍 dewhite+mono),下载产物,覆盖 `frontends/portfolio/public/icons/iconforge.svg`。
若暂无合适素材,保留 Task 9 的占位 wand 图标即可(它已是干净单色),本步骤标记完成并在 dev-log 记一句"图标待后续 dogfood 替换"。

- [ ] **Step 4: 重建门户并复验首页图标**

```bash
bash deploy/build-frontends.sh
curl -s -o /dev/null -w "home=%{http_code}\n" "http://127.0.0.1:8080/"
curl -s -o /dev/null -w "icon=%{http_code}\n" "http://127.0.0.1:8080/icons/iconforge.svg"
```
Expected: 均 `200`

- [ ] **Step 5: 提交**

```bash
git add frontends/portfolio/public/icons/iconforge.svg
git commit -m "feat(iconforge): finalize work-card icon (dogfooded via IconForge)"
```

---

### Task 11: 文档更新 + 收尾提交

**Files:**
- Modify: `docs/PROJECT-STATE.md`
- Modify: `docs/dev-log.md`(经 MCP 写,见步骤)

**Interfaces:** 无代码接口;同步文档到当前真实状态。

- [ ] **Step 1: 更新 PROJECT-STATE.md**

在「当前可用路径」表与「待处理/下一步」中加入 `/iconforge/`(IconForge 图标净化器,第 6 个 demo,FastAPI+Pillow+potrace,无状态);在「已定决策」记一句 IconForge 为门户改版分支内交付。把"一句话现状"补上 IconForge。

- [ ] **Step 2: 写开发日志(MCP)**

调用 `mcp__shiyuan-project-manager__update_dev_log`,category `tools`,project `ai-demos`,内容简述:新增 IconForge `/iconforge/` 第 6 个 web demo(三操作自选:位图转矢量/去白边/彩色转黑;SVG 走 svgutil、位图走 Pillow+potrace;无状态;照搬 DocHub 接线);并记录本次门户图标白边裁剪问题的根因与修复。

- [ ] **Step 3: 跑全量后端测试 + 全栈路由复验(回归)**

```bash
cd "C:/Users/hzs17/Desktop/ai-demos/.claude/worktrees/feat+portfolio-ui-redesign/backends/iconforge_app"
python -m pytest -q
cd "C:/Users/hzs17/Desktop/ai-demos/.claude/worktrees/feat+portfolio-ui-redesign"
for p in / /rag/ /fc/ /nexus/ /doctomd/ /learn/ /iconforge/; do printf "%s " "$p"; curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:8080$p"; done
```
Expected: pytest 全绿;所有路由 200

- [ ] **Step 4: 提交**

```bash
git add docs/PROJECT-STATE.md
git commit -m "docs(iconforge): update PROJECT-STATE and dev-log for IconForge demo"
```

---

## Release(计划执行完成、用户确认后进行)

> 这些是对外、不可逆动作,执行前向用户复述确认。

1. **合并 worktree 分支 → master**(线性合并门户改版 + IconForge):
   ```bash
   cd "C:/Users/hzs17/Desktop/ai-demos"
   git checkout master
   git merge --no-ff worktree-feat+portfolio-ui-redesign
   ```
2. **推送 GitHub**:`git push origin master`
3. **部署首尔服务器**(`https://www.shiyuan-wreg.cloud`):SSH 走本地代理 `127.0.0.1:7890`(见 `.claude/ssh_config`);服务器 `cd /opt/ai-demos && git pull`,`bash deploy/build-frontends.sh`,`docker compose -f deploy/docker-compose.yml up -d --build`(注意 potrace 首次构建会拉 apt 包)。
4. **线上验收**:`curl` 全路由含 `/iconforge/` 返回 200,浏览器实测上传净化一张图。
5. 部署完成后清理本地 worktree(`ExitWorktree` 或 `git worktree remove`),更新 PROJECT-STATE 与 memory。

---

## Self-Review

- **Spec coverage:** 三操作(A trace/B dewhite/C mono)→ Task 4/3;自选与 A→B→C 顺序、输入分派 → Task 5;API/数据流 → Task 6;前端亮暗预览+下载复制 → Task 7;错误处理 → Task 5/6(空 ops、超限、potrace 缺失、无路径);测试 → 各任务 TDD;五处接线 → Task 9;dogfood 图标 → Task 10;文档 → Task 11;部署 → Release。覆盖完整。
- **Placeholder scan:** 无 TBD/TODO;每个代码步骤含完整可运行代码。
- **Type consistency:** `clean()` 返回 `{svg, stats{pathsKept,pathsDropped,bbox,bytesIn,bytesOut}, warnings}` 与 `models.CleanResponse/CleanStats` 字段一致;`tracer.trace`/`TraceError`、`cleaner.CleanError`、`svgutil.dewhite/monochrome/bbox` 在调用处签名一致。
- **已知取舍(非阻塞):** 位图分支下 dewhite/mono 由 trace 内在满足(加 warning 说明);svgutil 仅处理自闭合 `<path>` 与 rgb()/hex 填充(覆盖救火场景与 potrace 输出,复杂多元素彩色 SVG 的非 path 元素不在本期)。
