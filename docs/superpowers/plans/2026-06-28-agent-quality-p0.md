# Agent 回答质量优化 P0 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 通过重写 RAG/FC 的 system prompt、改进 RAG 检索结果格式化、给两个 demo 前端加内联 Markdown 渲染、给 FC 加缺参数代码强制反问,显著提升两个 demo 的回答质量。

**Architecture:** 改动集中在 `core/`(RAG 侧逻辑+prompt)和 `backends/{rag_app,fc_app}/main.py`(FC 逻辑+prompt+两端内联前端)。可单测的逻辑(RAG 格式化纯函数、FC 缺参数校验)走 TDD;prompt 用轻量 smoke 测试锁定关键指令;前端 Markdown 渲染靠浏览器肉眼验收。

**Tech Stack:** Python 3.12 + FastAPI + pytest(house style:`sys.path` 注入 + 纯 `assert`,无 conftest);前端为内联 HTML/原生 JS(无构建、无 CDN)。

## Global Constraints

- 不改检索算法:`top_k` 维持 3,不动 `rag/retriever.py`、`rag/splitter.py`、`rag/loader.py`。
- 不接真实 API;不改 FC `calculate` 的 `eval`(P1)。
- Markdown 渲染器**不依赖 CDN**,两端各自内联(接受重复)。
- 安全:前端渲染回答时**先 escape 再做 markdown 变换**;user 消息永远纯文本转义。
- 测试 house style:文件顶部 `sys.path.insert(0, ...)` 注入仓库根;用纯 `assert` + `print("[OK] ...")`;可 `python tests/xxx.py` 直接跑。
- 本次**只本地验收,不部署生产**。
- 提交信息结尾附:`Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。

---

### Task 1: RAG 检索结果格式化(抽纯函数 + TDD)

**Files:**
- Modify: `core/rag_tool.py`(抽出 `format_retrieved`,`RAGTool.search` 改为调用它)
- Test: `tests/test_rag_tool.py`(新建)

**Interfaces:**
- Produces: `format_retrieved(query: str, docs: list, max_chars: int = 800) -> str`
  - `docs` 是 langchain Document 风格对象,需有 `.page_content`(str)和 `.metadata`(dict,可能含 `"source"`)。
  - 返回:首行 `用户问题:{query}`,次行排序提示,随后每片段 `[i] 来源:{basename}` 换行接 `page_content`(strip,**保留内部换行**),单片段超 `max_chars` 截断加 `…`。

- [ ] **Step 1: 写失败测试**

新建 `tests/test_rag_tool.py`:

```python
"""Unit tests for RAG retrieval formatting"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.rag_tool import format_retrieved


class _Doc:
    def __init__(self, content, source=None):
        self.page_content = content
        self.metadata = {"source": source} if source else {}


def test_format_preserves_newlines_and_source():
    docs = [_Doc("def add(a, b):\n    return a + b", source="/app/docs/python_guide.txt")]
    out = format_retrieved("什么是函数", docs)
    assert "什么是函数" in out                      # 含 query
    assert "python_guide.txt" in out                # 含来源 basename(非全路径)
    assert "/app/docs" not in out                   # 只取 basename
    assert "    return a + b" in out                # 保留换行+缩进(未被压成空格)
    assert "[1]" in out
    print("[OK] format preserves newlines and source")


def test_format_truncates_long_chunk():
    docs = [_Doc("x" * 1000, source="a.txt")]
    out = format_retrieved("q", docs, max_chars=800)
    assert "…" in out
    assert "x" * 801 not in out                     # 截断生效
    print("[OK] format truncates long chunk")


def test_format_missing_source_label():
    docs = [_Doc("hello")]
    out = format_retrieved("q", docs)
    assert "未知来源" in out
    print("[OK] format labels missing source")


if __name__ == "__main__":
    test_format_preserves_newlines_and_source()
    test_format_truncates_long_chunk()
    test_format_missing_source_label()
    print("\nAll rag_tool format tests passed!")
```

- [ ] **Step 2: 跑测试确认失败**

Run: `venv/Scripts/python.exe -m pytest tests/test_rag_tool.py -v`
Expected: FAIL —— `ImportError: cannot import name 'format_retrieved'`

- [ ] **Step 3: 实现 `format_retrieved` 并让 `search` 调用它**

在 `core/rag_tool.py` 顶部 import 区下方(`retrieve` import 之后)新增纯函数:

```python
def format_retrieved(query: str, docs: list, max_chars: int = 800) -> str:
    """把检索到的片段格式化为带来源、保留原始换行的文本。"""
    parts = [f"用户问题:{query}", "以下是按相关度排序的相关片段:"]
    for i, doc in enumerate(docs, 1):
        source = doc.metadata.get("source") if getattr(doc, "metadata", None) else None
        label = os.path.basename(source) if source else "未知来源"
        content = doc.page_content.strip()
        if len(content) > max_chars:
            content = content[:max_chars] + "…"
        parts.append(f"[{i}] 来源:{label}\n{content}")
    return "\n\n".join(parts)
```

把 `RAGTool.search` 中的格式化块替换为调用:

```python
    def search(self, query: str, top_k: int = 3) -> str:
        """执行检索,返回格式化的文本片段。"""
        if not self.vectorstore:
            return "错误: RAG 知识库未初始化,请检查 API Key 和文档路径"

        try:
            docs = retrieve(self.vectorstore, query, k=top_k)
            if not docs:
                return "未检索到相关文档片段"
            return format_retrieved(query, docs)
        except Exception as e:
            return f"检索错误: {e}"
```

(`os` 已在文件顶部 import,无需新增。)

- [ ] **Step 4: 跑测试确认通过**

Run: `venv/Scripts/python.exe -m pytest tests/test_rag_tool.py -v`
Expected: PASS(3 passed)

- [ ] **Step 5: 提交**

```bash
git add core/rag_tool.py tests/test_rag_tool.py
git commit -m "feat(rag): preserve newlines + source in retrieval formatting

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: RAG system prompt 重写(`core/agent.py`)

**Files:**
- Modify: `core/agent.py:40-50`(`self.system_message`)
- Test: `tests/test_agent.py`(追加一个 smoke 测试)

**Interfaces:**
- Consumes: 无新依赖。
- Produces: `Agent().system_message["content"]` 含关键指令(供 smoke 测试断言)。

- [ ] **Step 1: 写失败测试**

在 `tests/test_agent.py` 的 `test_agent_clear_history` 之后追加:

```python
def test_agent_system_prompt_directives():
    """system prompt 必须包含详细回答/引用/不编造的关键指令。"""
    agent = Agent()
    content = agent.system_message["content"]
    assert "[1]" in content              # 引用标注要求
    assert "结论" in content              # 先给结论
    assert "Markdown" in content or "markdown" in content  # 结构化输出
    assert "无法确定" in content          # 不编造
    print("[OK] RAG system prompt directives present")
```

并在 `__main__` 块追加调用 `test_agent_system_prompt_directives()`。

- [ ] **Step 2: 跑测试确认失败**

Run: `venv/Scripts/python.exe -m pytest tests/test_agent.py::test_agent_system_prompt_directives -v`
Expected: FAIL —— assert `"[1]" in content`

- [ ] **Step 3: 重写 system_message**

把 `core/agent.py` 的 `self.system_message` 替换为:

```python
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
```

- [ ] **Step 4: 跑测试确认通过**

Run: `venv/Scripts/python.exe -m pytest tests/test_agent.py -v`
Expected: PASS(原有 3 个 + 新增 1 个全过)

- [ ] **Step 5: 提交**

```bash
git add core/agent.py tests/test_agent.py
git commit -m "feat(rag): richer system prompt (structured, cited, no fabrication)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: FC 缺参数代码强制反问(`backends/fc_app/main.py`)

**Files:**
- Modify: `backends/fc_app/main.py`(新增 `missing_required_args` 辅助函数 + 在 `Agent.chat` 工具执行处插入校验分支)
- Test: `tests/fc/test_missing_args.py`(新建)

**Interfaces:**
- Produces: `missing_required_args(tool_name: str, tool_args: dict) -> list[str]`
  - 读模块级 `TOOLS` 找该工具的 `function.parameters.required`;返回「缺失或值为空串/None」的 required 参数名列表;工具不存在时返回 `[]`。

- [ ] **Step 1: 写失败测试**

新建 `tests/fc/test_missing_args.py`:

```python
"""Unit tests for FC missing-required-argument detection"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backends.fc_app.main import missing_required_args


