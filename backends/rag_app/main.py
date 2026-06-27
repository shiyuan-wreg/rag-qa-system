"""
智能文档任务 Agent - FastAPI Web 服务
=====================================
接口：
    POST /chat    - 发送消息，返回 Agent 回答
    POST /clear   - 清空对话历史
    POST /eval    - 运行测试用例评估
    GET  /        - 前端页面

运行方式（从仓库根目录）：
    venv/Scripts/python.exe -m uvicorn backends.rag_app.main:app --reload --port 8001
"""

import os

from dotenv import load_dotenv
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse

load_dotenv()

from core.config import Config
from core.agent import Agent
from core.rag_tool import init_rag_tool, search_docs
from core.tools import TOOL_MAP
from eval.evaluator import run_test_cases

API_KEY = Config.LLM_API_KEY

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


HTML_PAGE = r"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>智能文档任务 Agent</title>
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
        /* ===== 五主题调色板(对齐门户 theme.css) ===== */
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
            font-family: var(--d-font);
            background: var(--d-bg);
            color: var(--d-text);
            min-height: 100vh;
            padding: 20px;
            transition: background .25s, color .25s;
        }
        .container { max-width: 840px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 16px; }
        .header h1 { font-size: 20px; letter-spacing: .04em; }
        .header p { font-size: 13px; color: var(--d-dim); margin-top: 4px; }

        /* HUD 容器:直角 + 四角方括号 */
        .hud-box {
            position: relative;
            background: var(--d-surface);
            border: 1px solid var(--d-border);
            border-radius: 0;
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
        .chat-container {
            display: flex; flex-direction: column;
            height: calc(100vh - 150px);
        }

        /* 终端标题栏 + 闪烁状态点 */
        .term-head {
            display: flex; align-items: center; gap: 10px;
            padding: 10px 14px; border-bottom: 1px solid var(--d-border);
            text-transform: uppercase; letter-spacing: .14em;
            font-size: 12px; color: var(--d-dim);
        }
        .term-head .dot {
            width: 8px; height: 8px; border-radius: 50%;
            background: var(--d-danger); box-shadow: 0 0 8px var(--d-danger);
            animation: blink 1.4s steps(2, start) infinite;
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
            flex: 1; padding: 11px 14px; border: 1px solid var(--d-border);
            background: var(--d-bg); color: var(--d-text); font-size: 14px; outline: none;
            font-family: inherit; border-radius: 0;
        }
        .input-area input:focus { border-color: var(--d-accent); }
        .input-area button {
            padding: 11px 22px; background: var(--d-accent); color: var(--d-accent-text);
            border: none; cursor: pointer; font-weight: 700; letter-spacing: .08em;
            font-family: inherit; border-radius: 0; text-transform: uppercase;
        }
        .input-area button:disabled { opacity: .45; cursor: not-allowed; }
        .welcome { text-align: center; padding: 40px; color: var(--d-dim); }

        /* 思考中:循环跳动三点 */
        .thinking { display: inline-flex; align-items: center; gap: 8px; color: var(--d-dim); }
        .thinking .dots { display: inline-flex; gap: 4px; }
        .thinking .dots i { width: 5px; height: 5px; border-radius: 50%; background: var(--d-accent); display: inline-block; animation: think 1s infinite; }
        .thinking .dots i:nth-child(2) { animation-delay: .18s; }
        .thinking .dots i:nth-child(3) { animation-delay: .36s; }
        @keyframes think { 0%,80%,100% { opacity: .2; transform: translateY(0); } 40% { opacity: 1; transform: translateY(-3px); } }

        /* 警告框:三角内嵌 ! + 主题色 */
        .alert {
            display: flex; align-items: flex-start; gap: 10px;
            padding: 11px 14px; border: 1px solid var(--d-danger); border-radius: 0;
            background: color-mix(in srgb, var(--d-danger) 12%, transparent);
            color: var(--d-danger); font-size: 13px; line-height: 1.55;
        }
        .alert svg { flex: none; width: 18px; height: 18px; margin-top: 1px; }

        @media (prefers-reduced-motion: reduce) {
            .term-head .dot, .thinking .dots i { animation: none; }
        }
        .md-h { margin: 10px 0 6px; line-height: 1.3; }
        .md-ul, .md-ol { margin: 6px 0 6px 20px; }
        .md-ul li, .md-ol li { margin: 2px 0; }
        .md-code { background: var(--d-bg); border: 1px solid var(--d-border); padding: 1px 5px; border-radius: 0; font-family: "JetBrains Mono", ui-monospace, Consolas, monospace; font-size: 12.5px; }
        .md-pre { background: var(--d-bg); border: 1px solid var(--d-border); padding: 10px 12px; margin: 8px 0; overflow-x: auto; }
        .md-pre code { font-family: "JetBrains Mono", ui-monospace, Consolas, monospace; font-size: 12.5px; white-space: pre; }
        .md-table { border-collapse: collapse; margin: 8px 0; font-size: 13px; }
        .md-table th, .md-table td { border: 1px solid var(--d-border); padding: 5px 9px; text-align: left; }
        .md-table th { background: var(--d-surface-soft); }
        .msg.assistant { white-space: normal; }
        .msg.assistant p { margin: 6px 0; }
        .msg.assistant p:first-child { margin-top: 0; }
        .msg.assistant a { color: var(--d-accent); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>智能文档任务 Agent</h1>
            <p>基于 RAG + Function Calling 的文档问答与任务执行助手</p>
        </div>
        <div class="hud-box chat-container">
            <div class="term-head">
                <span class="dot"></span>
                <span>RAG // Document Agent</span>
                <span class="spacer"></span>
                <span>ENGINE: DEEPSEEK · STATUS: ONLINE</span>
            </div>
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
        const WARN_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>';

        function addMsg(content, type, tools) {
            const div = document.createElement('div');
            div.className = 'msg ' + type;
            let html = (type === 'assistant') ? renderMarkdown(content) : escapeHtml(content);
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

        // 思考指示:循环点
        function addThinking(label) {
            const div = document.createElement('div');
            div.className = 'msg assistant';
            div.innerHTML = '<span class="thinking">' + escapeHtml(label) +
                ' <span class="dots"><i></i><i></i><i></i></span></span>';
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
            return div;
        }

        // 错误:三角警告框
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
                    <div style="font-size:40px;margin-bottom:10px;">🤖</div>
                    <p>对话已清空<br>输入消息开始新对话</p>
                </div>
            `;
        }

        async function runEval() {
            const loading = addThinking('正在运行评估');

            try {
                const res = await fetch('eval', { method: 'POST' });
                const data = await res.json();
                loading.remove();

                if (data.error) {
                    addAlert('评估错误: ' + data.error);
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
                addAlert('评估请求失败: ' + e.message);
            }
        }

        function renderMarkdown(src){
            function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}
            var blocks=[];
            src=src.replace(/```[ \t]*([\w+\-]*)\r?\n([\s\S]*?)```/g,function(_,lang,code){
                blocks.push('<pre class="md-pre"><code>'+esc(code.replace(/\r?\n$/,''))+'</code></pre>');
                return '\x00'+(blocks.length-1)+'\x00';
            });
            function inline(t){
                t=esc(t);
                t=t.replace(/`([^`]+)`/g,'<code class="md-code">$1</code>');
                t=t.replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>');
                t=t.replace(/\*([^*\n]+)\*/g,'<em>$1</em>');
                t=t.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,'<a href="$2" target="_blank" rel="noopener">$1</a>');
                return t;
            }
            var lines=src.split(/\r?\n/),out=[],i=0;
            function blank(s){return /^\s*$/.test(s);}
            function cells(s){var a=s.split('|').map(function(c){return c.trim();});if(a.length&&a[0]==='')a.shift();if(a.length&&a[a.length-1]==='')a.pop();return a;}
            while(i<lines.length){
                var line=lines[i];
                var cb=line.match(/^\x00(\d+)\x00\s*$/);
                if(cb){out.push(blocks[+cb[1]]);i++;continue;}
                if(blank(line)){i++;continue;}
                var h=line.match(/^(#{1,6})\s+(.*)$/);
                if(h){out.push('<h'+h[1].length+' class="md-h">'+inline(h[2])+'</h'+h[1].length+'>');i++;continue;}
                if(line.indexOf('|')>=0&&i+1<lines.length&&/^\s*\|?[\s:|-]*-[\s:|-]*\|?\s*$/.test(lines[i+1])){
                    var header=cells(line);i+=2;var rows=[];
                    while(i<lines.length&&!blank(lines[i])&&lines[i].indexOf('|')>=0){rows.push(cells(lines[i]));i++;}
                    var th='<tr>'+header.map(function(c){return '<th>'+inline(c)+'</th>';}).join('')+'</tr>';
                    var tb=rows.map(function(r){return '<tr>'+r.map(function(c){return '<td>'+inline(c)+'</td>';}).join('')+'</tr>';}).join('');
                    out.push('<table class="md-table"><thead>'+th+'</thead><tbody>'+tb+'</tbody></table>');continue;
                }
                if(/^\s*[-*+]\s+/.test(line)){
                    var ul=[];
                    while(i<lines.length&&/^\s*[-*+]\s+/.test(lines[i])){ul.push('<li>'+inline(lines[i].replace(/^\s*[-*+]\s+/,''))+'</li>');i++;}
                    out.push('<ul class="md-ul">'+ul.join('')+'</ul>');continue;
                }
                if(/^\s*\d+\.\s+/.test(line)){
                    var ol=[];
                    while(i<lines.length&&/^\s*\d+\.\s+/.test(lines[i])){ol.push('<li>'+inline(lines[i].replace(/^\s*\d+\.\s+/,''))+'</li>');i++;}
                    out.push('<ol class="md-ol">'+ol.join('')+'</ol>');continue;
                }
                var para=[];
                while(i<lines.length&&!blank(lines[i])&&!/^\x00\d+\x00/.test(lines[i])&&!/^(#{1,6})\s+/.test(lines[i])&&!/^\s*[-*+]\s+/.test(lines[i])&&!/^\s*\d+\.\s+/.test(lines[i])){para.push(lines[i]);i++;}
                out.push('<p>'+para.map(inline).join('<br>')+'</p>');
            }
            return out.join('');
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
