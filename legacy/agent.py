"""
Function Calling 智能任务 Agent（完整版）
==========================================
功能：自然语言指令 → Agent 解析 → 调用工具 → 返回结果

支持：
  - 天气查询、数学计算、设置提醒
  - 多轮对话（保存上下文）
  - 单工具 / 多步骤任务
  - 异常处理（工具失败不影响整体）

运行方式：
    venv\Scripts\python.exe agent.py
"""

import json
import os
import traceback

import dashscope
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
dashscope.api_key = API_KEY


# ==================== 工具函数 ====================

def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    mock_db = {
        "北京": "晴天，25°C，空气质量良",
        "上海": "小雨，22°C，记得带伞",
        "广州": "多云，28°C，闷热",
        "深圳": "雷阵雨，26°C，出行注意安全",
        "杭州": "阴天，20°C，凉爽舒适",
    }
    return mock_db.get(city, f"抱歉，暂无{city}的天气数据")


def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"


def set_reminder(content: str, time: str) -> str:
    """设置提醒"""
    return f"已设置提醒: {content}，时间: {time}"


# ==================== 工具路由 ====================

TOOL_MAP = {
    "get_weather": get_weather,
    "calculate": calculate,
    "set_reminder": set_reminder,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息，包括温度、天气状况",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，如北京、上海"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算数学表达式，支持加减乘除、括号",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "数学表达式，如 2+3*4"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "设置提醒事项，在指定时间提醒用户",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "提醒内容"},
                    "time": {"type": "string", "description": "提醒时间，如明天上午9点"}
                },
                "required": ["content", "time"]
            }
        }
    }
]


# ==================== Agent 核心 ====================

class Agent:
    """
    Function Calling Agent

    核心设计：
      - 保存对话历史（messages）
      - 每次用户输入触发一轮对话循环
      - 循环内：模型推理 → 如需调用工具 → 执行 → 结果传回 → 继续推理
      - 支持多步骤任务（一次用户输入可能触发多次工具调用）
    """

    def __init__(self, model: str = "qwen-turbo"):
        self.model = model
        self.messages = []  # 对话历史
        self.max_turns = 5  # 单轮用户输入最多循环 5 次（防止死循环）

        # System Prompt：定义 Agent 角色
        self.system_message = {
            "role": "system",
            "content": (
                "你是一个智能任务助手，可以帮助用户查询天气、进行数学计算、设置提醒。"
                "当你需要获取实时信息或进行精确计算时，必须使用提供的工具。"
                "如果工具调用失败，向用户说明情况，不要编造结果。"
            )
        }

    def chat(self, user_input: str) -> str:
        """
        用户输入 → Agent 处理 → 返回回答

        内部实现：对话循环
        """
        # 把用户输入加入历史
        self.messages.append({"role": "user", "content": user_input})

        # 对话循环
        for turn in range(self.max_turns):
            try:
                # 调用模型
                response = dashscope.Generation.call(
                    model=self.model,
                    messages=[self.system_message] + self.messages,
                    tools=TOOLS,
                    result_format="message",
                )

                choice = response.output.choices[0]
                message = choice.message

                # 判断是否需要调用工具
                if message.get("tool_calls"):
                    # 模型要调用工具
                    self._handle_tool_calls(message)
                    # 继续下一轮循环（把工具结果给模型，让它继续推理）
                    continue
                else:
                    # 模型直接回答，循环结束
                    answer = message.content
                    self.messages.append({"role": "assistant", "content": answer})
                    return answer

            except Exception as e:
                error_msg = f"Agent 出错: {str(e)}"
                print(f"[错误] {error_msg}")
                print(traceback.format_exc())
                return error_msg

        # 超过最大循环次数
        return "处理时间过长，请简化您的问题后重试。"

    def _handle_tool_calls(self, message):
        """
        处理模型返回的 tool_calls

        步骤：
          1. 把模型的 tool_calls 加入对话历史
          2. 逐个执行工具
          3. 把每个工具的返回结果加入对话历史
        """
        # 把 tool_calls 加入 messages
        self.messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["function"]["name"],
                        "arguments": tc["function"]["arguments"],
                    }
                }
                for tc in message.tool_calls
            ]
        })

        # 逐个执行工具
        for tool_call in message.tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])

            print(f"  [工具] {tool_name}({json.dumps(tool_args, ensure_ascii=False)})")

            # 异常处理：单个工具失败不影响其他工具
            try:
                if tool_name in TOOL_MAP:
                    result = TOOL_MAP[tool_name](**tool_args)
                else:
                    result = f"错误: 未知工具 '{tool_name}'"
            except Exception as e:
                result = f"工具执行失败: {e}"
                print(f"  [工具错误] {result}")

            print(f"  [工具返回] {result}")

            # 把工具结果加入 messages
            self.messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tool_call["id"],
            })

    def get_history(self) -> list:
        """获取对话历史（用于调试）"""
        return self.messages

    def clear_history(self):
        """清空对话历史"""
        self.messages = []
        print("[Agent] 对话历史已清空")


# ==================== 主程序 ====================

def main():
    print("=" * 60)
    print("Function Calling 智能任务 Agent")
    print("=" * 60)
    print("\n支持的功能：")
    print("  - 天气查询: 北京今天天气怎么样？")
    print("  - 数学计算: 帮我算 (15 + 27) * 3")
    print("  - 设置提醒: 提醒我明天上午9点开会")
    print("  - 多步骤: 查上海天气，如果下雨提醒我带伞")
    print("\n命令: /clear 清空历史, /history 查看历史, /quit 退出")
    print("=" * 60)

    if not API_KEY:
        print("\n错误: 请先配置 DASHSCOPE_API_KEY")
        return

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
            continue
        elif user_input == "/history":
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
                    print(f"  工具结果: {content}")
            continue

        # 正常对话
        print("Agent: ", end="", flush=True)
        answer = agent.chat(user_input)
        print(answer)


if __name__ == "__main__":
    main()
