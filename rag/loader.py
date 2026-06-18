"""RAG 模块：文档加载"""

import os


def load_documents(path: str):
    """加载文档（支持 .txt 和 .pdf）。"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"文档路径不存在: {path}")

    if path.endswith(".txt"):
        from langchain_community.document_loaders import TextLoader
        loader = TextLoader(path, encoding="utf-8")
    elif path.endswith(".pdf"):
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(path)
    else:
        raise ValueError(f"不支持的文件格式: {path}")

    return loader.load()
