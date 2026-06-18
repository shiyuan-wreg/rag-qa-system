"""
Step 1: 文档加载
=============
学习目标：理解如何把本地文件（TXT / PDF）读入程序，变成 LangChain 的 Document 对象。

原理：
- LangChain 把每个文档封装成一个 Document 对象，包含两部分：
  - page_content: 文档的文本内容（字符串）
  - metadata: 文档的元信息（如文件名、页码等）
- 为什么要封装？因为后续的分块、向量化等操作，都依赖统一的 Document 接口。

运行方式：
    venv\Scripts\python.exe step1_load_docs.py
"""

from langchain_community.document_loaders import TextLoader


def load_txt(filepath: str):
    """
    加载 TXT 文本文件

    参数:
        filepath: 文件路径

    返回:
        Document 对象列表（虽然只有一个文件，但返回的是列表，为了兼容多文件场景）
    """
    # TextLoader 会自动读取文件内容，用 UTF-8 编码
    # 如果文件编码不是 UTF-8，可以传 encoding 参数，如 TextLoader(filepath, encoding="gbk")
    loader = TextLoader(filepath, encoding="utf-8")

    # load() 方法返回 Document 列表
    # 每个 Document 有两个属性：
    #   - page_content: 文件的全部文本内容
    #   - metadata: {"source": "文件路径"}
    documents = loader.load()

    return documents


def show_documents(docs):
    """打印 Document 的内容，方便观察"""
    print(f"共加载了 {len(docs)} 个 Document\n")

    for i, doc in enumerate(docs):
        print(f"--- Document {i + 1} ---")
        print(f"内容长度: {len(doc.page_content)} 字符")
        print(f"元数据: {doc.metadata}")
        print(f"内容前 200 字:\n{doc.page_content[:200]}...")
        print()


if __name__ == "__main__":
    # 加载示例文档
    filepath = "sample_docs/python_guide.txt"

    print("=" * 50)
    print("Step 1: 文档加载")
    print("=" * 50)

    docs = load_txt(filepath)
    show_documents(docs)

    print("说明：上面的 Document 就是把整篇文档作为一个大块读进来了。")
    print("下一步我们会把它切成更小的块。")
