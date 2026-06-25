"""编排层:按勾选的 ops(强制 A→B→C 顺序)对输入施加净化操作。"""
import svgutil
import tracer
from config import Config


class CleanError(Exception):
    pass


def _looks_like_svg(file_bytes: bytes, filename: str) -> bool:
    if filename.lower().endswith(".svg"):
        return True
    stripped = file_bytes.lstrip()
    if stripped.startswith(b"\xef\xbb\xbf"):
        stripped = stripped[3:]
    head = stripped.lstrip()[:5].lower()
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