def test_missing_returns_absent_required():
    # set_reminder 需要 content + time,这里缺 time
    assert missing_required_args("set_reminder", {"content": "开会"}) == ["time"]
    print("[OK] detects absent required arg")


def test_missing_treats_empty_as_missing():
    assert missing_required_args("set_reminder", {"content": "开会", "time": ""}) == ["time"]
    print("[OK] empty string counts as missing")


def test_missing_none_when_complete():
    assert missing_required_args("get_weather", {"city": "北京"}) == []
    print("[OK] complete args -> no missing")


def test_missing_unknown_tool_empty():
    assert missing_required_args("no_such_tool", {}) == []
    print("[OK] unknown tool -> empty")


if __name__ == "__main__":
    test_missing_returns_absent_required()
    test_missing_treats_empty_as_missing()
    test_missing_none_when_complete()
    test_missing_unknown_tool_empty()
    print("\nAll FC missing-args tests passed!")
```

- [ ] **Step 2: 跑测试确认失败**

Run: `venv/Scripts/python.exe -m pytest tests/fc/test_missing_args.py -v`
Expected: FAIL —— `ImportError: cannot import name 'missing_required_args'`

- [ ] **Step 3: 实现辅助函数 + 接入 chat 循环**

在 `backends/fc_app/main.py` 的 `TOOLS = [...]` 定义之后、`class Agent` 之前新增:

```python
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
```

在 `Agent.chat` 的「逐个执行工具」`for tool_call in message["tool_calls"]:` 循环体内,把现有的 try/执行块替换为先校验缺参:

```python
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
```

- [ ] **Step 4: 跑测试确认通过**

Run: `venv/Scripts/python.exe -m pytest tests/fc/test_missing_args.py -v`
Expected: PASS(4 passed)

- [ ] **Step 5: 提交**

```bash
git add backends/fc_app/main.py tests/fc/test_missing_args.py
git commit -m "feat(fc): enforce re-ask on missing required tool args

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: FC system prompt 重写(`backends/fc_app/main.py`)

