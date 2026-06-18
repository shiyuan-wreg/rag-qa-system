"""
Step 2: 文本分块
=============
学习目标：理解为什么需要分块，以及 RecursiveCharacterTextSplitter 是怎么工作的。

原理：
- 为什么分块？
  1. 大模型有上下文长度限制（比如最多处理几千到几万字），如果文档太长，塞不进去。
  2. 向量化的粒度：一整篇文档 embedding 后，向量会"平均化"很多主题，检索时不够精准。
     分成小块后，每个块聚焦一个主题，检索时能更精确地匹配问题。

- RecursiveCharacterTextSplitter 怎么分？
  它按"字符数"切分，但会尽量在语义边界处切断（如段落、句子），而不是硬砍。
  切割优先级：段落 > 句子 > 单词 > 字符
  这意味着它优先找段落边界，找不到就找句子边界，以此类推。

关键参数：
  - chunk_size: 每个块的最大字符数
  - chunk_overlap: 相邻块之间的重叠字符数（保证语义连贯性，不会刚好把关键信息切断）

运行方式：
    venv\Scripts\python.exe step2_split_text.py
"""

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_txt(filepath: str):
    """加载 TXT 文件（复用 Step 1 的代码）"""
    loader = TextLoader(filepath, encoding="utf-8")
    return loader.load()


def split_documents(docs, chunk_size=500, chunk_overlap=50):
    """
    将文档切分成小块

    参数:
        docs: Document 列表
        chunk_size: 每个块最多多少字符（越大保留的上下文越多，但检索精度可能下降）
        chunk_overlap: 相邻块重叠多少字符（建议为 chunk_size 的 10%-20%）

    返回:
        切分后的小 Document 列表
    """
    # 创建分片器
    # separators 指定了优先使用的分隔符，按优先级从高到低：
    #   1. 两个换行（段落边界）
    #   2. 一个换行（行边界）
    #   3. 空格（单词边界）
    #   4. 空字符串（字符边界，兜底）
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
        length_function=len,  # 用 len() 计算长度（按字符数）
    )

    # split_documents() 会把每个 Document 切分成多个小 Document
    # 每个小 Document 的 metadata 会继承原 Document 的 metadata（如 source 路径）
    split_docs = text_splitter.split_documents(docs)

    return split_docs


def show_splits(docs, split_docs):
    """展示分块前后的对比"""
    print(f"原始 Document 数量: {len(docs)}")
    print(f"原始总字符数: {sum(len(d.page_content) for d in docs)}")
    print()
    print(f"切分后 Document 数量: {len(split_docs)}")
    print(f"平均每块字符数: {sum(len(d.page_content) for d in split_docs) // len(split_docs)}")
    print()
    print("=" * 50)
    print("前 3 个分块的内容：")
    print("=" * 50)

    for i, doc in enumerate(split_docs[:3]):
        print(f"\n--- 块 {i + 1} ({len(doc.page_content)} 字符) ---")
        print(doc.page_content[:300])
        if len(doc.page_content) > 300:
            print("...")
        print(f"元数据: {doc.metadata}")


if __name__ == "__main__":
    filepath = "sample_docs/python_guide.txt"

    print("=" * 50)
    print("Step 2: 文本分块")
    print("=" * 50)
    print()

    # Step 1: 加载文档
    docs = load_txt(filepath)

    # Step 2: 分块
    # chunk_size=500: 每个块最多 500 字符
    # chunk_overlap=50: 相邻块重叠 50 字符（避免刚好把一句话切成两半）
    split_docs = split_documents(docs, chunk_size=500, chunk_overlap=50)

    # 展示结果
    show_splits(docs, split_docs)

    print("\n" + "=" * 50)
    print("说明：一篇文章被切成了多个小块，每个块可以独立处理。")
    print("下一步：把这些小块转成向量，存入向量数据库。")
