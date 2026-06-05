"""
Function Calling Agent - FastAPI 版
====================================
接口:
    POST /chat       - 发送消息，返回 Agent 回答
    GET  /           - 前端页面

运行方式:
    venv\Scripts\python.exe -m uvicorn agent_app:app --reload --port 8001

然后浏览器打开: http://127.0.0.1:8001
"""

import json
import os
import traceback

import dashscope
from dotenv import load_dotenv
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

load_dotenv()
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
dashscope.api_key = API_KEY

app = FastAPI(title="Function Calling Agent")


# ==================== 工具函数 ====================

def get_weather(city: str) -> str:
    mock_db = {
        "北京": "晴天，25°C，空气质量良",
        "上海": "小雨，22°C，记得带伞",
        "广州": "多云，28°C，闷热",
        "深圳": "雷阵雨，26°C，出行注意安全",
        "杭州": "阴天，20°C，凉爽舒适",
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
                    "time": {"type": "string", "description": "提醒时间，如明天上午9点"}
                },
                "required": ["content", "time"]
            }
        }
    }
]


# ==================== Agent 核心 ====================

class Agent:
    def __init__(self, model: str = "qwen-turbo"):
        self.model = model
        self.messages = []
        self.max_turns = 5
        self.system_message = {
            "role": "system",
            "content": (
                "你是一个智能任务助手，可以帮助用户查询天气、进行数学计算、设置提醒。"
                "当你需要获取实时信息或进行精确计算时，必须使用提供的工具。"
                "如果工具调用失败，向用户说明情况，不要编造结果。"
            )
        }

    def chat(self, user_input: str) -> dict:
        """返回包含回答和工具调用记录的字典"""
        self.messages.append({"role": "user", "content": user_input})
        tool_calls_log = []

        for turn in range(self.max_turns):
            try:
                response = dashscope.Generation.call(
                    model=self.model,
                    messages=[self.system_message] + self.messages,
                    tools=TOOLS,
                    result_format="message",
                )

                choice = response.output.choices[0]
                message = choice.message

                if message.get("tool_calls"):
                    # 记录工具调用
                    for tc in message.tool_calls:
                        tool_calls_log.append({
                            "name": tc["function"]["name"],
                            "arguments": json.loads(tc["function"]["arguments"]),
                        })

                    # 处理工具调用
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

                    for tool_call in message.tool_calls:
                        tool_name = tool_call["function"]["name"]
                        tool_args = json.loads(tool_call["function"]["arguments"])

                        try:
                            if tool_name in TOOL_MAP:
                                result = TOOL_MAP[tool_name](**tool_args)
                            else:
                                result = f"错误: 未知工具 '{tool_name}'"
                        except Exception as e:
                            result = f"工具执行失败: {e}"

                        self.messages.append({
                            "role": "tool",
                            "content": result,
                            "tool_call_id": tool_call["id"],
                        })

                    continue
                else:
                    answer = message.content
                    self.messages.append({"role": "assistant", "content": answer})
                    return {
                        "answer": answer,
                        "tool_calls": tool_calls_log,
                    }

            except Exception as e:
                return {
                    "answer": f"Agent 出错: {str(e)}",
                    "tool_calls": tool_calls_log,
                    "error": True,
                }

        return {
            "answer": "处理时间过长，请简化您的问题后重试。",
            "tool_calls": tool_calls_log,
        }


# 全局 Agent 实例（每个用户会话应该独立，这里简化为单用户）
agent = Agent()


# ==================== API 接口 ====================

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=AGENT_HTML)


@app.post("/chat")
def chat(query: str = Form(...)):
    """
    问答接口

    curl 测试:
        curl -X POST "http://127.0.0.1:8001/chat" \
             -d "query=北京今天天气怎么样"
    """
    if not API_KEY:
        return {"error": "API Key 未配置"}

    result = agent.chat(query)
    return result


@app.post("/clear")
def clear():
    """清空对话历史"""
    agent.messages = []
    return {"message": "对话历史已清空"}


# ==================== 前端页面 ====================

