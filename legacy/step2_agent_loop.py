"""
Step 2: 核心对话循环
=================
学习目标：理解 Function Calling 的完整对话循环，为什么需要循环、每次循环做什么。

核心流程（面试必须能画出来）：

  用户输入
      │
      ▼
  ┌─────────────────┐
  │ 构造 messages   │  ← 包含 system + history + user 消息
  │ 附加 tools 定义  │
  └────────┬────────┘
           │
           ▼
  ┌─────────────────┐
  │ 调大模型         │
  └────────┬────────┘
           │
      ┌────┴────┐
      ▼         ▼
  tool_calls  直接回答
      │         │
      ▼         ▼
  执行工具    输出给用户
      │
      ▼
  工具结果
  加入 messages
      │
      ▼
  再次调大模型  ←───┐
      │             │
      └─────────────┘  (循环直到模型不再调用工具)

运行方式：
    venv\Scripts\python.exe step2_agent_loop.py
"""

import json
import os

import dashscope
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")

# 确保 API Key 已设置
dashscope.api_key = API_KEY


# ==================== 工具定义（复用 Step 1）====================

def get_weather(city: str) -> str:
    mock_db = {
        "北京": "晴天，25°C，空气质量良",
        "上海": "小雨，22°C，记得带伞",
        "广州": "多云，28°C，闷热",
        "深圳": "雷阵雨，26°C，出行注意安全",
    }
    return mock_db.get(city, f"抱歉，暂无{city}的天气数据")


def calculate(expression: str) -> str:
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"


def set_reminder(content: str, time: str) -> str:
    return f"已设置提醒: {content}，时间: {time}"


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
            "description": "获取指定城市的天气信息",
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
            "description": "计算数学表达式",
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
            "description": "设置提醒事项",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "提醒内容"},
                    "time": {"type": "string", "description": "提醒时间"}
                },
                "required": ["content", "time"]
            }
        }
    }
]


# ==================== 核心：对话循环 ====================

def run_agent(user_input: str, messages: list = None) -> tuple:
    """
    Agent 核心对话循环

    参数:
        user_input: 用户的输入
        messages:   历史对话记录（多轮对话时传入）

    返回:
        (最终回答字符串, 更新后的 messages)
    """

    # 1. 初始化 messages（如果没有传入历史）
    if messages is None:
        messages = []

    # System 消息：定义 Agent 的角色和行为边界
    # 这是 Function Calling 中非常关键的一部分！
    # 它告诉模型：你是谁、你有什么工具、该怎么用
    system_msg = {
        "role": "system",
        "content": (
            "你是一个智能任务助手，可以帮助用户查询天气、进行数学计算、设置提醒。"
            "当你需要获取实时信息（如天气）或进行精确计算时，请使用提供的工具。"
            "使用工具后，基于工具返回的结果给用户一个自然、友好的回答。"
        )
    }

    # 把用户输入加入对话历史
    messages.append({"role": "user", "content": user_input})

    # 2. 调用大模型（带 tools 参数）
    print(f"\n[Agent] 用户输入: {user_input}")
    print("[Agent] 正在调用模型推理...")

    response = dashscope.Generation.call(
        model="qwen-turbo",
        messages=[system_msg] + messages,
        tools=TOOLS,
        result_format="message",
    )

    # 3. 处理模型输出
    choice = response.output.choices[0]
    message = choice.message

    # 4. 判断模型是否需要调用工具
    # 关键判断：message.tool_calls 是否存在且不为空
    if message.get("tool_calls"):
        print(f"[Agent] 模型决定调用工具")

        # 把模型的"思考"（tool_calls）加入对话历史
        # 注意：这里的 role 是 "assistant"，但 content 为空（或 tool_calls）
        messages.append({
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

        # 5. 执行所有工具调用
        for tool_call in message.tool_calls:
            tool_name = tool_call["function"]["name"]
            tool_args = json.loads(tool_call["function"]["arguments"])

            print(f"[Agent] 执行工具: {tool_name}({json.dumps(tool_args, ensure_ascii=False)})")

            # 执行工具函数
            if tool_name in TOOL_MAP:
                result = TOOL_MAP[tool_name](**tool_args)
            else:
                result = f"错误: 未知工具 '{tool_name}'"

            print(f"[Agent] 工具返回: {result}")

            # 6. 把工具结果加入对话历史
            # role="tool" 表示这是工具执行的结果
            # tool_call_id 对应之前的 tool_call，让模型知道这是哪个工具的返回值
            messages.append({
                "role": "tool",
                "content": result,
                "tool_call_id": tool_call["id"],
            })

        # 7. 再次调用模型，传入工具结果，让模型生成最终回答
        print("[Agent] 工具执行完毕，再次调用模型生成回答...")
        response = dashscope.Generation.call(
            model="qwen-turbo",
            messages=[system_msg] + messages,
            tools=TOOLS,
            result_format="message",
        )

        final_message = response.output.choices[0].message
        final_answer = final_message.content

        # 把最终回答加入历史
        messages.append({"role": "assistant", "content": final_answer})

        return final_answer, messages

    else:
        # 模型不需要调用工具，直接回答
        final_answer = message.content
        print(f"[Agent] 模型直接回答（未调用工具）")

        messages.append({"role": "assistant", "content": final_answer})
        return final_answer, messages


# ==================== 演示 ====================

if __name__ == "__main__":
    if not API_KEY:
        print("错误：请先配置 DASHSCOPE_API_KEY")
        exit(1)

    print("=" * 60)
    print("Step 2: Function Calling 核心对话循环")
    print("=" * 60)

    # 测试用例 1：单工具调用
    print("\n" + "=" * 60)
    print("测试 1：单工具调用（查天气）")
    print("=" * 60)
    answer, msgs = run_agent("北京今天天气怎么样？")
    print(f"\n最终回答: {answer}")

    # 测试用例 2：多步骤推理
    print("\n" + "=" * 60)
    print("测试 2：多步骤推理（天气 + 提醒）")
    print("=" * 60)
    answer, msgs = run_agent("查一下上海天气，如果下雨就提醒我带伞")
    print(f"\n最终回答: {answer}")

    # 测试用例 3：数学计算
    print("\n" + "=" * 60)
    print("测试 3：数学计算")
    print("=" * 60)
    answer, msgs = run_agent("帮我算一下 (15 + 27) * 3 等于多少")
    print(f"\n最终回答: {answer}")

    # 测试用例 4：不需要工具的直接回答
    print("\n" + "=" * 60)
    print("测试 4：不需要工具（闲聊）")
    print("=" * 60)
    answer, msgs = run_agent("你好，你能做什么？")
    print(f"\n最终回答: {answer}")

    print("\n" + "=" * 60)
    print("完整对话历史（messages）:")
    print("=" * 60)
    for i, msg in enumerate(msgs):
        role = msg["role"]
        content = msg.get("content", "")
        if role == "user":
            print(f"\n  用户: {content}")
        elif role == "assistant":
            if "tool_calls" in msg:
                print(f"  模型(思考): 需要调用工具")
                for tc in msg["tool_calls"]:
                    print(f"    → {tc['function']['name']}({tc['function']['arguments']})")
            else:
                print(f"  模型: {content}")
        elif role == "tool":
            print(f"  工具结果: {content}")

    print("\n" + "=" * 60)
    print("核心理解：")
    print("  1. 每次循环 = 一次模型调用")
    print("  2. 如果模型返回 tool_calls → 执行工具 → 再次调模型（新循环）")
    print("  3. 如果模型直接回答 → 循环结束")
    print("  4. messages 列表不断增长，保存了完整的对话上下文")
    print("=" * 60)
