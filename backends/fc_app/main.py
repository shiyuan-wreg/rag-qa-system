r"""
Function Calling Agent - FastAPI 版
====================================
接口:
    POST /chat       - 发送消息，返回 Agent 回答
    GET  /           - 前端页面

运行方式(从仓库根目录):
    venv\Scripts\python.exe -m uvicorn backends.fc_app.main:app --reload --port 8002

然后浏览器打开: http://127.0.0.1:8002
"""

import json
import os
import traceback

from dotenv import load_dotenv
from fastapi import FastAPI, Form, Body
from fastapi.responses import HTMLResponse

from core.config import Config
from core.llm import LLMClient

load_dotenv()
API_KEY = Config.LLM_API_KEY

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

def missing_required_args(tool_name: str, tool_args: dict) -> list:
    """返回该工具缺失(不存在或值为空)的 required 参数名列表。"""
    spec = next((t for t in TOOLS if t["function"]["name"] == tool_name), None)
    if spec is None:
        return []
    required = spec["function"]["parameters"].get("required", [])
    missing = []
    for name in required:
        val = tool_args.get(name)
        if val is None or (isinstance(val, str) and val.strip() == ""):
            missing.append(name)
    return missing


class Agent:
    def __init__(self, model: str = "qwen-turbo"):
        self.model = model
        self.llm = LLMClient.from_config()
        self.messages = []
        self.max_turns = 5
        self.system_message = {
            "role": "system",
            "content": (
                "你是一个智能任务助手,可以查询天气、做数学计算、设置提醒。\n"
                "使用工具后,请把工具结果组织成自然、完整的回答:\n"
                "1. 说明你调用了什么工具以及原因;\n"
                "2. 给出工具返回的结果;\n"
                "3. 根据结果给出建议或下一步操作(例如查到下雨就提示带伞);\n"
                "4. 如果缺少必要参数,主动向用户询问/反问,不要猜测或编造;\n"
                "5. 用 Markdown 组织回答(标题、列表、代码块),前端会渲染成富文本。\n"
                "当你需要获取实时信息或进行精确计算时,必须使用提供的工具。\n"
                "如果工具调用失败,如实向用户说明情况,不要编造结果。"
            )
        }

    def chat(self, user_input: str) -> dict:
        """返回包含回答和工具调用记录的字典"""
        self.messages.append({"role": "user", "content": user_input})
        tool_calls_log = []

        for turn in range(self.max_turns):
            try:
                message = self.llm.chat(
                    [self.system_message] + self.messages,
                    tools=TOOLS,
                )

                if message.get("tool_calls"):
                    # 记录工具调用
                    for tc in message["tool_calls"]:
                        tool_calls_log.append({
                            "name": tc["function"]["name"],
                            "arguments": json.loads(tc["function"]["arguments"]),
                        })

                    # 处理工具调用
                    self.messages.append({
                        "role": "assistant",
                        "content": message["content"] or "",
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

                    for tool_call in message["tool_calls"]:
                        tool_name = tool_call["function"]["name"]
                        tool_args = json.loads(tool_call["function"]["arguments"])

                        missing = missing_required_args(tool_name, tool_args)
                        if missing:
                            result = (
                                f"缺少必要参数:{', '.join(missing)}。"
                                "请向用户说明并询问这些信息,不要猜测或编造。"
                            )
                        else:
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
                    answer = message["content"]
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


@app.post("/execute")
def execute(tool: str = Body(...), args: dict = Body(default_factory=dict)):
    handler = TOOL_MAP.get(tool)
    if handler is None:
        return {"result": f"错误: 未知工具 '{tool}'"}
    try:
        result = handler(**args)
        return {"result": result}
    except Exception as e:
        return {"result": f"工具执行失败: {e}"}


# ==================== 前端页面 ====================

AGENT_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Function Calling Agent</title>
    <script>
    // 跟随门户主题:读 localStorage,监听 storage 事件即时换肤(同源 iframe 自动收到)
    (function(){
      var KEY='ai-demos-theme', VALID=['mono-light','light','deepblue','cyber','machine'];
      function apply(t){ if(VALID.indexOf(t)<0)t='mono-light'; document.documentElement.setAttribute('data-demo-theme',t); }
      try{ apply(localStorage.getItem(KEY)); }catch(e){ apply('mono-light'); }
      window.addEventListener('storage', function(e){ if(e.key===KEY) apply(e.newValue); });
    })();
    </script>
    <style>
        :root, [data-demo-theme="mono-light"]{
          --d-bg:#fafafa;--d-surface:#fff;--d-surface-soft:#f8f8f9;--d-border:rgba(0,0,0,.12);
          --d-text:#09090b;--d-dim:#71717a;--d-accent:#09090b;--d-accent-text:#fafafa;--d-danger:#dc2626;
          --d-font:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
        }
        [data-demo-theme="light"]{
          --d-bg:#f6f7fb;--d-surface:#fff;--d-surface-soft:#f8fafc;--d-border:#e2e8f0;
          --d-text:#0f172a;--d-dim:#64748b;--d-accent:#4f46e5;--d-accent-text:#fff;--d-danger:#dc2626;
          --d-font:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
        }
        [data-demo-theme="deepblue"]{
          --d-bg:#0b1120;--d-surface:#111827;--d-surface-soft:#172033;--d-border:#1f2937;
          --d-text:#f8fafc;--d-dim:#94a3b8;--d-accent:#2563eb;--d-accent-text:#fff;--d-danger:#f87171;
          --d-font:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;
        }
        [data-demo-theme="cyber"]{
          --d-bg:#050507;--d-surface:#0f0f12;--d-surface-soft:#141417;--d-border:#27272a;
          --d-text:#e4e4e7;--d-dim:#71717a;--d-accent:#a3e635;--d-accent-text:#050507;--d-danger:#ff5577;
          --d-font:"JetBrains Mono",ui-monospace,Consolas,"PingFang SC","Microsoft YaHei",monospace;
        }
        [data-demo-theme="machine"]{
          --d-bg:#0a0a0c;--d-surface:#0e0e11;--d-surface-soft:#111114;--d-border:rgba(227,179,65,.30);
          --d-text:#e3b341;--d-dim:#9a8c5a;--d-accent:#e3b341;--d-accent-text:#0a0a0c;--d-danger:#ff4500;
          --d-font:"JetBrains Mono",ui-monospace,Consolas,"PingFang SC","Microsoft YaHei",monospace;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: var(--d-font); background: var(--d-bg); color: var(--d-text);
            min-height: 100vh; padding: 20px; transition: background .25s, color .25s;
        }
        .container { max-width: 720px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 16px; }
        .header h1 { font-size: 20px; letter-spacing: .04em; }
        .header p { font-size: 13px; color: var(--d-dim); margin-top: 4px; }

        .hud-box {
            position: relative; background: var(--d-surface); border: 1px solid var(--d-border); border-radius: 0;
            --c: var(--d-accent); --cl: 11px;
            background-image:
              linear-gradient(var(--c),var(--c)), linear-gradient(var(--c),var(--c)),
              linear-gradient(var(--c),var(--c)), linear-gradient(var(--c),var(--c)),
              linear-gradient(var(--c),var(--c)), linear-gradient(var(--c),var(--c)),
              linear-gradient(var(--c),var(--c)), linear-gradient(var(--c),var(--c));
            background-repeat: no-repeat;
            background-size:
              var(--cl) 2px, 2px var(--cl), var(--cl) 2px, 2px var(--cl),
              var(--cl) 2px, 2px var(--cl), var(--cl) 2px, 2px var(--cl);
            background-position:
              top left, top left, top right, top right,
              bottom left, bottom left, bottom right, bottom right;
        }
        .chat-container { display: flex; flex-direction: column; height: calc(100vh - 150px); }

        .term-head {
            display: flex; align-items: center; gap: 10px; padding: 10px 14px;
            border-bottom: 1px solid var(--d-border); text-transform: uppercase;
            letter-spacing: .14em; font-size: 12px; color: var(--d-dim);
        }
        .term-head .dot {
            width: 8px; height: 8px; border-radius: 50%; background: var(--d-danger);
            box-shadow: 0 0 8px var(--d-danger); animation: blink 1.4s steps(2, start) infinite;
        }
        .term-head .spacer { flex: 1; }
        @keyframes blink { 50% { opacity: .25; } }

        .toolbar { display: flex; gap: 10px; padding: 10px 14px; border-bottom: 1px solid var(--d-border); }
        .toolbar button {
            padding: 6px 12px; border: 1px solid var(--d-border); background: transparent;
            color: var(--d-dim); font-size: 12px; cursor: pointer; border-radius: 0; font-family: inherit;
        }
        .toolbar button:hover { color: var(--d-text); border-color: var(--d-accent); }

        .messages { flex: 1; overflow-y: auto; padding: 18px; display: flex; flex-direction: column; gap: 12px; }
        .msg {
            max-width: 82%; padding: 10px 14px; font-size: 14px; line-height: 1.6;
            border: 1px solid var(--d-border); border-radius: 0; word-break: break-word; white-space: pre-wrap;
        }
        .msg.user {
            align-self: flex-end; border-color: var(--d-accent); color: var(--d-text);
            background: color-mix(in srgb, var(--d-accent) 12%, transparent);
        }
        .msg.assistant { align-self: flex-start; background: var(--d-surface-soft); color: var(--d-text); }
        .msg .tools { margin-top: 8px; padding-top: 8px; border-top: 1px dashed var(--d-border); font-size: 12px; color: var(--d-dim); }
        .msg .tool-item { margin-top: 4px; padding: 4px 8px; background: var(--d-bg); border: 1px solid var(--d-border); }

        .input-area { display: flex; gap: 10px; padding: 14px; border-top: 1px solid var(--d-border); }
        .input-area input {
            flex: 1; padding: 11px 14px; border: 1px solid var(--d-border); background: var(--d-bg);
            color: var(--d-text); font-size: 14px; outline: none; font-family: inherit; border-radius: 0;
        }
        .input-area input:focus { border-color: var(--d-accent); }
        .input-area button {
            padding: 11px 22px; background: var(--d-accent); color: var(--d-accent-text); border: none;
            cursor: pointer; font-weight: 700; letter-spacing: .08em; font-family: inherit;
            border-radius: 0; text-transform: uppercase;
        }
        .input-area button:disabled { opacity: .45; cursor: not-allowed; }
        .welcome { text-align: center; padding: 40px; color: var(--d-dim); }

        .thinking { display: inline-flex; align-items: center; gap: 8px; color: var(--d-dim); }
        .thinking .dots { display: inline-flex; gap: 4px; }
        .thinking .dots i { width: 5px; height: 5px; border-radius: 50%; background: var(--d-accent); display: inline-block; animation: think 1s infinite; }
        .thinking .dots i:nth-child(2) { animation-delay: .18s; }
        .thinking .dots i:nth-child(3) { animation-delay: .36s; }
        @keyframes think { 0%,80%,100% { opacity: .2; transform: translateY(0); } 40% { opacity: 1; transform: translateY(-3px); } }

        .alert {
            display: flex; align-items: flex-start; gap: 10px; padding: 11px 14px;
            border: 1px solid var(--d-danger); border-radius: 0;
            background: color-mix(in srgb, var(--d-danger) 12%, transparent);
            color: var(--d-danger); font-size: 13px; line-height: 1.55;
        }
        .alert svg { flex: none; width: 18px; height: 18px; margin-top: 1px; }

        @media (prefers-reduced-motion: reduce) { .term-head .dot, .thinking .dots i { animation: none; } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Function Calling Agent</h1>
            <p>支持天气查询、数学计算、设置提醒</p>
        </div>
        <div class="hud-box chat-container">
            <div class="term-head">
                <span class="dot"></span>
                <span>FC // Function Calling</span>
                <span class="spacer"></span>
                <span>ENGINE: DEEPSEEK · STATUS: ONLINE</span>
            </div>
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
        const WARN_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>';

        function addMsg(content, type, tools) {
            const div = document.createElement('div');
            div.className = 'msg ' + type;
            let html = escapeHtml(content);
            if (tools && tools.length) {
                html += '<div class="tools">调用了工具:';
                tools.forEach(t => {
                    html += `<div class="tool-item">${escapeHtml(t.name)}(${escapeHtml(JSON.stringify(t.arguments))})</div>`;
                });
                html += '</div>';
            }
            div.innerHTML = html;
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        function addThinking(label) {
            const div = document.createElement('div');
            div.className = 'msg assistant';
            div.innerHTML = '<span class="thinking">' + escapeHtml(label) +
                ' <span class="dots"><i></i><i></i><i></i></span></span>';
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
            return div;
        }

        function addAlert(text) {
            const div = document.createElement('div');
            div.className = 'msg assistant';
            div.style.maxWidth = '100%';
            div.style.border = 'none';
            div.style.background = 'transparent';
            div.style.padding = '0';
            div.innerHTML = '<div class="alert">' + WARN_SVG + '<div>' + escapeHtml(text) + '</div></div>';
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }

        async function send() {
            const text = input.value.trim();
            if (!text) return;

            addMsg(text, 'user');
            input.value = '';
            sendBtn.disabled = true;

            const loading = addThinking('思考中');

            try {
                const form = new FormData();
                form.append('query', text);
                const res = await fetch('chat', { method: 'POST', body: form });
                const data = await res.json();

                loading.remove();

                if (data.error) {
                    addAlert('错误: ' + data.error);
                } else {
                    addMsg(data.answer, 'assistant', data.tool_calls);
                }
            } catch (e) {
                loading.remove();
                addAlert('请求失败: ' + e.message);
            } finally {
                sendBtn.disabled = false;
            }
        }

        async function clearHistory() {
            await fetch('clear', { method: 'POST' });
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
