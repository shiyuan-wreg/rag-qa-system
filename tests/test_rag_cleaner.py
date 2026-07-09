"""RAG cleaner 单元测试"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.documents import Document

from rag.cleaner import (
    clean_chunks,
    compute_info_density,
    deduplicate_documents,
)


def _doc(content: str, source: str = "a.md") -> Document:
    return Document(page_content=content, metadata={"source": source})


def test_deduplicate_exact_duplicates():
    docs = [
        _doc("Python 变量定义"),
        _doc("Python 函数定义"),
        _doc("Python 变量定义"),  # 重复
    ]
    result = deduplicate_documents(docs)
    assert len(result) == 2
    print("[OK] 精确去重生效")


def test_deduplicate_near_duplicates():
    docs = [
        _doc("Python 变量定义"),
        _doc("Python 变量定义。"),  # 仅多一个句号，相似度 > 0.85
    ]
    result = deduplicate_documents(docs)
    assert len(result) == 1
    print("[OK] 近似去重生效")


def test_clean_chunks_filters_short_and_low_density():
    chunks = [
        _doc("这是一个完整的 Python 函数定义示例，信息密度足够高。"),
        _doc("第 3 页"),  # 太短
        _doc("!!!!!!!"),  # 信息密度太低
        _doc("页眉：Kairos 文档"),  # 正常长度但信息密度可能低
    ]
    cleaned = clean_chunks(chunks)
    assert len(cleaned) >= 1
    assert all(len(c.page_content.strip()) >= 30 for c in cleaned)
    assert all(c.metadata.get("quality_score", 0) >= 0 for c in cleaned)
    print(f"[OK] 噪声过滤生效，清洗后剩余 {len(cleaned)} 个 chunk")


def test_clean_chunks_scores_metadata():
    chunks = [_doc("Python 变量是用于在程序运行期间存储数据的容器，可以通过赋值语句创建。")]
    cleaned = clean_chunks(chunks)
    assert len(cleaned) == 1
    meta = cleaned[0].metadata
    assert "info_density" in meta
    assert "completeness" in meta
    assert "quality_score" in meta
    assert 0 <= meta["quality_score"] <= 1
    print("[OK] 质量分元数据写入正确")


def test_compute_info_density():
    assert compute_info_density("Python 变量") > 0.5
    assert compute_info_density("☆★☆★☆★☆") < 0.3
    print("[OK] 信息密度计算正确")


if __name__ == "__main__":
    test_deduplicate_exact_duplicates()
    test_deduplicate_near_duplicates()
    test_clean_chunks_filters_short_and_low_density()
    test_clean_chunks_scores_metadata()
    test_compute_info_density()
    print("\nAll cleaner tests passed!")
