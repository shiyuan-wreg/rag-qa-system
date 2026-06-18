"""RAG 模块：检索器"""


def retrieve(vectorstore, query: str, k: int = 3):
    """从向量数据库中检索相关文档片段。"""
    return vectorstore.similarity_search(query, k=k)
