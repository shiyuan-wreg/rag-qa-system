"""
智能文档任务 Agent - 命令行版
==============================
运行方式：
    venv/Scripts/python.exe main.py

支持命令：
    /clear  - 清空对话历史
    /history - 查看对话历史
    /eval   - 运行测试用例评估
    /quit   - 退出
"""

import os

from dotenv import load_dotenv

load_dotenv()

from core.agent import Agent
from core.rag_tool import init_rag_tool, search_docs
from core.tools import TOOL_MAP
from eval.evaluator import run_test_cases

API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")


def print_banner():
    print("=" * 60)
    print("基于 RAG + Function Calling 的智能文档任务 Agent")
    print("=" * 60)
    print("\n支持的功能：")
    print("  - 知识库问答: Python 中列表和元组有什么区别？")
    print("  - 代码执行: 帮我算 (15 + 27) * 3")
    print("  - 文件读取: 读取 docs/python_guide.txt 文件")
    print("  - 目录查看: 列出当前目录下的文件")
    print("\n命令: /clear 清空历史, /history 查看历史, /eval 评估, /quit 退出")
    print("=" * 60)


def main():
    print_banner()

    if not API_KEY:
        print("\n错误: 请先配置 DASHSCOPE_API_KEY")
        return

    # 初始化 RAG 工具
    print("\n[+] 正在初始化 RAG 知识库...")
    init_rag_tool()

    # 注册 RAG 工具到工具映射
    TOOL_MAP["search_docs"] = search_docs

    agent = Agent()

    while True:
        try:
            user_input = input("\n你: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n再见！")
            break

        if not user_input:
            continue

        # 特殊命令
        if user_input == "/quit":
            print("再见！")
            break
        elif user_input == "/clear":
            agent.clear_history()
            print("[Agent] 对话历史已清空")
            continue
        elif user_input == "/history":
            print_history(agent)
            continue
        elif user_input == "/eval":
            run_evaluation(agent)
            continue

        # 正常对话
        print("Agent: ", end="", flush=True)
        result = agent.chat(user_input)
        print(result["answer"])

        if result.get("tool_calls"):
            print(f"\n[本次调用工具数: {len(result['tool_calls'])}]")


def print_history(agent):
    """打印对话历史。"""
    print("\n对话历史:")
    for msg in agent.get_history():
        role = msg["role"]
        content = msg.get("content", "")
        if role == "user":
            print(f"  用户: {content}")
        elif role == "assistant":
            if "tool_calls" in msg:
                print(f"  模型(调用工具):")
                for tc in msg["tool_calls"]:
                    print(f"    → {tc['function']['name']}({tc['function']['arguments']})")
            else:
                print(f"  模型: {content}")
        elif role == "tool":
            print(f"  工具结果: {content[:100]}{'...' if len(content) > 100 else ''}")


def run_evaluation(agent):
    """运行测试用例评估。"""
    test_cases = [
        {"query": "Python 中列表和元组有什么区别？"},
        {"query": "帮我算一下 (15 + 27) * 3"},
        {"query": "docs 目录下有什么文件？"},
    ]

    print("\n[+] 开始运行评估...")
    result = run_test_cases(agent.chat, test_cases)

    print(f"\n平均得分: {result['average_score']}")
    for item in result["results"]:
        print(f"\n问题: {item['query']}")
        print(f"回答: {item['answer'][:100]}{'...' if len(item['answer']) > 100 else ''}")
        print(f"得分: {item['scores']}")


if __name__ == "__main__":
    main()
