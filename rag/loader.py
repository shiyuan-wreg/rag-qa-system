"""RAG 模块：文档加载"""

import os


def load_documents(path: str):
    """加载单个文档（支持 .txt / .md / .pdf）。"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"文档路径不存在: {path}")

    if path.endswith((".txt", ".md")):
        from langchain_community.document_loaders import TextLoader
        loader = TextLoader(path, encoding="utf-8")
    elif path.endswith(".pdf"):
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(path)
    else:
        raise ValueError(f"不支持的文件格式: {path}")

    return loader.load()


def load_directory(path: str):
    """递归加载目录下的 .txt / .md / .pdf 文件。

    返回 LangChain Document 列表，每个 Document 的 metadata.source 为文件路径。
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"文档路径不存在: {path}")

    if os.path.isfile(path):
        return load_documents(path)

    docs = []
    for root, _, files in os.walk(path):
        for filename in sorted(files):
            if filename.endswith((".txt", ".md", ".pdf")):
                file_path = os.path.join(root, filename)
                try:
                    docs.extend(load_documents(file_path))
                except Exception as e:
                    print(f"[警告] 加载文件失败 {file_path}: {e}")
    return docs
