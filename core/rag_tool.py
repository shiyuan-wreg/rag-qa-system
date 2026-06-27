"""
RAG 检索工具
============
将 RAG 检索能力封装为 Agent 可调用的工具 search_docs。
"""

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

from rag.loader import load_documents
from rag.splitter import split_documents
from rag.vectorstore import get_or_create_vectorstore
from rag.retriever import retrieve


def format_retrieved(query: str, docs: list, max_chars: int = 800) -> str:
    """把检索到的片段格式化为带来源、保留原始换行的文本。"""
    parts = [f"用户问题:{query}", "以下是按相关度排序的相关片段:"]
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source") if getattr(doc, "metadata", None) else None
        label = os.path.basename(source) if source else "未知来源"
        content = doc.page_content.strip()
        if len(content) > max_chars:
            content = content[:max_chars] + "…"
        parts.append(f"[{i}] 来源:{label}\n{content}")
    return "\n\n".join(parts)


# RAG 向量检索的 embedding 用 Jina(海外可达)
JINA_API_KEY = os.environ.get("JINA_API_KEY", "")
DOCS_PATH = os.environ.get("DOCS_PATH", "docs/python_guide.txt")
VECTOR_DB_DIR = os.environ.get("VECTOR_DB_DIR", "./chroma_db")


class RAGTool:
    """RAG 检索工具，封装文档加载、切分、建库、检索流程。"""

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
            raw_docs = load_documents(self.docs_path)
            chunks = split_documents(raw_docs)
            self.vectorstore = get_or_create_vectorstore(
                chunks, self.vector_db_dir, api_key=JINA_API_KEY
            )
            print(f"[+] RAG 工具初始化完成: {len(chunks)} 个文本块")
        except Exception as e:
            print(f"[错误] RAG 工具初始化失败: {e}")

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
