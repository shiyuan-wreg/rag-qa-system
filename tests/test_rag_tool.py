"""Unit tests for RAG retrieval formatting"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.rag_tool import format_retrieved


class _Doc:
    def __init__(self, content, source=None, section=None, keywords=None, quality_score=None):
        self.page_content = content
        self.metadata = {}
        if source:
            self.metadata["source"] = source
        if section:
            self.metadata["section"] = section
        if keywords:
            self.metadata["keywords"] = keywords
        if quality_score is not None:
            self.metadata["quality_score"] = quality_score


def test_format_preserves_newlines_and_source():
    docs = [_Doc(
        "def add(a, b):\n    return a + b",
        source="/app/docs/python_guide.txt",
        section="函数",
        keywords=["函数", "def"],
        quality_score=0.92,
    )]
    out = format_retrieved("什么是函数", docs)
    assert "什么是函数" in out                      # 含 query
    assert "python_guide.txt" in out                # 含来源 basename
    assert "/app/docs" not in out                   # 只取 basename
    assert "    return a + b" in out                # 保留换行+缩进
    assert "[1]" in out
    assert "章节:函数" in out
    assert "质量分:0.92" in out
    assert "关键词:函数, def" in out
    print("[OK] format preserves metadata, newlines and source")


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
