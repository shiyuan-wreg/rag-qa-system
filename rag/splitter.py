"""RAG 模块：文本切分"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(docs, chunk_size: int = 500, chunk_overlap: int = 50):
    """将文档切分成小块，并保留每个 chunk 在原文中的起始位置。"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
        add_start_index=True,
    )
    return splitter.split_documents(docs)
