"""RAG enricher 单元测试"""

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.documents import Document

from rag.enricher import enrich_chunks, _find_section


def _doc(content: str, source: str = "test.md", start_index: int = 0) -> Document:
    return Document(
        page_content=content,
        metadata={"source": source, "start_index": start_index},
    )


def test_find_section():
    text = "# 标题一\n内容一\n## 标题二\n内容二\n"
    assert _find_section(text, 5) == "标题一"
    assert _find_section(text, 20) == "标题二"
    print("[OK] Markdown 章节解析正确")


def test_enrich_chunks_metadata():
    with tempfile.TemporaryDirectory() as tmp:
        md_path = os.path.join(tmp, "test.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Python 基础\n\nPython 变量是存储数据的容器。\n")

        chunks = [
            Document(
                page_content="Python 变量是存储数据的容器。",
                metadata={"source": md_path, "start_index": 16},
            )
        ]
        # 关闭 LLM，使用启发式
        enriched = enrich_chunks(chunks, use_llm=False)

        assert len(enriched) == 1
        meta = enriched[0].metadata
        assert meta.get("section") == "Python 基础"
        assert meta.get("doc_type") == "markdown"
        assert "ingest_time" in meta
        assert isinstance(meta.get("keywords"), list)
        assert isinstance(meta.get("entities"), list)
        assert isinstance(meta.get("summary"), str)
        print("[OK] 元数据增强字段完整")


def test_enrich_chunks_heuristic_fallback():
    chunk = _doc("def hello():\n    print('hello')", source="test.py", start_index=0)
    enriched = enrich_chunks([chunk], use_llm=False)
    meta = enriched[0].metadata
    # 非 markdown 文件，section 为未分类
    assert meta.get("section") == "未分类"
    assert meta.get("keywords") != []
    print("[OK] 启发式降级生效")


if __name__ == "__main__":
    test_find_section()
    test_enrich_chunks_metadata()
    test_enrich_chunks_heuristic_fallback()
    print("\nAll enricher tests passed!")
