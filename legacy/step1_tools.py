"""
Step 1: 工具定义
=============
学习目标：理解 Function Calling 中的"工具"是什么，怎么定义，为什么要用 JSON Schema。

核心概念：
- 工具（Tool）= 一个可以被大模型调用的函数
- 大模型不知道函数怎么实现，它只知道函数的"说明书"（JSON Schema）
- 模型根据说明书判断"这个函数能解决用户的问题吗？该传什么参数？"

运行方式：
    venv\Scripts\python.exe step1_tools.py
"""

import json


# ============================================================
# 工具函数的实际实现（Python 函数）
# ============================================================

def get_weather(city: str) -> str:
    """
    获取指定城市的天气信息

    参数:
        city: 城市名，如"北京"、"上海"

    返回:
        天气描述字符串
    """
    # 实际项目中这里会调用真实天气 API（如和风天气、OpenWeatherMap）
    # 为了演示，先用 mock 数据
    mock_db = {
        "北京": "晴天，25°C，空气质量良",
        "上海": "小雨，22°C，记得带伞",
        "广州": "多云，28°C，闷热",
        "深圳": "雷阵雨，26°C，出行注意安全",
    }
    return mock_db.get(city, f"抱歉，暂无{city}的天气数据")


def calculate(expression: str) -> str:
    """
    计算数学表达式

    参数:
        expression: 数学表达式，如 "2 + 3 * 4"、"sqrt(16)"

    返回:
        计算结果字符串
    """
    try:
        # eval 有安全风险，实际项目要用 ast.literal_eval 或专门的安全计算库
        # 这里为了演示简单使用 eval（只接受数字和运算符）
        result = eval(expression, {"__builtins__": {}}, {})
        return str(result)
    except Exception as e:
        return f"计算错误: {e}"


def set_reminder(content: str, time: str) -> str:
    """
    设置提醒

    参数:
        content: 提醒内容，如"开会"
        time: 提醒时间，如"明天上午9点"

    返回:
        设置结果
    """
    # 实际项目中这里会写入数据库或调用系统日历 API
    return f"已设置提醒: {content}，时间: {time}"


def send_email(to: str, subject: str, body: str) -> str:
    """
    发送邮件

    参数:
        to: 收件人邮箱
        subject: 邮件主题
        body: 邮件正文

    返回:
        发送结果
    """
    # 实际项目中这里会调用 SMTP 服务器
    return f"邮件已发送至 {to}，主题: {subject}"


# ============================================================
# 工具的 JSON Schema 定义（给大模型看的"说明书"）
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "获取指定城市的天气信息，包括温度、天气状况等",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "城市名称，如北京、上海、广州"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算数学表达式，支持加减乘除、括号等",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "数学表达式，如 2+3*4、sqrt(16)"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_reminder",
            "description": "设置一个提醒事项，在指定时间提醒用户",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "提醒内容，如开会、拿快递"
                    },
                    "time": {
                        "type": "string",
                        "description": "提醒时间，如明天上午9点、30分钟后"
                    }
                },
                "required": ["content", "time"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "发送电子邮件给指定收件人",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "收件人邮箱地址"
                    },
                    "subject": {
                        "type": "string",
                        "description": "邮件主题"
                    },
                    "body": {
                        "type": "string",
                        "description": "邮件正文内容"
                    }
                },
                "required": ["to", "subject", "body"]
            }
        }
    }
]


# ============================================================
# 工具路由表：根据函数名找到对应的 Python 函数
# ============================================================

TOOL_MAP = {
    "get_weather": get_weather,
    "calculate": calculate,
    "set_reminder": set_reminder,
    "send_email": send_email,
}


def execute_tool(name: str, arguments: dict) -> str:
    """
    根据函数名和参数，执行对应的工具函数

    参数:
        name: 函数名，如 "get_weather"
        arguments: 参数字典，如 {"city": "北京"}

    返回:
        函数执行结果的字符串
    """
    if name not in TOOL_MAP:
        return f"错误: 未知的工具 '{name}'"

    tool_func = TOOL_MAP[name]
    try:
        result = tool_func(**arguments)
        return result
    except Exception as e:
        return f"工具执行错误: {e}"


# ============================================================
# 演示
# ============================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Step 1: 工具定义")
    print("=" * 50)

    print("\n【工具列表】")
    for tool in TOOLS:
        func = tool["function"]
        print(f"  - {func['name']}: {func['description']}")
        params = list(func["parameters"]["properties"].keys())
        print(f"    参数: {', '.join(params)}")

    print("\n【工具执行测试】")
    print(f"  get_weather(北京) -> {execute_tool('get_weather', {'city': '北京'})}")
    print(f"  calculate(2+3*4) -> {execute_tool('calculate', {'expression': '2+3*4'})}")
    print(f"  set_reminder(开会, 明天9点) -> {execute_tool('set_reminder', {'content': '开会', 'time': '明天9点'})}")

    print("\n【JSON Schema 示例】")
    print("这是给大模型看的'说明书'，告诉它每个工具能做什么、需要什么参数:")
    print(json.dumps(TOOLS[0], indent=2, ensure_ascii=False))

    print("\n" + "=" * 50)
    print("说明：")
    print("  1. 上面的 Python 函数是工具的实际实现（程序执行）")
    print("  2. JSON Schema 是工具的'说明书'（给大模型看的）")
    print("  3. 大模型根据说明书判断该调用哪个工具、传什么参数")
    print("  4. TOOL_MAP 是路由表，把函数名映射到实际函数")
    print("=" * 50)
