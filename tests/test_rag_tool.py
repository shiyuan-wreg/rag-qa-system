"""Unit tests for RAG retrieval formatting"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.rag_tool import format_retrieved


class _Doc:
    def __init__(self, content, source=None):
        self.page_content = content
        self.metadata = {"source": source} if source else {}


def test_format_preserves_newlines_and_source():
    docs = [_Doc("def add(a, b):\n    return a + b", source="/app/docs/python_guide.txt")]
    out = format_retrieved("什么是函数", docs)
    assert "什么是函数" in out                      # 含 query
    assert "python_guide.txt" in out                # 含来源 basename(非全路径)
    assert "/app/docs" not in out                   # 只取 basename
    assert "    return a + b" in out                # 保留换行+缩进(未被压成空格)
    assert "[1]" in out
    print("[OK] format preserves newlines and source")


def test_format_truncates_long_chunk():
    docs = [_Doc("x" * 1000, source="a.txt")]
    out = format_retrieved("q", docs, max_chars=800)
    assert "…" in out
    assert "x" * 801 not in out                     # 截断生效
    print("[OK] format truncates long chunk")


def test_format_missing_source_label():
    docs = [_Doc("hello")]
    out = format_retrieved("q", docs)
    assert "未知来源" in out
    print("[OK] format labels missing source")


if __name__ == "__main__":
    test_format_preserves_newlines_and_source()
    test_format_truncates_long_chunk()
    test_format_missing_source_label()
    print("\nAll rag_tool format tests passed!")