**Files:**
- Modify: `backends/fc_app/main.py`(`Agent.system_message`,约 117-124 行)
- Test: `tests/fc/test_missing_args.py`(追加 smoke 断言)

**Interfaces:**
- Produces: `Agent().system_message["content"]` 含关键指令。

- [ ] **Step 1: 写失败测试**

在 `tests/fc/test_missing_args.py` 顶部 import 处增加 `from backends.fc_app.main import Agent`,并追加:

```python
def test_fc_system_prompt_directives():
    agent = Agent()
    content = agent.system_message["content"]
    assert "建议" in content                  # 给建议/下一步
    assert "反问" in content or "询问" in content  # 缺参反问
    assert "Markdown" in content or "markdown" in content
    print("[OK] FC system prompt directives present")
```

并在 `__main__` 块追加调用。

- [ ] **Step 2: 跑测试确认失败**

Run: `venv/Scripts/python.exe -m pytest tests/fc/test_missing_args.py::test_fc_system_prompt_directives -v`
Expected: FAIL —— assert `"建议" in content`

- [ ] **Step 3: 重写 system_message**

把 `backends/fc_app/main.py` 的 `self.system_message` 替换为:

```python
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
```

- [ ] **Step 4: 跑测试确认通过**

Run: `venv/Scripts/python.exe -m pytest tests/fc/test_missing_args.py -v`
Expected: PASS(5 passed)

