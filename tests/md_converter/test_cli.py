import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/backends/md_converter_app")

import cli


def test_cli_convert_directory():
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src"
        out = Path(tmp) / "out"
        src.mkdir()
        (src / "doc.md").write_text("# Hello", encoding="utf-8")

        cli.convert_paths([src], out, no_index=False)

        assert (out / "src" / "doc.html").exists()
        assert (out / "src" / "index.html").exists()
        assert (out / "index.html").exists()
