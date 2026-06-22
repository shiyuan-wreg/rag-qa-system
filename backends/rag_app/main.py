"""
智能文档任务 Agent - FastAPI Web 服务
=====================================
接口：
    POST /chat    - 发送消息，返回 Agent 回答
    POST /clear   - 清空对话历史
    POST /eval    - 运行测试用例评估
    GET  /        - 前端页面

运行方式：
    venv/Scripts/python.exe -m uvicorn app:app --reload --port 8000
"""

import os

import dashscope
from dotenv import load_dotenv
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse

load_dotenv()

from core.agent import Agent
from core.rag_tool import init_rag_tool, search_docs
from core.tools import TOOL_MAP
from eval.evaluator import run_test_cases

API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
dashscope.api_key = API_KEY

app = FastAPI(title="基于 RAG + Function Calling 的智能文档任务 Agent")

# 初始化 RAG 工具
init_rag_tool()
TOOL_MAP["search_docs"] = search_docs

# 全局 Agent 实例（单用户简化版）
agent = Agent()


@app.get("/", response_class=HTMLResponse)
def index():
    """前端页面。"""
    return HTMLResponse(content=HTML_PAGE)


@app.post("/chat")
def chat(query: str = Form(...)):
    """对话接口。"""
    if not API_KEY:
        return JSONResponse({"error": "API Key 未配置"}, status_code=500)

    result = agent.chat(query)
    return result


@app.post("/clear")
def clear():
    """清空对话历史。"""
    agent.clear_history()
    return {"message": "对话历史已清空"}


@app.post("/eval")
def eval_agent():
    """运行测试用例评估。"""
    if not API_KEY:
        return JSONResponse({"error": "API Key 未配置"}, status_code=500)

    test_cases = [
        {"query": "Python 中列表和元组有什么区别？"},
        {"query": "帮我算一下 (15 + 27) * 3"},
        {"query": "docs 目录下有什么文件？"},
    ]

    result = run_test_cases(agent.chat, test_cases)
    return result


HTML_PAGE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智能文档任务 Agent</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
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
            background: #667eea;
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
        .input-area input:focus { border-color: #667eea; }
        .input-area button {
            padding: 12px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
        }
        .input-area button:disabled { background: #ccc; }
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
            <h1>智能文档任务 Agent</h1>
            <p>基于 RAG + Function Calling 的文档问答与任务执行助手</p>
        </div>
        <div class="chat-container">
            <div class="toolbar">
                <button onclick="clearHistory()">清空对话</button>
                <button onclick="runEval()">运行评估</button>
            </div>
            <div class="messages" id="messages">
                <div class="welcome">
                    <div style="font-size:40px;margin-bottom:10px;">🤖</div>
                    <p>输入消息开始对话<br>例如：Python 中列表和元组有什么区别？</p>
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
            loading.className = 'msg assistant';
            loading.style.fontStyle = 'italic';
            loading.style.color = '#888';
            loading.textContent = '思考中...';
            messages.appendChild(loading);

            try {
                const form = new FormData();
                form.append('query', text);
                const res = await fetch('chat', { method: 'POST', body: form });
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
            await fetch('clear', { method: 'POST' });
            messages.innerHTML = `
                <div class="welcome">
                    <div style="font-size:40px;margin-bottom:10px;">🤖</div>
                    <p>对话已清空<br>输入消息开始新对话</p>
                </div>
            `;
        }

        async function runEval() {
            const loading = document.createElement('div');
            loading.className = 'msg assistant';
            loading.style.fontStyle = 'italic';
            loading.style.color = '#888';
            loading.textContent = '正在运行评估...';
            messages.appendChild(loading);

            try {
                const res = await fetch('eval', { method: 'POST' });
                const data = await res.json();
                loading.remove();

                if (data.error) {
                    addMsg('评估错误: ' + data.error, 'assistant');
                } else {
                    let html = `平均得分: ${data.average_score}\n\n`;
                    data.results.forEach((item, i) => {
                        html += `问题 ${i+1}: ${item.query}\n`;
                        html += `回答: ${item.answer.substring(0, 80)}...\n`;
                        html += `得分: ${JSON.stringify(item.scores)}\n\n`;
                    });
                    addMsg(html, 'assistant');
                }
            } catch (e) {
                loading.remove();
                addMsg('评估请求失败: ' + e.message, 'assistant');
            }
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
    uvicorn.run(app, host="127.0.0.1", port=8000)
