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
