import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/backends/md_converter_app")

from converter import convert_markdown_file, build_dir_index, convert_directory, build_global_index


def test_convert_markdown_file_creates_html():
    with tempfile.TemporaryDirectory() as tmp:
        md = Path(tmp) / "test.md"
        md.write_text("# Hello\n\nThis is a test.", encoding="utf-8")
        out = Path(tmp) / "test.html"

        convert_markdown_file(md, out, index_link="index.html")

        assert out.exists()
        html = out.read_text(encoding="utf-8")
        assert "<h1 id=" in html
        assert "Hello" in html
        assert "This is a test." in html


def test_build_dir_index_creates_index_html():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "a.html").write_text("a")
        (root / "b.html").write_text("b")

        build_dir_index(root, [root / "a.html", root / "b.html"], root)

        index = root / "index.html"
        assert index.exists()
        html = index.read_text(encoding="utf-8")
        assert "a.html" in html
        assert "b.html" in html


def test_convert_directory_keeps_structure():
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src"
        out = Path(tmp) / "out"
        (src / "sub").mkdir(parents=True)
        (src / "root.md").write_text("# Root", encoding="utf-8")
        (src / "sub" / "nested.md").write_text("# Nested", encoding="utf-8")

        html_files = convert_directory(src, out, "job-1")

        assert (out / "root.html").exists()
        assert (out / "sub" / "nested.html").exists()
        assert len(html_files) == 2


def test_build_global_index_lists_all_jobs():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "uploads" / "job-1").mkdir(parents=True)
        (root / "uploads" / "job-1" / "index.html").write_text("upload job")
        (root / "paths" / "job-2").mkdir(parents=True)
        (root / "paths" / "job-2" / "index.html").write_text("path job")

        build_global_index(root)

        index = root / "index.html"
        assert index.exists()
        html = index.read_text(encoding="utf-8")
        assert "uploads/job-1/index.html" in html
        assert "paths/job-2/index.html" in html
