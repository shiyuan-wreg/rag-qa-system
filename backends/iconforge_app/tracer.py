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
