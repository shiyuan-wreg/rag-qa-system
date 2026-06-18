"""RAG 模块：文本切分"""

from langchain_text_splitters import RecursiveCharacterTextSplitter


def split_documents(docs, chunk_size: int = 500, chunk_overlap: int = 50):
    """将文档切分成小块。"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(docs)