- [ ] **Step 5: 提交**

```bash
git add backends/fc_app/main.py tests/fc/test_missing_args.py
git commit -m "feat(fc): richer system prompt (explain tools, advise, re-ask)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: RAG 前端内联 Markdown 渲染(`backends/rag_app/main.py`)

**Files:**
- Modify: `backends/rag_app/main.py`(内联 HTML:`<style>` 加 markdown 样式,`<script>` 加 `renderMarkdown`,`addMsg` 区分 assistant/user)

**Interfaces:**
- Produces: 前端 JS 函数 `renderMarkdown(src)`(与 Task 6 完全相同的实现)。

> 本任务无单元测试(内联前端无 JS 测试运行器),靠 Step 4 浏览器肉眼验收。

- [ ] **Step 1: 在 `<style>` 内追加 markdown 样式**

在 `backends/rag_app/main.py` 内联 HTML 的 `</style>` 之前追加:

```css
        .md-h { margin: 10px 0 6px; line-height: 1.3; }
        .md-ul, .md-ol { margin: 6px 0 6px 20px; }
        .md-ul li, .md-ol li { margin: 2px 0; }
        .md-code { background: var(--d-bg); border: 1px solid var(--d-border); padding: 1px 5px; border-radius: 0; font-family: "JetBrains Mono", ui-monospace, Consolas, monospace; font-size: 12.5px; }
        .md-pre { background: var(--d-bg); border: 1px solid var(--d-border); padding: 10px 12px; margin: 8px 0; overflow-x: auto; }
        .md-pre code { font-family: "JetBrains Mono", ui-monospace, Consolas, monospace; font-size: 12.5px; white-space: pre; }
        .md-table { border-collapse: collapse; margin: 8px 0; font-size: 13px; }
        .md-table th, .md-table td { border: 1px solid var(--d-border); padding: 5px 9px; text-align: left; }
        .md-table th { background: var(--d-surface-soft); }
        .msg.assistant p { margin: 6px 0; }
        .msg.assistant p:first-child { margin-top: 0; }
        .msg.assistant a { color: var(--d-accent); }
```

- [ ] **Step 2: 在 `<script>` 内加 `renderMarkdown`**

在 `backends/rag_app/main.py` 内联脚本里、`escapeHtml` 函数附近加入(完整实现):

```javascript
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
```

- [ ] **Step 3: `addMsg` 对 assistant 用 markdown**

把 `addMsg` 里 `let html = escapeHtml(content);` 改为按类型区分:

```javascript
            let html = (type === 'assistant') ? renderMarkdown(content) : escapeHtml(content);
```

(其余 tools 拼接逻辑不变。)

- [ ] **Step 4: 浏览器肉眼验收**

```bash
bash deploy/build-frontends.sh
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml up -d --build
docker restart deploy-nginx-1
```

访问 http://127.0.0.1:8080/rag/ ,问一个会触发结构化回答的问题(如「Python 列表和元组的区别?」)。
Expected:回答里的标题/有序列表/代码块/表格被渲染成富文本(不是裸 `#`/`**`/```` ``` ````);自己输入的 user 消息保持纯文本(若输入 `**x**` 不应变粗)。

- [ ] **Step 5: 提交**

