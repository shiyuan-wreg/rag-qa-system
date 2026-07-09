"""RAG 模块：元数据增强

为每个 chunk 补充：
- section：章节标题（Markdown 从标题解析）
- keywords：关键词
- entities：实体
- summary：一句话摘要
- doc_type：文档类型
- ingest_time：入库时间
"""

import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from typing import List, Optional

from langchain_core.documents import Document


# 简单停用词表（中/英）
_STOPWORDS = set(
    "的 了 和 是 在 我 有 就 不 人 都 一 一个 上 也 很 到 说 要 去 你 会 着 没有 看 好 自己 这 那 有 个 之 与 及 等 可以 我们 他 她 它 但 而 或 如果 因为 所以 被 让 从 向 为 以 于 中 对 将 还 把 能 都 就 都 又 亦 很 非常 已经 正在 曾经 现在 这样 那么 这里 那里 这些 那些".split()
    + "the a an is are was were be been have has had do does did will would could should may might must can need to of in on at by for with about as into through during before after above below between under again further then once here there when where why how all any both each few more most other some such no nor not only own same so than too very just".split()
)

# 简单技术名词/版本号正则
_ENTITY_RE = re.compile(r"([A-Z][a-zA-Z0-9_]*(?:\s+[A-Z][a-zA-Z0-9_]*){0,2})|([a-zA-Z]+\s*\d+(?:\.\d+)*)")


def _doc_type(source: str) -> str:
    """根据文件后缀判断文档类型。"""
    if source.endswith(".md"):
        return "markdown"
    if source.endswith(".pdf"):
        return "pdf"
    if source.endswith(".txt"):
        return "text"
    return "unknown"


def _read_source_text(source: str) -> Optional[str]:
    """从磁盘读取原始文档文本（用于章节解析）。"""
    if not source or not os.path.exists(source):
        return None
    try:
        with open(source, encoding="utf-8") as f:
            return f.read()
    except Exception:
        return None


def _extract_markdown_headings(text: str) -> List[tuple]:
    """解析 Markdown 标题，返回 [(position, level, title), ...]。"""
    headings = []
    for m in re.finditer(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE):
        level = len(m.group(1))
        title = m.group(2).strip()
        headings.append((m.start(), level, title))
    return headings


def _find_section(text: str, start_index: int) -> str:
    """根据 chunk 在原文中的起始位置，找到最近的前置 Markdown 标题。"""
    headings = _extract_markdown_headings(text)
    section = "未分类"
    for pos, _level, title in headings:
        if pos <= start_index:
            section = title
        else:
            break
    return section


def _heuristic_keywords(text: str, top_k: int = 5) -> List[str]:
    """启发式关键词：按词频取前 k 个。"""
    # 简单分词：按非字母数字中文字符切分
    tokens = re.findall(r"[a-zA-Z0-9]+|[一-鿿]", text)
    tokens = [t.lower() for t in tokens if len(t) > 1 and t.lower() not in _STOPWORDS]
    if not tokens:
        return []
    counter = Counter(tokens)
    return [word for word, _ in counter.most_common(top_k)]


def _heuristic_entities(text: str) -> List[str]:
    """启发式实体：正则匹配技术名词和版本号。"""
    entities = []
    for m in _ENTITY_RE.finditer(text):
        entity = (m.group(1) or m.group(2)).strip()
        if entity and len(entity) >= 2:
            entities.append(entity)
    return list(set(entities))[:10]


def _heuristic_summary(text: str) -> str:
    """启发式摘要：取第一句或前 30 字。"""
    text = text.strip().replace("\n", " ")
    if len(text) <= 30:
        return text
    # 尝试取第一句
    for sep in "。.?!?！":
        if sep in text:
            idx = text.find(sep)
            if 5 <= idx <= 60:
                return text[: idx + 1]
    return text[:30] + "…"


def _llm_extract(chunks: List[Document], batch_size: int = 10) -> List[dict]:
    """调用 LLM 批量抽取 keywords / entities / summary。

    返回与 chunks 顺序一致的字典列表。
    """
    try:
        from core.llm import LLMClient
        client = LLMClient.from_config()
    except Exception as e:
        print(f"[警告] LLM 客户端初始化失败，将使用启发式元数据: {e}")
        return []

    results = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        items = []
        for idx, chunk in enumerate(batch):
            items.append({"index": idx, "text": chunk.page_content[:800]})

        prompt = (
            "你是一个知识抽取助手。请对以下每个文本片段提取：\n"
            "- keywords: 3-5 个关键词（技术术语、核心概念）\n"
            "- entities: 重要实体（产品名、技术名、版本号等）\n"
            "- summary: 一句话摘要\n\n"
            f"{json.dumps(items, ensure_ascii=False)}\n\n"
            "请严格返回以下 JSON 格式，不要包含任何其他说明：\n"
            '{"results": [{"keywords": ["..."], "entities": ["..."], "summary": "..."}, ...]}'
        )

        try:
            resp = client.chat(
                messages=[
                    {"role": "system", "content": "你擅长从文本中提取结构化元数据。只输出 JSON。"},
                    {"role": "user", "content": prompt},
                ]
            )
            content = resp.get("content", "")
            # 提取 JSON 块
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                batch_results = data.get("results", [])
                if len(batch_results) == len(batch):
                    results.extend(batch_results)
                    continue
        except Exception as e:
            print(f"[警告] LLM 元数据抽取失败: {e}")

        # 本 batch 失败，用启发式填充
        for chunk in batch:
            results.append({
                "keywords": _heuristic_keywords(chunk.page_content),
                "entities": _heuristic_entities(chunk.page_content),
                "summary": _heuristic_summary(chunk.page_content),
            })

    return results


def enrich_chunks(
    chunks: List[Document],
    use_llm: bool = True,
) -> List[Document]:
    """为每个 chunk 补充元数据。

    流程：
    1. 读取源文件，按 start_index 解析 Markdown 章节。
    2. 补充 doc_type、ingest_time。
    3. 调用 LLM 批量抽取 keywords/entities/summary，失败时自动降级到启发式。
    """
    if not chunks:
        return chunks

    ingest_time = datetime.now(timezone.utc).isoformat()

    # 按源文件缓存原文，避免重复读取
    source_cache = {}

    # 章节解析
    for chunk in chunks:
        source = chunk.metadata.get("source", "")
        chunk.metadata["doc_type"] = _doc_type(source)
        chunk.metadata["ingest_time"] = ingest_time

        if source not in source_cache:
            source_cache[source] = _read_source_text(source)

        original_text = source_cache[source]
        start_index = chunk.metadata.get("start_index")
        if original_text and start_index is not None:
            chunk.metadata["section"] = _find_section(original_text, start_index)
        else:
            chunk.metadata["section"] = "未分类"

    # LLM 抽取
    if use_llm:
        llm_results = _llm_extract(chunks)
    else:
        llm_results = []

    if llm_results and len(llm_results) == len(chunks):
        for chunk, meta in zip(chunks, llm_results):
            chunk.metadata["keywords"] = meta.get("keywords", [])
            chunk.metadata["entities"] = meta.get("entities", [])
            chunk.metadata["summary"] = meta.get("summary", "")
    else:
        for chunk in chunks:
            text = chunk.page_content
            chunk.metadata["keywords"] = _heuristic_keywords(text)
            chunk.metadata["entities"] = _heuristic_entities(text)
            chunk.metadata["summary"] = _heuristic_summary(text)

    return chunks
