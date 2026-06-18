"""RAG 模块：向量数据库"""

import os

from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma


def get_or_create_vectorstore(docs, persist_dir: str, api_key: str):
    """获取或创建向量数据库。"""
    embedding = DashScopeEmbeddings(
        model="text-embedding-v3",
        dashscope_api_key=api_key,
    )

    # 如果已有数据库，直接加载
    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        print("[+] 加载已有向量数据库")
        return Chroma(
            persist_directory=persist_dir,
            embedding_function=embedding,
        )

    # 否则新建
    print("[+] 构建向量数据库...")
    return Chroma.from_documents(
        documents=docs,
        embedding=embedding,
        persist_directory=persist_dir,
    )
