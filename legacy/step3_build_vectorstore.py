"""
Step 3: 向量化 + 存入向量数据库
=============================
学习目标：理解什么是 Embedding，为什么用向量数据库，以及 Chroma 怎么用。

原理：
- 什么是 Embedding（向量化）？
  把一段文本转成一串数字（向量）。语义相似的文本，向量也接近。
  比如 "猫" 和 "小猫" 的向量距离很近，"猫" 和 "汽车" 的向量距离很远。
  这样我们就用数学的方式量化了"语义相似度"。

- 什么是向量数据库？
  专门存储和查询向量的一种数据库。
  它能快速找到"与某个向量最接近"的其他向量（近似最近邻搜索）。
  在 RAG 中，我们把每个文本块转成向量存进去。用户提问时，也把问题转成向量，
  然后在库里搜"最相似的文本块向量"，就能找到和问题相关的文档内容。

- 为什么选 Chroma？
  轻量、纯 Python、不需要额外服务，适合小项目和快速验证。
  生产环境可以用 Milvus、Pinecone、Weaviate 等。

运行方式：
    venv\Scripts\python.exe step3_build_vectorstore.py
"""

import os

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量读取 API Key
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")


def load_and_split(filepath: str):
    """加载并切分文档（复用 Step 1 + Step 2）"""
    loader = TextLoader(filepath, encoding="utf-8")
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""],
    )
    return text_splitter.split_documents(docs)


def build_vectorstore(split_docs, persist_dir="./chroma_db"):
    """
    将分块后的文档转成向量，存入 Chroma 数据库

    参数:
        split_docs: 分块后的 Document 列表
        persist_dir: 向量数据库的本地存储目录

    返回:
        Chroma 向量数据库对象
    """
    # DashScopeEmbeddings 调用通义千问的 Embedding API
    # text-embedding-v3 是通义千问的嵌入模型，效果较好且免费额度充足
    embedding = DashScopeEmbeddings(
        model="text-embedding-v3",
        dashscope_api_key=API_KEY,
    )

    print("正在将文本转为向量并存入 Chroma...")
    print(f"共有 {len(split_docs)} 个文本块需要处理")

    # from_documents() 做了三件事：
    # 1. 对每个文本块调用 Embedding API，得到向量
    # 2. 把向量和对应的文本、metadata 存入 Chroma
    # 3. 如果指定了 persist_directory，会把数据持久化到磁盘
    #
    # 注意：第一次运行会调用 Embedding API 产生费用（但免费额度够用）
    vectorstore = Chroma.from_documents(
        documents=split_docs,
        embedding=embedding,
        persist_directory=persist_dir,
    )

    print(f"向量数据库已构建，保存在: {persist_dir}")
    return vectorstore


def inspect_vectorstore(vectorstore):
    """查看向量数据库的基本信息"""
    # Chroma 的 _collection 可以拿到底层集合的信息
    collection = vectorstore._collection
    count = collection.count()
    print(f"\n向量数据库统计:")
    print(f"  存储的向量数量: {count}")
    print(f"  向量维度: 1024 (text-embedding-v3 默认输出 1024 维)")
    print(f"  存储路径: ./chroma_db")


if __name__ == "__main__":
    filepath = "sample_docs/python_guide.txt"

    print("=" * 50)
    print("Step 3: 向量化 + 向量数据库")
    print("=" * 50)
    print()

    if not API_KEY:
        print("错误：请先填写 API_KEY！")
        exit(1)

    os.environ["DASHSCOPE_API_KEY"] = API_KEY

    # 1. 加载并分块
    print("1. 加载并分块文档...")
    split_docs = load_and_split(filepath)
    print(f"   得到 {len(split_docs)} 个文本块\n")

    # 2. 构建向量数据库
    print("2. 构建向量数据库...")
    vectorstore = build_vectorstore(split_docs)
    print()

    # 3. 查看信息
    inspect_vectorstore(vectorstore)

    print("\n" + "=" * 50)
    print("说明：每个文本块都被转成了一个 1024 维的向量，存入 Chroma。")
    print("下一步：用这个向量库做检索，看看能不能找到相关内容。")
