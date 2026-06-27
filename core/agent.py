"""
Agent 核心
=========
实现基于 Function Calling 的多轮对话 Agent。
"""

import json
import os
import traceback
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv()

from core.config import Config
from core.llm import LLMClient
from core.tools import TOOL_MAP, TOOLS

API_KEY = Config.LLM_API_KEY


class Agent:
    """
    基于 Function Calling 的任务 Agent。

    核心能力：
      - 多轮对话上下文管理
      - 自动判断是否需要调用工具
      - 支持多步骤任务（一次用户输入可能触发多次工具调用）
      - 工具调用失败不影响整体流程
      - 最大循环次数保护，防止死循环
    """

    def __init__(self, model: str = "qwen-turbo"):
        self.model = model
        self.llm = LLMClient.from_config()
        self.messages: List[Dict[str, Any]] = []
        self.max_turns = 5
        self.system_message = {
            "role": "system",
            "content": (
                "你是一位耐心、专业的技术文档讲师。请按以下规则回答:\n"
                "1. 先给出直接答案或核心结论;\n"
                "2. 再分 2-4 点详细解释,每点说明「是什么」和「为什么」;\n"
                "3. 如果可能,给出一个具体例子或代码片段;\n"
                "4. 如果用到文档内容,在答案中用 [1]、[2] 标注引用对应检索片段;\n"
                "5. 如果检索结果不足以回答,明确说明「根据现有资料无法确定」,不要编造;\n"
                "6. 用 Markdown 组织回答(标题、列表、代码块、表格),前端会渲染成富文本。\n"
                "当问题涉及文档内容时,必须先用 search_docs 检索,再基于检索结果回答。\n"
                "execute_python 只是一个算术计算器(只能算 2+3*4 这种表达式),仅在需要精确数字计算时才用;"
                "不要用它写示例代码、定义函数或演示——这类需求直接用文字说明即可。\n"
                "查看文件内容或目录结构时,使用 read_file 或 list_files 工具。\n"
                "如果工具调用失败,向用户说明情况或直接作答,不要反复重试同一个工具。"
            )
        }

    def chat(self, user_input: str) -> Dict[str, Any]:
        """
        处理用户输入并返回 Agent 回答。

        返回：
            {
                "answer": str,
                "tool_calls": List[Dict],
                "error": bool
            }
        """
        self.messages.append({"role": "user", "content": user_input})
        tool_calls_log: List[Dict[str, Any]] = []

        for turn in range(self.max_turns):
            try:
                message = self.llm.chat(
                    [self.system_message] + self.messages,
                    tools=TOOLS,
                )

                if message.get("tool_calls"):
                    # 记录工具调用日志
                    for tc in message["tool_calls"]:
                        tool_calls_log.append({
                            "name": tc["function"]["name"],
                            "arguments": json.loads(tc["function"]["arguments"]),
                            "result": None,
                        })

                    # 处理工具调用
                    self._handle_tool_calls(message)
                    continue
                else:
                    answer = message["content"]
                    self.messages.append({"role": "assistant", "content": answer})
                    return {
                        "answer": answer,
                        "tool_calls": tool_calls_log,
                        "error": False,
                    }

            except Exception as e:
                error_msg = f"Agent 出错: {str(e)}"
                print(f"[错误] {error_msg}")
                print(traceback.format_exc())
                return {
                    "answer": error_msg,
                    "tool_calls": tool_calls_log,
                    "error": True,
                }

        return {
            "answer": "处理时间过长，请简化您的问题后重试。",
            "tool_calls": tool_calls_log,
            "error": False,
        }

    def _handle_tool_calls(self, message: Dict[str, Any]):
        """处理模型返回的 tool_calls。"""
        # 把模型的 tool_calls 加入对话历史
        self.messages.append({
            "role": "assistant",
            "content": message.get("content", ""),
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["function"]["name"],
                        "arguments": tc["function"]["arguments"],
                    }
                }
                for tc in message["tool_calls"]
            ]
        })

        # 逐个执行工具
        for tool_call in message["tool_calls"]:
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])

            print(f"  [工具] {tool_name}({json.dumps(tool_args, ensure_ascii=False)})")

            try:
                if tool_name in TOOL_MAP:
                    result = TOOL_MAP[tool_name](**tool_args)
                else:
                    result = f"错误: 未知工具 '{tool_name}'"
            except Exception as e:
                result = f"工具执行失败: {e}"
                print(f"  [工具错误] {result}")

            print(f"  [工具返回] {result[:200]}{'...' if len(result) > 200 else ''}")

            # 把工具结果加入对话历史
            self.messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tool_call["id"],
            })

    def get_history(self) -> List[Dict[str, Any]]:
        """获取对话历史（用于调试）。"""
        return self.messages

    def clear_history(self):
        """清空对话历史。"""
        self.messages = []


def create_agent() -> Agent:
    """创建并返回一个 Agent 实例。"""
    if not API_KEY:
        raise ValueError("DASHSCOPE_API_KEY 未配置，请检查 .env 文件")
    return Agent()
