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
