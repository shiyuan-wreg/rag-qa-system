"""RAG 模块：向量数据库

embedding 走 Jina 托管 API(api.jina.ai),海外服务器可达、免费额度。
这里手写一个最小的 Embeddings 客户端(实现 Chroma 需要的
embed_documents / embed_query 接口),避免依赖 langchain 的 Jina 集成版本差异。
"""

import os
from typing import List

import requests
from langchain_community.vectorstores import Chroma

JINA_API_URL = "https://api.jina.ai/v1/embeddings"
JINA_MODEL = "jina-embeddings-v3"


class JinaEmbeddings:
    """最小 Jina embedding 客户端,兼容 LangChain Embeddings 接口。"""

    def __init__(self, api_key: str, model: str = JINA_MODEL):
        self.api_key = api_key
        self.model = model

    def _embed(self, texts: List[str], task: str) -> List[List[float]]:
        resp = requests.post(
            JINA_API_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={"model": self.model, "task": task, "input": texts},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()["data"]
        # 按 index 排序,保证顺序与输入一致
        data.sort(key=lambda d: d["index"])
        return [d["embedding"] for d in data]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self._embed(texts, task="retrieval.passage")

    def embed_query(self, text: str) -> List[float]:
        return self._embed([text], task="retrieval.query")[0]


def get_or_create_vectorstore(docs, persist_dir: str, api_key: str):
    """获取或创建向量数据库。api_key 为 Jina embedding key。"""
    embedding = JinaEmbeddings(api_key=api_key)

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
