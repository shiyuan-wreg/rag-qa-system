"""
RAG 智能文档问答系统（完整版）
==============================
功能：加载本地文档 → 切分 → 向量化 → 存储 → 问答

使用方法：
    1. 将文档放入 sample_docs/ 目录（支持 .txt 和 .pdf）
    2. 在下方填入 API_KEY
    3. 运行: venv\Scripts\python.exe rag.py

项目结构（RAG 流水线）：
    Document Loader → Text Splitter → Embedding → Vector Store → Retriever → LLM
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

# ==================== 配置区域 ====================
DOCS_PATH = "sample_docs/python_guide.txt"  # 文档路径
VECTOR_DB_DIR = "./chroma_db"               # 向量数据库存储目录
CHUNK_SIZE = 500                            # 每个文本块最大字符数
CHUNK_OVERLAP = 50                          # 块间重叠字符数
TOP_K = 3                                   # 检索时返回最相关的几个片段
MODEL = "qwen-turbo"                        # 通义千问模型
# ==================================================


def load_documents(path: str):
    """加载文档（支持 .txt，可扩展 .pdf）"""
    if path.endswith(".txt"):
        loader = TextLoader(path, encoding="utf-8")
    elif path.endswith(".pdf"):
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(path)
    else:
        raise ValueError(f"不支持的文件格式: {path}")
    return loader.load()


def split_documents(docs):
    """将文档切分成小块"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    return splitter.split_documents(docs)


def get_or_create_vectorstore(docs, persist_dir: str):
    """获取或创建向量数据库"""
    embedding = DashScopeEmbeddings(
        model="text-embedding-v3",
        dashscope_api_key=API_KEY,
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


def answer_question(vectorstore, query: str) -> str:
    """
    RAG 核心：检索 + 生成答案

    流程：
        1. 把问题向量化
        2. 在向量库中检索最相关的文本片段
        3. 将片段 + 问题拼成 Prompt
        4. 调大模型生成回答
    """
    # 1. 检索
    docs = vectorstore.similarity_search(query, k=TOP_K)

    # 2. 拼接上下文
    context = "\n\n".join([
        f"[{i+1}] {d.page_content}"
        for i, d in enumerate(docs)
    ])

    # 3. 构造 Prompt（System + Context + Question）
    prompt = f"""你是一个严谨的知识助手。请根据以下参考资料回答用户问题。
如果资料中没有相关内容，请回答"根据提供的资料无法回答该问题"。
不要编造信息。

参考资料：
{context}

用户问题：{query}

请给出准确、简洁的回答："""

    # 4. 调用大模型
    llm = Tongyi(model=MODEL)
    return llm.invoke(prompt)


def main():
    print("=" * 50)
    print("RAG 智能文档问答系统")
    print("=" * 50)

    if not API_KEY:
        print("请先填写 API_KEY！")
        return

    os.environ["DASHSCOPE_API_KEY"] = API_KEY

    # 1. 加载
    print(f"\n[1/4] 加载文档: {DOCS_PATH}")
    raw_docs = load_documents(DOCS_PATH)
    print(f"      加载完成，共 {len(raw_docs)} 个文件")

    # 2. 切分
    print(f"\n[2/4] 切分文档 (chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    chunks = split_documents(raw_docs)
    print(f"      切分为 {len(chunks)} 个文本块")

    # 3. 向量化
    print(f"\n[3/4] 构建向量数据库")
    vectorstore = get_or_create_vectorstore(chunks, VECTOR_DB_DIR)
    print(f"      向量库就绪")

    # 4. 问答循环
    print(f"\n[4/4] 问答系统就绪！输入问题开始（quit 退出）\n")

    while True:
        query = input("你: ").strip()
        if query.lower() in ("quit", "exit", "q"):
            break
        if not query:
            continue

        print("助手: ", end="", flush=True)
        try:
            answer = answer_question(vectorstore, query)
            print(answer)
        except Exception as e:
            print(f"出错了: {e}")
        print()

    print("\n再见！")


if __name__ == "__main__":
    main()
