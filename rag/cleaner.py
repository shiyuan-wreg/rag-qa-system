"""RAG 模块：数据清洗

包含：
- 文档级去重（精确）
- chunk 级噪声过滤
- chunk 质量评分
"""

import hashlib
import re
from collections import Counter
from typing import List

from langchain_core.documents import Document


# 被视为“有效字符”的 Unicode 范围：CJK、拉丁字母、数字、常见标点
_MEANINGFUL_CHAR_RE = re.compile(
    r"[一-鿿가-힯぀-ゟ゠-ヿ"
    r"a-zA-Z0-9，。、；：？！\"\"''（）【】《》.,;:?!'\"()\[\]<>]"
)


def _normalize_text(text: str) -> str:
    """用于去重的标准化文本：去除首尾空白、统一换行、转小写。"""
    return re.sub(r"\s+", " ", text.strip().lower())


def _compute_md5(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def deduplicate_documents(docs: List[Document]) -> List[Document]:
    """文档级精确去重。

    对文档内容做标准化后计算 MD5，MD5 相同即视为重复，保留第一个。
    近似去重（SimHash/MinHash）后续可扩展，当前优先保证 O(n) 性能。
    """
    unique = []
    seen_hashes = set()

    for doc in docs:
        normalized = _normalize_text(doc.page_content)
        if not normalized:
            continue

        md5 = _compute_md5(normalized)
        if md5 in seen_hashes:
            continue
        seen_hashes.add(md5)
        unique.append(doc)

    return unique


def compute_info_density(text: str) -> float:
    """计算文本信息密度：有效字符 / 总字符。"""
    if not text:
        return 0.0
    meaningful = len(_MEANINGFUL_CHAR_RE.findall(text))
    total = len(text)
    return meaningful / total if total > 0 else 0.0


def _is_sentence_complete(text: str) -> bool:
    """文本是否以句末标点结尾。"""
    stripped = text.strip()
    if not stripped:
        return False
    return stripped[-1] in "。！？.!?"


def detect_repeated_noise(chunks: List[Document], frequency_threshold: float = 0.3) -> set:
    """检测跨 chunk 重复出现的固定文本（页眉页脚）。

    使用标准化后的精确匹配统计频率，避免 O(n^2) 的相似度计算。
    返回应被标记为噪声的 chunk 索引集合。
    """
    if not chunks or frequency_threshold <= 0:
        return set()

    total = len(chunks)
    normalized = []
    for chunk in chunks:
        text = _normalize_text(chunk.page_content)
        # 只保留长度适中的文本参与频率统计（太短太容易撞）
        normalized.append(text if len(text) >= 10 else "")

    counter = Counter(normalized)
    noisy_indices = {
        i
        for i, text in enumerate(normalized)
        # 排除自身后统计重复次数
        if text and (counter[text] - 1) / total >= frequency_threshold
    }
    return noisy_indices


def clean_chunks(
    chunks: List[Document],
    min_length: int = 30,
    min_info_density: float = 0.4,
    noise_frequency_threshold: float = 0.3,
) -> List[Document]:
    """清洗 chunk：过滤噪声并计算质量分。

    清洗规则：
    - 长度低于 min_length 丢弃。
    - 信息密度低于 min_info_density 丢弃。
    - 在超过 noise_frequency_threshold 比例的 chunk 中重复出现的文本丢弃。

    质量评分：
    - info_density：有效字符比例。
    - completeness：句末标点完整则 1.0，否则 0.6。
    - quality_score = 0.6 * info_density + 0.4 * completeness。
    """
    noisy_indices = detect_repeated_noise(chunks, frequency_threshold=noise_frequency_threshold)

    cleaned = []
    for i, chunk in enumerate(chunks):
        text = chunk.page_content
        stripped = text.strip()

        # 长度过滤
        if len(stripped) < min_length:
            continue

        # 重复噪声过滤
        if i in noisy_indices:
            continue

        # 信息密度过滤
        info_density = compute_info_density(text)
        if info_density < min_info_density:
            continue

        completeness = 1.0 if _is_sentence_complete(stripped) else 0.6
        quality_score = 0.6 * info_density + 0.4 * completeness

        chunk.metadata["info_density"] = round(info_density, 4)
        chunk.metadata["completeness"] = round(completeness, 2)
        chunk.metadata["quality_score"] = round(quality_score, 4)

        cleaned.append(chunk)

    return cleaned
