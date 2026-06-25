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

def test_bom_prefixed_svg_sniffed_as_svg():
    bom_svg = b"\xef\xbb\xbf" + DIRTY_SVG
    # filename not .svg, but BOM-stripped sniff should recognize it
    r = cleaner.clean(bom_svg, "x.bin", ["mono"], {})
    assert r["stats"]["pathsKept"] == 2