```bash
git add backends/rag_app/main.py
git commit -m "feat(rag): inline markdown rendering for assistant answers

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: FC 前端内联 Markdown 渲染(`backends/fc_app/main.py`)

**Files:**
- Modify: `backends/fc_app/main.py`(内联 HTML:同 Task 5 的样式 + `renderMarkdown` + `addMsg` 区分)

**Interfaces:**
- Consumes: 与 Task 5 完全相同的 `renderMarkdown` 实现(原样复制,两端各一份)。

> 无单元测试,靠 Step 4 浏览器肉眼验收。

- [ ] **Step 1: 在 `<style>` 内追加 markdown 样式**

在 `backends/fc_app/main.py` 内联 HTML 的 `</style>` 之前追加(与 Task 5 Step 1 完全相同):

```css
        .md-h { margin: 10px 0 6px; line-height: 1.3; }
        .md-ul, .md-ol { margin: 6px 0 6px 20px; }
        .md-ul li, .md-ol li { margin: 2px 0; }
        .md-code { background: var(--d-bg); border: 1px solid var(--d-border); padding: 1px 5px; border-radius: 0; font-family: "JetBrains Mono", ui-monospace, Consolas, monospace; font-size: 12.5px; }
        .md-pre { background: var(--d-bg); border: 1px solid var(--d-border); padding: 10px 12px; margin: 8px 0; overflow-x: auto; }
        .md-pre code { font-family: "JetBrains Mono", ui-monospace, Consolas, monospace; font-size: 12.5px; white-space: pre; }
        .md-table { border-collapse: collapse; margin: 8px 0; font-size: 13px; }
        .md-table th, .md-table td { border: 1px solid var(--d-border); padding: 5px 9px; text-align: left; }
        .md-table th { background: var(--d-surface-soft); }
        .msg.assistant p { margin: 6px 0; }
        .msg.assistant p:first-child { margin-top: 0; }
        .msg.assistant a { color: var(--d-accent); }
```

- [ ] **Step 2: 在 `<script>` 内加 `renderMarkdown`**

在 `backends/fc_app/main.py` 内联脚本里、`escapeHtml` 附近加入(与 Task 5 Step 2 **逐字相同**的函数):

```javascript
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
```

- [ ] **Step 3: `addMsg` 对 assistant 用 markdown**

把 FC 的 `addMsg` 里 `let html = escapeHtml(content);` 改为:

```javascript
            let html = (type === 'assistant') ? renderMarkdown(content) : escapeHtml(content);
```

- [ ] **Step 4: 浏览器肉眼验收**

```bash
bash deploy/build-frontends.sh
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml up -d --build
docker restart deploy-nginx-1
```

访问 http://127.0.0.1:8080/fc/ ,测试三类:
1. 「北京和上海哪个天气更好?」→ 看是否解释过程 + 给建议 + Markdown 渲染。
2. 「帮我设个提醒」(不给时间)→ 应反问时间,而不是瞎设。
3. 「(15+27)*3 等于多少」→ 计算 + 解释。
Expected:回答富文本渲染;缺参数时反问。

- [ ] **Step 5: 提交**

```bash
git add backends/fc_app/main.py
git commit -m "feat(fc): inline markdown rendering for assistant answers

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: 全量回归 + 收尾

**Files:** 无改动(验证 + 文档)

- [ ] **Step 1: 跑全量测试**

Run: `venv/Scripts/python.exe -m pytest tests/ -v`
Expected: 新增用例全过;原有用例不回归(已知 `tests/fc/test_execute.py` 可能因本机 venv 未装 `openai` 收集失败,与本次改动无关——若出现,确认是同一原因即可)。

- [ ] **Step 2: 更新交接文档**

在 `docs/PROJECT-STATE.md` 顶部更新最近进展:P0 Agent 质量优化已完成(RAG/FC prompt + RAG 格式化 + FC 缺参反问 + 两端 markdown 渲染),本地验收通过,**生产未部署**(与主题皮肤批次一并延后)。

- [ ] **Step 3: 提交**

```bash
git add docs/PROJECT-STATE.md
git commit -m "docs: record P0 agent-quality optimization done (local only)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## 备注

- 各 demo 后端为运行中容器,本地用 `up --build` 重建会把源改动正式烤进镜像(rag/fc 源已提交,重建即生效);改单容器后需 `docker restart deploy-nginx-1` 防 502。
- 本计划不含生产部署;收尾后可单独走「重建镜像 + 推首尔」。