AGENT_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Function Calling Agent</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 700px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 20px;
        }
        .header h1 { font-size: 24px; margin-bottom: 8px; }
        .header p { font-size: 14px; opacity: 0.9; }
        .chat-container {
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            display: flex;
            flex-direction: column;
            height: calc(100vh - 140px);
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .msg {
            max-width: 80%;
            padding: 10px 14px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.6;
        }
        .msg.user {
            align-self: flex-end;
            background: #11998e;
            color: white;
        }
        .msg.assistant {
            align-self: flex-start;
            background: #f5f5f5;
            color: #333;
        }
        .msg .tools {
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid #e0e0e0;
            font-size: 12px;
            color: #888;
        }
        .msg .tool-item {
            margin-top: 4px;
            padding: 4px 8px;
            background: white;
            border-radius: 4px;
        }
        .input-area {
            padding: 15px 20px;
            border-top: 1px solid #f0f0f0;
            display: flex;
            gap: 10px;
        }
        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            font-size: 14px;
            outline: none;
        }
        .input-area input:focus { border-color: #11998e; }
        .input-area button {
            padding: 12px 20px;
            background: #11998e;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
        }
        .input-area button:disabled { background: #ccc; }
        .toolbar {
            padding: 10px 20px;
            border-bottom: 1px solid #f0f0f0;
            display: flex;
            gap: 10px;
        }
        .toolbar button {
            padding: 6px 12px;
            border: 1px solid #e0e0e0;
            background: white;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
        }
        .toolbar button:hover { background: #f5f5f5; }
        .loading {
            color: #888;
            font-style: italic;
        }
        .welcome {
            text-align: center;
            padding: 40px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Function Calling Agent</h1>
            <p>支持天气查询、数学计算、设置提醒</p>
        </div>
        <div class="chat-container">
            <div class="toolbar">
                <button onclick="clearHistory()">清空对话</button>
            </div>
            <div class="messages" id="messages">
                <div class="welcome">
                    <div style="font-size:40px;margin-bottom:10px;">&#129302;</div>
                    <p>输入消息开始对话<br>例如：北京今天天气怎么样？</p>
                </div>
            </div>
            <div class="input-area">
                <input type="text" id="input" placeholder="输入消息...">
                <button id="sendBtn" onclick="send()">发送</button>
            </div>
        </div>
    </div>

    <script>
        const messages = document.getElementById('messages');
        const input = document.getElementById('input');
        const sendBtn = document.getElementById('sendBtn');

        function addMsg(content, type, tools) {
            const div = document.createElement('div');
            div.className = 'msg ' + type;
            let html = escapeHtml(content);
            if (tools && tools.length) {
                html += '<div class="tools">调用了工具:';
                tools.forEach(t => {
                    html += `<div class="tool-item">${t.name}(${JSON.stringify(t.arguments)})</div>`;
                });
                html += '</div>';
            }
            div.innerHTML = html;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        async function send() {
            const text = input.value.trim();
            if (!text) return;

            addMsg(text, 'user');
            input.value = '';
            sendBtn.disabled = true;

            const loading = document.createElement('div');
            loading.className = 'msg assistant loading';
            loading.textContent = '思考中...';
            messages.appendChild(loading);

            try {
                const form = new FormData();
                form.append('query', text);
                const res = await fetch('/chat', { method: 'POST', body: form });
                const data = await res.json();

                loading.remove();

                if (data.error) {
                    addMsg('错误: ' + data.error, 'assistant');
                } else {
                    addMsg(data.answer, 'assistant', data.tool_calls);
                }
            } catch (e) {
                loading.remove();
                addMsg('请求失败: ' + e.message, 'assistant');
            } finally {
                sendBtn.disabled = false;
            }
        }

        async function clearHistory() {
            await fetch('/clear', { method: 'POST' });
            messages.innerHTML = `
                <div class="welcome">
                    <div style="font-size:40px;margin-bottom:10px;">&#129302;</div>
                    <p>对话已清空<br>输入消息开始新对话</p>
                </div>
            `;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') send();
        });
    </script>
</body>
</html>
"""


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
