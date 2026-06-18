"""
Step 4: 完整 RAG 检索 + 问答
=========================
学习目标：理解 RAG 的完整流程——用户提问 → 检索相关片段 → 拼接 Prompt → 大模型生成答案。

完整流程回顾：
  1. 加载文档 → 2. 切分 → 3. 向量化存入 Chroma → 4. 用户提问
  5. 问题也向量化 → 6. 在 Chroma 里找最相似的文本块
  7. 把找到的文本块 + 问题拼成 Prompt → 8. 调大模型生成答案

运行方式：
    venv\Scripts\python.exe step4_rag_qa.py
"""

import os

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.llms import Tongyi
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量读取 API Key
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")


def build_rag_system(filepath: str, persist_dir="./chroma_db"):
    """
    构建完整的 RAG 系统（1~3 步的整合）

    参数:
        filepath: 文档路径
        persist_dir: 向量库存储目录

    返回:
        构建好的向量数据库对象
    """
    # 如果向量库已经存在，直接加载（避免重复调用 Embedding API）
    embedding = DashScopeEmbeddings(
        model="text-embedding-v3",
        dashscope_api_key=API_KEY,
    )

    if os.path.exists(persist_dir) and os.listdir(persist_dir):
        print("检测到已有向量数据库，直接加载...")
        vectorstore = Chroma(
            persist_directory=persist_dir,
            embedding_function=embedding,
        )
        return vectorstore

    # 否则重新构建
    print("构建新的向量数据库...")

    # Step 1: 加载
    loader = TextLoader(filepath, encoding="utf-8")
    docs = loader.load()

    # Step 2: 切分
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""],
    )
    split_docs = text_splitter.split_documents(docs)
    print(f"文档切分为 {len(split_docs)} 个块")

    # Step 3: 向量化 + 建库
    vectorstore = Chroma.from_documents(
        documents=split_docs,
        embedding=embedding,
        persist_directory=persist_dir,
    )
    print("向量数据库构建完成")
    return vectorstore


def retrieve(vectorstore, query: str, k=3):
    """
    检索：根据用户问题，找出最相关的文本块

    参数:
        vectorstore: Chroma 向量数据库
        query: 用户的问题
        k: 返回最相关的前 k 个块

    返回:
        检索到的 Document 列表
    """
    print(f"\n用户提问: {query}")
    print(f"检索前 {k} 个最相关的文本块...")

    # similarity_search() 内部做了：
    # 1. 把 query 转成向量（调用 Embedding API）
    # 2. 在 Chroma 里找与 query 向量最接近的 k 个向量
    # 3. 返回对应的 Document
    results = vectorstore.similarity_search(query, k=k)

    print(f"检索到 {len(results)} 个相关片段:\n")
    for i, doc in enumerate(results, 1):
        # 打印前 150 字，方便观察
        preview = doc.page_content[:150].replace("\n", " ")
        print(f"  片段{i}: {preview}...")

    return results


def generate_answer(retrieved_docs, query: str):
    """
    生成答案：把检索到的片段拼成 Prompt，调大模型生成回答

    参数:
        retrieved_docs: 检索到的 Document 列表
        query: 用户原始问题

    返回:
        模型生成的答案字符串
    """
    # 把所有检索到的片段拼接成一个字符串
    # 每个片段前面标注来源，方便模型理解
    context = "\n\n".join([
        f"片段 {i+1}:\n{doc.page_content}"
        for i, doc in enumerate(retrieved_docs)
    ])

    # 构造 Prompt
    # system 部分告诉模型"你是谁，该做什么"
    # user 部分包含：上下文（检索结果）+ 用户问题
    # 关键指令："基于上下文回答，不知道就说不知道"——防止模型胡说
    prompt = f"""你是一个专业的知识问答助手。请根据以下提供的参考信息回答用户的问题。
如果参考信息中没有相关内容，请明确说明"根据提供的资料无法回答"。
不要编造信息。

参考信息：
{context}

用户问题：{query}

请基于参考信息给出准确、简洁的回答："""

    print("\n正在调用大模型生成答案...")

    llm = Tongyi(model="qwen-turbo")
    answer = llm.invoke(prompt)

    return answer


def ask(vectorstore, query: str):
    """
    一站式问答：检索 + 生成答案

    这是 RAG 的核心接口，面试时要能讲清楚这一步的流程。
    """
    print("=" * 60)

    # 1. 检索
    docs = retrieve(vectorstore, query, k=3)

    # 2. 生成
    answer = generate_answer(docs, query)

    print(f"\n回答: {answer}")
    print("=" * 60)
    return answer


if __name__ == "__main__":
    filepath = "sample_docs/python_guide.txt"

    print("=" * 60)
    print("Step 4: 完整 RAG 检索 + 问答")
    print("=" * 60)

    if not API_KEY:
        print("错误：请先填写 API_KEY！")
        exit(1)

    os.environ["DASHSCOPE_API_KEY"] = API_KEY

    # 构建 RAG 系统（首次运行会构建向量库，后续直接加载）
    vectorstore = build_rag_system(filepath)
    print()

    # 测试几个问题
    questions = [
        "Python 中的列表和元组有什么区别？",
        "什么是列表推导式？",
        "Python 怎么进行异常处理？",
    ]

    for q in questions:
        ask(vectorstore, q)
        print()

    # 交互模式：你可以输入自己的问题
    print("\n你可以输入自己的问题（输入 'quit' 退出）：")
    while True:
        user_q = input("> ").strip()
        if user_q.lower() in ("quit", "exit", "q"):
            break
        if user_q:
            ask(vectorstore, user_q)
            print()
