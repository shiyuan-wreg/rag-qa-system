"""RAG 模块：检索器"""


def retrieve(vectorstore, query: str, k: int = 3, min_quality_score: float = 0.5):
    """从向量数据库中检索相关文档片段。

    默认过滤掉 quality_score 低于 min_quality_score 的 chunk。
    """
    where_filter = {"quality_score": {"$gte": min_quality_score}}
    return vectorstore.similarity_search(query, k=k, filter=where_filter)
