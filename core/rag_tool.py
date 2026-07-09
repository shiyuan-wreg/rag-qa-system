"""
RAG 检索工具
============
将 RAG 检索能力封装为 Agent 可调用的工具 search_docs。
"""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

from rag.cleaner import clean_chunks, deduplicate_documents
from rag.enricher import enrich_chunks
from rag.loader import load_directory
from rag.retriever import retrieve
from rag.splitter import split_documents
from rag.vectorstore import get_or_create_vectorstore


# RAG 数据工程 pipeline 版本号。升级此版本会触发向量库重建。
RAG_PIPELINE_VERSION = "2026-07-09-v1"


def format_retrieved(query: str, docs: list, max_chars: int = 800) -> str:
    """把检索到的片段格式化为带来源、章节、关键词、质量分的文本。"""
    parts = [f"用户问题:{query}", "以下是按相关度排序的相关片段:"]
    for i, doc in enumerate(docs, 1):
        meta = getattr(doc, "metadata", {}) or {}
        source = meta.get("source")
        label = os.path.basename(source) if source else "未知来源"
        section = meta.get("section") or "未分类"
        keywords = meta.get("keywords", [])
        quality = meta.get("quality_score", "未知")
        content = doc.page_content.strip()
        if len(content) > max_chars:
            content = content[:max_chars] + "…"
        parts.append(
            f"[{i}] 来源:{label} | 章节:{section} | 质量分:{quality}"
            f"{(' | 关键词:' + ', '.join(keywords)) if keywords else ''}\n{content}"
        )
    return "\n\n".join(parts)


# RAG 向量检索的 embedding 用 Jina(海外可达)
JINA_API_KEY = os.environ.get("JINA_API_KEY", "")
DOCS_PATH = os.environ.get("DOCS_PATH", "docs")
VECTOR_DB_DIR = os.environ.get("VECTOR_DB_DIR", "./chroma_db")
RAG_ENRICH_WITH_LLM = os.environ.get("RAG_ENRICH_WITH_LLM", "1") == "1"


class RAGTool:
    """RAG 检索工具，封装文档加载、清洗、元数据增强、切分、建库、检索流程。"""

    def __init__(self, docs_path: str = DOCS_PATH, vector_db_dir: str = VECTOR_DB_DIR):
        self.docs_path = docs_path
        self.vector_db_dir = vector_db_dir
        self.vectorstore = None
        self._init_vectorstore()

    def _init_vectorstore(self):
        """初始化向量数据库。"""
        if not JINA_API_KEY:
            print("[警告] JINA_API_KEY 未配置，RAG 工具不可用")
            return

        if not os.path.exists(self.docs_path):
            print(f"[警告] 文档路径不存在: {self.docs_path}")
            return

        try:
            # 1. 加载目录/文件
            raw_docs = load_directory(self.docs_path)
            print(f"[+] 加载文档: {len(raw_docs)} 个")

            # 2. 文档级去重
            deduped_docs = deduplicate_documents(raw_docs)
            print(f"[+] 去重后: {len(deduped_docs)} 个")

            # 3. 切分
            chunks = split_documents(deduped_docs)
            print(f"[+] 切分后: {len(chunks)} 个 chunk")

            # 4. chunk 级清洗 + 质量评分
            cleaned_chunks = clean_chunks(chunks)
            print(f"[+] 清洗后: {len(cleaned_chunks)} 个 chunk")

            # 5. 元数据增强
            enriched_chunks = enrich_chunks(cleaned_chunks, use_llm=RAG_ENRICH_WITH_LLM)
            print(f"[+] 元数据增强完成")

            # 6. 入库（带 pipeline 版本管理，代码升级自动重建）
            self.vectorstore = get_or_create_vectorstore(
                enriched_chunks,
                self.vector_db_dir,
                api_key=JINA_API_KEY,
                pipeline_version=RAG_PIPELINE_VERSION,
            )
            print(f"[+] RAG 工具初始化完成")
        except Exception as e:
            print(f"[错误] RAG 工具初始化失败: {e}")
            import traceback
            traceback.print_exc()

    def search(self, query: str, top_k: int = 3) -> str:
        """执行检索，返回格式化的文本片段。"""
        if not self.vectorstore:
            return "错误: RAG 知识库未初始化，请检查 API Key 和文档路径"

        try:
            docs = retrieve(self.vectorstore, query, k=top_k)
            if not docs:
                return "未检索到相关文档片段"
            return format_retrieved(query, docs)
        except Exception as e:
            return f"检索错误: {e}"


# 全局 RAG 工具实例（启动时初始化）
_rag_tool: Optional[RAGTool] = None


def init_rag_tool(docs_path: str = DOCS_PATH, vector_db_dir: str = VECTOR_DB_DIR):
    """初始化 RAG 工具，应在应用启动时调用。"""
    global _rag_tool
    _rag_tool = RAGTool(docs_path, vector_db_dir)


def search_docs(query: str) -> str:
    """Agent 可调用的工具函数。"""
    if _rag_tool is None:
        return "错误: RAG 工具未初始化"
    return _rag_tool.search(query)
