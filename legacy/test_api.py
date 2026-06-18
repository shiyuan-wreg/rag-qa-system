"""
测试脚本：验证通义千问 API 是否可用
运行方式：
    1. 在下方填入你的 API Key（从 https://bailian.console.aliyun.com/ 获取）
    2. 执行：python test_api.py
"""

import os

from dotenv import load_dotenv
from langchain_community.llms import Tongyi

# 加载 .env 文件中的环境变量
load_dotenv()


# ============================================================
# 方式一：直接在代码里填 API Key（简单，但不适合提交到 GitHub）
# ============================================================
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")

# ============================================================
# 方式二（推荐）：从环境变量读取（更安全，适合提交代码）
# 在运行前执行：set DASHSCOPE_API_KEY=你的Key
# ============================================================
# API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")


def test_basic_chat():
    """测试基础对话能力"""
    print("=" * 50)
    print("测试 1：基础对话")
    print("=" * 50)

    if not API_KEY:
        print("错误：请先填写 API_KEY！")
        return False

    os.environ["DASHSCOPE_API_KEY"] = API_KEY

    try:
        llm = Tongyi(model="qwen-turbo")
        response = llm.invoke("你好，请用一句话介绍自己")
        print(f"模型回答：{response}")
        return True
    except Exception as e:
        print(f"调用失败：{e}")
        return False


def test_chinese_qa():
    """测试中文问答能力"""
    print("\n" + "=" * 50)
    print("测试 2：中文问答")
    print("=" * 50)

    try:
        llm = Tongyi(model="qwen-turbo")
        response = llm.invoke("Python 中的列表和元组有什么区别？")
        print(f"模型回答：{response}")
        return True
    except Exception as e:
        print(f"调用失败：{e}")
        return False


def test_streaming():
    """测试流式输出"""
    print("\n" + "=" * 50)
    print("测试 3：流式输出")
    print("=" * 50)

    try:
        llm = Tongyi(model="qwen-turbo", streaming=True)
        print("模型回答：", end="", flush=True)
        for chunk in llm.stream("写一个 Python 打印 Hello World 的代码"):
            print(chunk, end="", flush=True)
        print()
        return True
    except Exception as e:
        print(f"调用失败：{e}")
        return False


if __name__ == "__main__":
    print("通义千问 API 测试脚本")
    print("=" * 50)

    success = test_basic_chat()
    if success:
        test_chinese_qa()
        test_streaming()
        print("\n" + "=" * 50)
        print("所有测试通过！API 可用。")
        print("=" * 50)
    else:
        print("\n测试失败，请检查 API Key 是否正确。")
