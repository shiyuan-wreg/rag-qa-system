# ai-demos 项目基础与进阶知识学习指南

> 本文档面向零基础或刚接触 AI/Agent 开发的读者，结合 `C:\Users\hzs17\Desktop\ai-demos` 项目源码，从最基础的概念讲起，逐步深入到项目所用到的进阶技术。阅读时不必一次读完，可按章节循序渐进。

---

## 0. 项目全景：ai-demos 是什么？

### 0.1 一句话概括

`ai-demos` 是一个把多个 AI/Agent 相关小 demo 整合在一起的**个人作品集门户**。它目前包含：

- 一个基于 **RAG + Function Calling** 的智能文档问答 Agent（`/rag/`）；
- 一个只演示 **Function Calling** 的 Agent（`/fc/`）；
- 一个 **Nexus Multi-Agent** 工作流助手（`/nexus/`）；
- 一个 **DocHub** Markdown 文档站（`/doctomd/`）；
- 一个 **IconForge** 图标净化器（`/iconforge/`）；
- 一个统一展示的 **React 门户外壳**（黑白科技风，含"监控"可选主题）；
- 一个交互式学习站 `nexus-learning-web`（`/learn/`）；
- 用 **Docker + Nginx** 在本地/服务器把前后端跑起来。

### 0.2 它解决什么问题？

普通大模型有三个常见短板：

1. **知识滞后**：模型训练数据有截止日期，不知道最新或私有文档里的内容。
2. **幻觉**：可能编造不存在的信息。
3. **只会说、不会做**：不能执行计算、读取文件等真实操作。

`ai-demos` 通过 **RAG（检索增强生成）+ Function Calling（函数调用）+ 多 Agent 协作** 来缓解这些问题：

- 需要文档知识时，先检索私有知识库，再把检索结果喂给模型；
- 需要计算/查文件时，调用真实工具执行；
- 多个专门 Agent 分工协作，共同完成复杂任务。

### 0.3 整体架构（简化版）

```
用户（浏览器）
    │
    ▼
┌─────────────────────────────────────┐
│  Nginx（反向代理 + 静态文件托管）      │  端口 80/443（本地是 8080）
└─────────────────────────────────────┘
    │
    ├──▶ /            →  frontends/portfolio/dist（React 门户）
    ├──▶ /learn/      →  frontends/nexus-learning-web/dist（学习站）
    ├──▶ /rag/        →  backends/rag_app/main.py（RAG Agent）
    ├──▶ /fc/         →  backends/fc_app/main.py（Function Calling Agent）
    ├──▶ /nexus/      →  backends/nexus_app/main.py（Nexus Multi-Agent）
    ├──▶ /doctomd/    →  backends/md_converter_app/main.py（DocHub）
    └──▶ /iconforge/  →  backends/iconforge_app/main.py（IconForge）
```

---

## 1. 基础知识篇

### 1.1 大语言模型（LLM）是什么？

#### 1.1.1 从“文字接龙”理解 LLM

大语言模型（Large Language Model，简称 LLM）本质上是一个**超级复杂的文字接龙机器**。你给它一段文字（称为 **Prompt/提示词**），它会根据训练时学到的统计规律，预测下一个最可能出现的词，然后一个词一个词地“接龙”，直到生成完整回答。

例如：

```
输入：中国的首都是
模型预测：北 → 京 → 。
输出：中国的首都是北京。
```

模型并没有“真正理解”知识，而是靠海量文本中的模式来生成看起来合理的回答。这解释了为什么它有时会**幻觉**——也就是编造听起来像真的但实际错误的内容。

#### 1.1.2 模型、参数与能力

- **模型（Model）**：一个训练好的神经网络文件，例如 `qwen-turbo`。
- **参数（Parameters）**：神经网络里的可学习数值，通常用“亿”或“万亿”衡量。参数越多，模型通常越强，但推理成本也越高。
- **推理（Inference）**：把输入喂给模型、得到输出的过程。
- **上下文窗口（Context Window）**：模型一次能处理的文字长度限制，比如 8K、32K、128K token。

#### 1.1.3 Token 是什么？

模型不是直接按“字”或“词”处理文本，而是按 **token** 切分。token 是模型内部使用的基本文本单位：

- 英文通常 1 个 token 约等于 0.75 个单词；
- 中文通常 1 个汉字约等于 1~2 个 token。

例如：

```
"你好世界" 可能被切分为 ["你好", "世界"] 或 ["你", "好", "世", "界"]
```

token 数量直接影响：调用成本、上下文窗口占用、响应速度。

### 1.2 什么是 Prompt / 提示词？

#### 1.2.1 提示词就是给模型的输入

你发给模型的文字就是 prompt。好的 prompt 能显著提升回答质量。项目中很多地方都在构造 prompt，例如 `core/agents/planner.py` 里的：

```python
system_prompt = """你是一个任务规划专家。请将用户的需求拆解为可执行的步骤。"""
```

这里的 `system_prompt` 就是告诉模型“你现在扮演什么角色、要遵守什么规则”。

#### 1.2.2 提示词的常见角色

在 OpenAI/通义千问等对话模型中，消息通常分为三种角色：

- **system**：系统指令，设定模型身份和行为规则；
- **user**：用户输入；
- **assistant**：模型的回答；
- **tool**：工具执行结果（Function Calling 场景）。

例如 `core/agent.py` 中的对话历史：

```python
self.messages = [
    {"role": "system", "content": "你是一个智能文档任务助手..."},
    {"role": "user", "content": "Python 中列表和元组有什么区别？"},
    {"role": "assistant", "content": "..."},
]
```

### 1.3 API 与通义千问

#### 1.3.1 什么是 API？

API（Application Programming Interface，应用程序接口）就是**程序之间互相通信的约定**。你可以把 API 想象成餐厅菜单：你按菜单点菜（发送请求），厨房做菜（服务器处理），然后服务员把菜端上来（返回响应）。

在 `ai-demos` 中，代码通过调用通义千问的 API 来使用大模型能力，而不需要自己训练模型。

#### 1.3.2 通义千问（Qwen）与 DashScope

- **通义千问（Qwen）**：阿里云开发的大语言模型系列，例如 `qwen-turbo`。
- **DashScope**：阿里云提供的大模型服务平台，相当于“贩卖 API 调用额度”的窗口。
- **API Key**：一串密钥，用来证明“是谁在调用 API”。项目里放在 `.env` 文件中，代码通过 `DASHSCOPE_API_KEY` 读取。

#### 1.3.3 项目中如何调用模型？

看 `core/llm.py`：

```python
import dashscope
dashscope.api_key = self.api_key
response = dashscope.Generation.call(
    model=self.model,
    messages=messages,
    tools=tools,
    result_format="message",
)
```

- `dashscope.Generation.call()`：调用文本生成接口；
- `model`：指定模型版本；
- `messages`：对话历史；
- `tools`：可选，声明可用工具；
- `result_format="message"`：要求返回标准消息格式。

### 1.4 Python 虚拟环境与依赖管理

#### 1.4.1 为什么需要虚拟环境？

不同 Python 项目可能依赖不同版本的库。虚拟环境（Virtual Environment）能为每个项目创建独立的“沙盒”，避免版本冲突。

项目中的 `venv/` 目录就是一个虚拟环境。

#### 1.4.2 requirements.txt

`requirements.txt` 列出了项目所需的所有 Python 包及其最低版本：

```text
langchain>=1.0.0
fastapi>=0.110.0
uvicorn>=0.30.0
...
```

安装命令：

```bash
pip install -r requirements.txt
```

### 1.5 环境变量与 .env

#### 1.5.1 什么是环境变量？

环境变量是操作系统层面的“配置项”，程序运行时读取。把敏感信息（如 API Key）放在环境变量里，而不是直接写进代码，是安全好习惯。

#### 1.5.2 .env 文件

`.env` 文件用来集中存放环境变量。项目中的 `.env.example` 是模板：

```text
DASHSCOPE_API_KEY=your_key_here
LLM_MODEL=qwen-turbo
```

代码中通过 `python-dotenv` 加载：

```python
from dotenv import load_dotenv
load_dotenv()

import os
api_key = os.environ.get("DASHSCOPE_API_KEY")
```

**注意**：`.env` 通常会被 `.gitignore` 排除，不会上传到 GitHub，避免泄露密钥。

### 1.6 Web 基础：HTTP、REST API、FastAPI

#### 1.6.1 HTTP 请求与响应

浏览器和服务器之间通过 HTTP 协议通信。一次请求包括：

- **方法（Method）**：GET（获取）、POST（提交）、DELETE（删除）等；
- **URL**：请求地址；
- **Headers**：附加信息，如 Content-Type；
- **Body**：请求体，POST 时携带数据。

响应包括：

- **状态码**：200 成功、404 未找到、500 服务器错误；
- **Headers**：响应头；
- **Body**：响应体，通常是 JSON 或 HTML。

#### 1.6.2 REST API

REST 是一种设计风格，把网络上的资源用 URL 表示，用 HTTP 方法操作资源。例如：

```
GET  /users      获取用户列表
POST /users      创建用户
GET  /users/1    获取 ID 为 1 的用户
```

#### 1.6.3 FastAPI 是什么？

FastAPI 是一个现代、快速的 Python Web 框架，用来写后端 API。它的特点是：

- 基于 Python 类型注解自动校验参数；
- 自动生成交互式文档（`/docs`）；
- 性能高，支持异步。

在 `backends/rag_app/main.py` 中：

```python
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, JSONResponse

app = FastAPI(title="基于 RAG + Function Calling 的智能文档任务 Agent")

@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(content=HTML_PAGE)

@app.post("/chat")
def chat(query: str = Form(...)):
    result = agent.chat(query)
    return result
```

- `@app.get("/")`：定义 GET 请求路由；
- `@app.post("/chat")`：定义 POST 请求路由；
- `query: str = Form(...)`：从表单中读取 `query` 参数；
- `HTMLResponse`：返回 HTML 页面；
- `JSONResponse`：返回 JSON 数据。

#### 1.6.4 Uvicorn：运行 FastAPI

Uvicorn 是一个 ASGI 服务器，负责把 FastAPI 应用跑起来：

```bash
uvicorn backends.rag_app.main:app --reload --port 8001
```

- `backends.rag_app.main:app`：模块 `backends.rag_app.main` 中的 `app` 对象；
- `--reload`：代码改动后自动重启（开发模式）；
- `--port 8001`：监听 8001 端口。

### 1.7 前端基础：HTML、CSS、JavaScript

#### 1.7.1 HTML

HTML（超文本标记语言）定义网页结构。例如 `backends/rag_app/main.py` 里的 `HTML_PAGE`：

```html
<div class="chat-container">
  <div class="messages" id="messages"></div>
  <div class="input-area">
    <input type="text" id="input" placeholder="输入消息...">
    <button onclick="send()">发送</button>
  </div>
</div>
```

#### 1.7.2 CSS

CSS 控制网页样式。例如：

```css
.chat-container {
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.15);
}
```

#### 1.7.3 JavaScript

JavaScript 让网页有交互。例如前端发送消息：

```javascript
async function send() {
  const text = input.value.trim();
  const form = new FormData();
  form.append('query', text);
  const res = await fetch('chat', { method: 'POST', body: form });
  const data = await res.json();
  addMsg(data.answer, 'assistant', data.tool_calls);
}
```

- `fetch()`：浏览器内置的 HTTP 请求函数；
- `FormData`：构造表单数据；
- `await`：等待异步请求完成。

### 1.8 React、Vite、TypeScript、Tailwind CSS

#### 1.8.1 React 是什么？

React 是 Facebook 开发的 JavaScript 库，用来构建用户界面。核心思想是：

- **组件化**：把界面拆成独立可复用的小块；
- **声明式**：你描述界面“应该长什么样”，React 负责更新 DOM；
- **状态（State）**：数据变化时界面自动重新渲染。

#### 1.8.2 JSX

JSX 是 React 中类似 HTML 的语法，允许在 JavaScript 中写标签：

```jsx
function App() {
  return <h1>Hello, world!</h1>;
}
```

#### 1.8.3 Vite 是什么？

Vite 是一个现代前端构建工具，特点是：

- 开发服务器启动极快；
- 热更新（HMR）响应迅速；
- 内置对 React、TypeScript 的支持。

`frontends/portfolio/vite.config.ts`：

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: '/',
  plugins: [react()],
  server: { port: 5180 },
})
```

- `base: '/'`：部署时的基础路径；
- `plugins: [react()]`：启用 React 支持；
- `server: { port: 5180 }`：开发服务器端口。

#### 1.8.4 TypeScript

TypeScript 是 JavaScript 的超集，增加了**静态类型检查**。例如：

```typescript
function greet(name: string): string {
  return `Hello, ${name}`;
}
```

好处：在编码阶段就能发现类型错误，提高代码可维护性。

#### 1.8.5 Tailwind CSS

Tailwind 是“工具类优先”的 CSS 框架。你不需要写传统 CSS，而是在 HTML/JSX 里直接用预设好的类名：

```jsx
<div className="bg-white rounded-2xl shadow-lg p-6">
  <h1 className="text-2xl font-bold text-gray-800">标题</h1>
</div>
```

等价于写大量 CSS：`background: white; border-radius: 1rem; box-shadow: ...`。

`frontends/portfolio/tailwind.config.js` 中定义了扫描哪些文件来生成样式：

```javascript
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: { extend: {} },
  plugins: [],
}
```

### 1.9 版本控制：Git 基础

#### 1.9.1 什么是 Git？

Git 是分布式版本控制系统，用来记录代码的历史变更，方便多人协作和回滚。

#### 1.9.2 常用概念

- **仓库（Repository）**：项目的 Git 管理目录；
- **提交（Commit）**：一次代码快照；
- **分支（Branch）**：独立的代码线；
- **合并（Merge）**：把分支代码合并到一起；
- **远程（Remote）**：例如 GitHub 上的仓库。

#### 1.9.3 项目中的分支状态

根据 `docs/PROJECT-STATE.md`：

- `master`：主分支，Phase 1 已完成并合并；
- `origin/master`：GitHub 远程主分支，本地领先 36 个提交，尚未推送。

---

## 2. 进阶知识篇

### 2.1 RAG：检索增强生成

#### 2.1.1 为什么需要 RAG？

大模型训练完后，知识就固定了。如果你想让它回答**私有文档**（比如公司手册、个人笔记）或**最新资料**里的内容，需要：

1. 把这些文档切分成小块；
2. 把每块转成向量（Embedding）；
3. 存进向量数据库；
4. 用户提问时，先检索最相关的块；
5. 把检索结果作为上下文，连同问题一起喂给模型；
6. 模型基于上下文生成回答。

这就是 **RAG（Retrieval-Augmented Generation，检索增强生成）**。

#### 2.1.2 RAG 流程图解

```
文档（txt/pdf）
    │
    ▼
加载文档  ──▶  切分文本  ──▶  计算 Embedding  ──▶  存入 Chroma
                                              │
                                              ▼
用户提问  ──▶  计算问题 Embedding  ──▶  向量相似度检索  ──▶  取 Top-K 文本块
                                                              │
                                                              ▼
                                            把文本块 + 问题 拼成 Prompt
                                                              │
                                                              ▼
                                                        大模型生成回答
```

#### 2.1.3 Embedding 是什么？

Embedding 是把文本映射成**高维向量**的技术。语义相近的文本，在向量空间中的距离也近。

例如：

- “国王” 和 “皇帝” 的向量距离很近；
- “苹果” 和 “香蕉” 的距离比 “苹果” 和 “汽车” 更近。

项目中使用 `text-embedding-v3` 模型，通过 DashScope 调用：

```python
from langchain_community.embeddings import DashScopeEmbeddings

embedding = DashScopeEmbeddings(
    model="text-embedding-v3",
    dashscope_api_key=api_key,
)
```

#### 2.1.4 向量数据库 Chroma

**Chroma** 是一个开源的向量数据库，专门用来存储和检索向量。

在 `rag/vectorstore.py` 中：

```python
from langchain_community.vectorstores import Chroma

# 如果已有数据库，直接加载
if os.path.exists(persist_dir) and os.listdir(persist_dir):
    return Chroma(
        persist_directory=persist_dir,
        embedding_function=embedding,
    )

# 否则新建
return Chroma.from_documents(
    documents=docs,
    embedding=embedding,
    persist_directory=persist_dir,
)
```

- `persist_directory`：数据库持久化目录（这里是 `./chroma_db`）；
- `embedding_function`：用来把文本转成向量的函数；
- `from_documents`：从文档列表创建向量库。

#### 2.1.5 LangChain 的作用

LangChain 是一个简化 LLM 应用开发的框架，提供：

- 文档加载器（Loader）
- 文本切分器（Splitter）
- 向量存储封装
- 链式调用（Chain）
- Agent 工具集成

项目中的 `rag/` 模块大量使用了 LangChain：

```python
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
```

#### 2.1.6 文档加载与切分

**加载**：`rag/loader.py`

```python
from langchain_community.document_loaders import TextLoader
loader = TextLoader(path, encoding="utf-8")
return loader.load()
```

**切分**：`rag/splitter.py`

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # 每块最多 500 字符
    chunk_overlap=50,      # 块与块之间重叠 50 字符
    separators=["\n\n", "\n", " ", ""],
)
return splitter.split_documents(docs)
```

为什么要切分？

- 模型上下文窗口有限；
- 一次性塞入整本书会超出 token 限制；
- 切分后只检索最相关的小块，提高精度。

为什么要重叠？

- 避免关键信息正好被切到两块边界上而丢失上下文。

#### 2.1.7 检索：相似度搜索

`rag/retriever.py`：

```python
def retrieve(vectorstore, query: str, k: int = 3):
    return vectorstore.similarity_search(query, k=k)
```

- `similarity_search`：把查询转成向量，然后在向量库中找最相似的 `k` 个文档块；
- `k=3`：默认返回前 3 个最相关结果。

#### 2.1.8 RAG 在项目中如何被封装成工具？

`core/rag_tool.py` 把整个 RAG 流程封装成 `search_docs` 函数，注册到 Agent 的工具列表里：

```python
class RAGTool:
    def __init__(self, docs_path, vector_db_dir):
        self._init_vectorstore()

    def search(self, query: str, top_k: int = 3) -> str:
        docs = retrieve(self.vectorstore, query, k=top_k)
        # 格式化返回文本片段
        ...
```

然后在 `backends/rag_app/main.py` 中：

```python
from core.rag_tool import init_rag_tool, search_docs
from core.tools import TOOL_MAP

init_rag_tool()
TOOL_MAP["search_docs"] = search_docs
```

这样 Agent 就能像调用普通函数一样调用 `search_docs` 了。

### 2.2 Function Calling：让模型“动手”

#### 2.2.1 什么是 Function Calling？

Function Calling（函数调用）是 OpenAI、通义千问等模型支持的一种能力：

> 你向模型描述一组可用工具（函数），模型自己判断是否需要调用、调用哪个、传入什么参数。

这样模型不仅能生成文本，还能触发真实代码执行。

#### 2.2.2 工具 Schema

每个工具都要用 JSON Schema 描述：

```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "获取指定城市的天气信息",
    "parameters": {
      "type": "object",
      "properties": {
        "city": {
          "type": "string",
          "description": "城市名称，如北京、上海"
        }
      },
      "required": ["city"]
    }
  }
}
```

- `name`：函数名；
- `description`：告诉模型这个函数是干什么的；
- `parameters`：参数结构和每个参数的含义；
- `required`：必填参数。

#### 2.2.3 工具调用循环

看 `core/agent.py` 的 `chat` 方法：

```python
for turn in range(self.max_turns):
    response = dashscope.Generation.call(..., tools=TOOLS)
    message = response.output.choices[0].message

    if message.get("tool_calls"):
        # 模型要求调用工具
        self._handle_tool_calls(message)
        continue
    else:
        # 模型直接回答
        return {"answer": message.content, ...}
```

循环逻辑：

1. 把用户问题和对话历史发给模型；
2. 模型判断是否需要工具；
3. 如果需要，返回 `tool_calls`；
4. 代码执行工具，把结果以 `role: "tool"` 的形式加回对话历史；
5. 再次调用模型；
6. 直到模型直接给出最终回答，或达到最大轮数。

#### 2.2.4 安全执行 Python

`core/tools.py` 中的 `safe_execute_python` 不是用 `eval()` 直接执行，而是用 **AST（抽象语法树）** 做受限执行：

```python
tree = ast.parse(code, mode='eval')
result = _eval_node(tree)
```

只允许白名单里的节点类型和运算符：

```python
_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ...
}
```

这样可以防止执行 `__import__('os').system('rm -rf /')` 等危险代码。

### 2.3 Agent 架构：从单体到多 Agent

#### 2.3.1 什么是 Agent？

在 AI 领域，**Agent（智能体）** 是指能感知环境、做出决策并执行动作的程序。一个 LLM Agent 通常由以下部分组成：

- **大脑**：大语言模型；
- **记忆**：对话历史；
- **工具**：可以调用的函数；
- **规划**：决定下一步做什么。

#### 2.3.2 单体 Agent

`core/agent.py` 中的 `Agent` 是单体 Agent：

- 自己维护对话历史；
- 自己决定是否调用工具；
- 自己执行工具并继续推理。

适合简单任务，逻辑集中，容易理解。

#### 2.3.3 多 Agent 协作（Nexus）

`main.py` 启动了一个多 Agent 系统：

```python
orchestrator = OrchestratorAgent(bus, llm)
planner = PlannerAgent(bus, llm)
retriever = RetrieverAgent(bus, llm)
executor = ExecutorAgent(bus, llm)
summarizer = SummarizerAgent(bus, llm)
critic = CriticAgent(bus, llm)
```

每个 Agent 负责一个专门任务：

| Agent | 职责 |
|---|---|
| **Orchestrator** | 总指挥，调度其他 Agent |
| **Planner** | 把用户需求拆成可执行步骤 |
| **Retriever** | 检索知识库（Phase 1 是 mock） |
| **Executor** | 执行工具（Phase 1 是 mock） |
| **Summarizer** | 综合结果生成最终回答 |
| **Critic** | 评估回答质量 |

#### 2.3.4 Orchestrator 的工作流程

`core/agents/orchestrator.py` 中的 `process` 方法：

1. **Plan**：让 Planner 生成执行计划；
2. **Execute**：按顺序调用 Retriever 和 Executor；
3. **Summarize**：把检索结果和工具结果交给 Summarizer 生成回答；
4. **Critique**：让 Critic 评估回答质量。

```python
async def process(self, query: str, timeout: float = 60.0) -> Dict[str, Any]:
    # Step 1: Plan
    plan_msg = await self._send_and_wait("planner", ...)
    # Step 2: Execute plan steps
    for step in session.plan:
        ...
    # Step 3: Summarize
    summary_msg = await self._send_and_wait("summarizer", ...)
    # Step 4: Critique
    critique_msg = await self._send_and_wait("critic", ...)
```

#### 2.3.5 抽象基类 BaseAgent

`core/agents/base.py` 定义了所有 Agent 的公共行为：

```python
class BaseAgent:
    def __init__(self, agent_id: str, bus: MessageBus, llm: LLMClient):
        self.agent_id = agent_id
        self.bus = bus
        self.llm = llm

    async def run(self) -> None:
        queue = self.bus.subscribe(self.agent_id)
        while self._running:
            message = await asyncio.wait_for(queue.get(), timeout=0.5)
            await self.handle_message(message)

    @abstractmethod
    async def handle_message(self, message: Message) -> None:
        pass
```

- `run()`：每个 Agent 启动后都在自己的循环里等待消息；
- `handle_message()`：子类必须实现，处理收到的消息。

### 2.4 消息总线：Agent 之间如何通信

#### 2.4.1 为什么需要消息总线？

多 Agent 之间需要互相发送消息。消息总线（Message Bus）就像一个“邮局”：每个 Agent 有一个自己的信箱（Queue），其他 Agent 可以往里面投递消息。

#### 2.4.2 实现

`core/message_bus.py`：

```python
import asyncio
from typing import Dict

class MessageBus:
    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}

    def subscribe(self, agent_id: str) -> asyncio.Queue:
        if agent_id not in self._queues:
            self._queues[agent_id] = asyncio.Queue()
        return self._queues[agent_id]

    async def publish(self, message: Message) -> None:
        if message.recipient == "broadcast":
            for queue in self._queues.values():
                await queue.put(message)
        else:
            queue = self._queues.get(message.recipient)
            if queue is None:
                queue = self.subscribe(message.recipient)
            await queue.put(message)
```

- `asyncio.Queue`：异步队列，支持 `await put()` 和 `await get()`；
- `subscribe(agent_id)`：为某个 Agent 创建/获取队列；
- `publish(message)`：把消息发给指定接收者，或广播给所有人。

#### 2.4.3 Message 数据结构

`core/message.py`：

```python
from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class Message:
    task_id: str
    sender: str
    recipient: str
    message_type: str  # task, result, plan, thought, critique, error
    payload: Dict[str, Any]
    message_id: str = field(default_factory=lambda: str(uuid4()))
    in_reply_to: Optional[str] = None
```

- `task_id`：一次用户请求的唯一标识，所有相关消息共享；
- `message_type`：消息类型，帮助接收者判断如何处理；
- `payload`：实际携带的数据。

### 2.5 asyncio：Python 异步编程

#### 2.5.1 为什么需要异步？

一个 Web 服务可能同时处理很多请求。如果每个请求都阻塞等待网络或模型返回，服务器资源会被浪费。异步编程允许程序在等待 I/O（如 API 调用）时去处理其他任务。

#### 2.5.2 核心概念

- `async def`：定义异步函数；
- `await`：等待一个异步操作完成；
- `asyncio.run()`：启动事件循环；
- `asyncio.create_task()`：并发运行多个任务；
- `asyncio.Queue`：异步队列。

例如 `main.py`：

```python
async def main():
    bus = MessageBus()
    llm = create_llm_client()
    agents = [orchestrator, planner, ...]
    tasks = [asyncio.create_task(agent.run()) for agent in agents]
    ...
    await asyncio.gather(*tasks, return_exceptions=True)

if __name__ == "__main__":
    asyncio.run(main())
```

### 2.6 质量评估：如何判断 Agent 回答好不好？

#### 2.6.1 规则评估

`eval/evaluator.py` 中基于规则快速打分：

```python
def evaluate_answer(query, answer, contexts=None):
    scores = {}
    # 正确性、相关性、完整性、安全性
    ...
    scores["overall"] = round((correctness + relevance + completeness + safety) / 4, 2)
    return scores
```

#### 2.6.2 LLM-as-a-Judge

用更强或另一个 LLM 来评估回答质量。`llm_as_judge` 函数把问题、参考答案、模型回答拼成 prompt，让模型输出 JSON 评分。

#### 2.6.3 Critic Agent

`core/agents/critic.py` 是一个专门的评估 Agent，对 Summarizer 的输出进行打分和反馈：

```python
def _rule_based_scores(self, query: str, answer: str) -> dict:
    ...
    return {
        "correctness": correctness,
        "relevance": relevance,
        "completeness": completeness,
        "safety": safety,
        "overall": overall,
    }
```

### 2.7 容器化：Docker 与 docker-compose

#### 2.7.1 什么是 Docker？

Docker 可以把应用和它依赖的环境打包成一个**容器镜像**，保证“在我电脑上能跑，在你电脑上也能跑”。

#### 2.7.2 Dockerfile

`backends/rag_app/Dockerfile` 示例：

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "backends.rag_app.main:app", "--host", "0.0.0.0", "--port", "8001"]
```

- `FROM`：基础镜像；
- `WORKDIR`：工作目录；
- `COPY`：把本地文件复制到镜像里；
- `RUN`：构建时执行命令；
- `CMD`：容器启动时执行的命令。

#### 2.7.3 docker-compose

`deploy/docker-compose.yml` 用来自动化启动多个容器：

```yaml
services:
  rag:
    build:
      context: ..
      dockerfile: backends/rag_app/Dockerfile
    env_file: ../.env
    expose: ["8001"]

  nginx:
    image: nginx:1.27-alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
```

- `services`：要运行的容器；
- `build`：从 Dockerfile 构建镜像；
- `image`：直接使用已有镜像；
- `ports`：把容器端口映射到宿主机；
- `volumes`：挂载本地文件/目录到容器里；
- `depends_on`：指定启动顺序。

### 2.8 Nginx：反向代理与静态托管

#### 2.8.1 反向代理

Nginx 可以把外部请求转发到内部不同服务。例如：

```nginx
location /rag/ {
    proxy_pass http://rag:8001/;
}

location /fc/ {
    proxy_pass http://fc:8002/;
}
```

- 用户访问 `http://localhost/rag/chat`；
- Nginx 去掉 `/rag/` 前缀，转发到 `http://rag:8001/chat`。

#### 2.8.2 静态文件托管

Nginx 也可以直接返回 HTML/CSS/JS 文件：

```nginx
location / {
    root /usr/share/nginx/html;
    try_files $uri $uri/ /index.html;
}
```

这对应 `frontends/portfolio/dist` 目录，即 React 打包后的产物。

### 2.9 Monorepo：单仓库多项目

#### 2.9.1 什么是 Monorepo？

Monorepo 是把多个相关项目放在同一个 Git 仓库里管理。`ai-demos` 就是一个 monorepo：

```
ai-demos/
├── backends/      # Python 后端服务
├── frontends/     # React 前端项目
├── deploy/        # 部署配置
├── core/          # 共享的 Agent 核心代码
├── rag/           # 共享的 RAG 模块
├── eval/          # 共享的评估模块
└── tests/         # 测试
```

#### 2.9.2 好处

- 代码复用：`core/`、`rag/` 可以被多个后端共享；
- 版本一致：前后端改动可以一次提交、一次 review；
- 统一部署：`docker-compose.yml` 能一次性拉起整个系统。

### 2.10 测试基础

#### 2.10.1 单元测试

单元测试是对代码最小单元（函数、类）的自动化测试。项目中 `tests/test_tools.py`：

```python
from core.tools import safe_execute_python, read_file, list_files

def test_safe_execute_python():
    assert safe_execute_python("2 + 3 * 4") == "14"
    assert safe_execute_python("__import__('os').system('ls')").startswith("Error:")
```

- `assert`：断言，条件不满足时测试失败；
- `pytest`：更强大的测试框架，支持自动发现测试函数。

#### 2.10.2 为什么写测试？

- 验证代码行为是否符合预期；
- 后续改代码时防止回退；
- 作为代码使用示例。

---

## 3. 项目代码走读

### 3.1 启动入口

- **命令行多 Agent 版**：`main.py` → 启动 Nexus 的 Orchestrator/Planner/Retriever/Executor/Summarizer/Critic。
- **Web RAG 版**：`backends/rag_app/main.py` → FastAPI + 单体 Agent + RAG 工具。
- **Web FC 版**：`backends/fc_app/main.py` → FastAPI + 单体 Function Calling Agent。

### 3.2 数据流示例（以 RAG Web 版为例）

1. 用户打开 `http://127.0.0.1:8080/rag/`，Nginx 返回 `backends/rag_app/main.py` 里的 HTML 页面；
2. 用户输入问题，前端 JS 用 `fetch` 向 `/rag/chat` 发 POST 请求；
3. Nginx 把请求转发到 `rag` 容器的 8001 端口；
4. `Agent.chat()` 调用通义千问 API；
5. 模型判断需要 `search_docs`，代码执行 RAG 检索；
6. 检索结果加入对话历史，再次调用模型；
7. 模型生成最终回答，返回给前端显示。

### 3.3 关键文件索引

| 文件 | 作用 |
|---|---|
| `core/config.py` | 读取环境变量配置 |
| `core/llm.py` | 统一封装 LLM 调用，支持 qwen/openai |
| `core/agent.py` | 单体 Function Calling Agent |
| `core/tools.py` | 工具函数与 JSON Schema |
| `core/rag_tool.py` | 把 RAG 封装成 `search_docs` 工具 |
| `core/message_bus.py` | 多 Agent 异步消息总线 |
| `core/agents/orchestrator.py` | 多 Agent 调度器 |
| `rag/loader.py` | 文档加载 |
| `rag/splitter.py` | 文本切分 |
| `rag/vectorstore.py` | Chroma 向量库管理 |
| `rag/retriever.py` | 相似度检索 |
| `eval/evaluator.py` | 回答质量评估 |
| `deploy/docker-compose.yml` | 容器编排 |
| `deploy/nginx/nginx.conf` | Nginx 反向代理配置 |

---

## 4. 常见术语表

| 术语 | 解释 |
|---|---|
| LLM | 大语言模型 |
| RAG | 检索增强生成 |
| Function Calling | 模型调用外部函数的能力 |
| Embedding | 把文本变成向量的表示 |
| Vector Store | 存储和检索向量的数据库 |
| Agent | 能感知、决策、行动的智能体 |
| Prompt | 给模型的输入提示 |
| Token | 模型处理文本的基本单位 |
| AsyncIO | Python 异步 I/O 框架 |
| FastAPI | Python Web 框架 |
| React | 前端 UI 库 |
| Vite | 前端构建工具 |
| Tailwind CSS | 工具类 CSS 框架 |
| TypeScript | 带类型的 JavaScript |
| Docker | 容器化平台 |
| docker-compose | 多容器编排工具 |
| Nginx | Web 服务器/反向代理 |
| Monorepo | 单仓库多项目管理方式 |
| LLM-as-a-Judge | 用 LLM 评估 LLM 输出 |

---

## 5. 学习路径建议

### 5.1 如果你是完全新手

按这个顺序学习：

1. Python 基础语法（变量、函数、类、模块）；
2. HTTP 与 Web 基础；
3. 学习调用一次通义千问 API，理解 prompt 和 response；
4. 学习 FastAPI，写一个“ echo 服务”；
5. 学习 HTML/CSS/JS 基础；
6. 学习 React + Vite，做一个简单计数器页面；
7. 回头看 `ai-demos` 代码，理解它是怎么把这些拼起来的。

### 5.2 如果你已有 Python/Web 基础

按这个顺序深入：

1. 学习 RAG 全流程，动手用 LangChain + Chroma 做一个知识库问答；
2. 学习 Function Calling，让模型能调用你自己写的函数；
3. 学习 asyncio 和消息队列，理解多 Agent 通信；
4. 学习 Docker 和 docker-compose，把服务容器化；
5. 学习 Nginx 反向代理，把多个服务统一暴露到一个域名下；
6. 研究更复杂的多 Agent 框架，如 LangGraph、CrewAI、AutoGen。

### 5.3 推荐动手实验

1. **最小 RAG**：用 5 行 Python 把 `docs/python_guide.txt` 加载、切分、建库、提问。
2. **最小 Function Calling**：写一个 `get_time()` 函数，让模型在需要时调用它。
3. **最小多 Agent**：在 `main.py` 基础上修改 Planner 的 prompt，看看计划怎么变化。
4. **最小 Docker**：只构建 `backends/rag_app` 镜像并运行，验证 API 可访问。

---

## 6. 进阶思考与追问

为了帮你建立更系统的理解，下面是一些可以进一步思考的问题：

1. **RAG 的局限**：如果文档块切分不好，会不会漏掉关键信息？如何优化切分策略和检索精度？
2. **Function Calling 的安全边界**：项目中 `safe_execute_python` 是 AST 白名单，但 `fc_app` 里的 `calculate` 用了 `eval`，哪个更安全？为什么？
3. **多 Agent 的调度复杂度**：如果 Planner 生成的计划有 10 步，Orchestrator 如何优雅处理并行、依赖和失败？
4. **上下文窗口限制**：当检索到很多文档块时，如何压缩或选择最相关的上下文？
5. **评估的客观性**：规则评估和 LLM-as-a-Judge 各有什么优缺点？如何设计更可靠的评估？
6. **部署与扩展**：单台服务器能支撑多少并发？如何横向扩展 RAG 后端？
7. **成本与延迟**：每次调用 LLM 都要花钱和耗时，如何缓存结果、减少重复调用？

---

## 7. 总结

`ai-demos` 是一个非常适合学习的项目，它把当前 AI/Agent 开发中的核心概念都串联了起来：

- 用大模型做推理；
- 用 RAG 解决知识滞后和幻觉；
- 用 Function Calling 让模型具备行动能力；
- 用多 Agent 分工处理复杂任务；
- 用 FastAPI + React 构建 Web 应用；
- 用 Docker + Nginx 完成本地部署。

建议你从“最小可运行单元”开始动手，每次只改一个小地方，观察输出变化。这比单纯看代码更能加深理解。

祝你学习顺利！

---

## 附录：项目演进与主题系统（2026-06 更新）

本附录记录 2026 年 6 月集中迭代的几项重要改动，帮助你理解项目当前状态。

### A.1 黑白科技风门户改版

门户从原来的浅色默认风格升级为**黑白科技风**：

- 默认主题 `mono-light`，强调高对比度、网格/噪点质感、等宽元信息字体；
- Hero 区使用 glitch 标题 + 打字机副标题 + 假终端装饰；
- WorkCard 采用纯黑白四特效选中态；
- 新增可选主题 **"监控（The Machine）"**，金色高对比 HUD 风格，灵感来自《疑犯追踪》。

相关实现：`frontends/portfolio/src/` 下的 theme 系统、MachineSkin 组件、machine-skin.css、texture.css。

### A.2 新增 Demo

- **Nexus Multi-Agent（`/nexus/`）**：Planner + Orchestrator + Critic 多 Agent 协作，SSE 流式打字机回显；
- **DocHub（`/doctomd/`）**：Markdown 转 HTML 文档站，支持上传、本地路径转换、密码保护、在线浏览；
- **IconForge（`/iconforge/`）**：图标净化器，支持位图转矢量（potrace）、去除白边、彩色转黑。

### A.3 Demo 后端主题同步机制

为了让每个 demo 内部 UI 跟随门户主题，采用了**同源 iframe + localStorage + storage 事件**的方案：

1. 门户切换主题时调用 `localStorage.setItem('ai-demos-theme', theme)`；
2. 同源的 iframe 文档会自动收到 `storage` 事件；
3. iframe 内脚本读取新主题并设置 `document.documentElement.setAttribute('data-demo-theme', theme)`；
4. 每个后端的 HTML/CSS 使用统一的 `--d-*` token 调色板，根据 `data-demo-theme` 自动变色。

该机制无需 postMessage、无需刷新页面，且对现有后端侵入很小。

### A.4 LLM 出口切换：DeepSeek + Jina

生产环境从大陆 DashScope 切换到：

- **DeepSeek**（`deepseek-chat`，OpenAI 兼容接口）处理聊天/Agent 推理；
- **Jina**（`api.jina.ai`）处理 RAG embedding。

动机：服务器位于首尔，DeepSeek 与 Jina 从海外均可稳定访问。切换过程中发现并修复了 `safe_execute_python` 的描述/报错问题，避免模型发送整段程序导致死循环。

### A.5 图标清洗：从位图描摹到干净 SVG

IconForge 解决了一个实际工程问题：从网上下载的线性图标是位图，用工具描摹后会得到"带白边/脏路径"的 SVG。清洗流程：

1. **位图转矢量**：Pillow 裁剪内容 → 二值化 → potrace 描摹；
2. **去除白边**：按亮度阈值剥离近白路径，并紧贴 viewBox；
3. **彩色转黑**：统一转为 `#171817` 深色，保证在门户各主题下可见。

这套流程也被用来处理门户首页的 demo 线性图标。

### A.6 如何继续学习

如果你想动手复现，建议按这个顺序：

1. 本地跑通 `docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml up -d --build`；
2. 在浏览器切换主题，观察各 demo iframe 颜色变化；
3. 打开 `backends/iconforge_app/templates/home.html` 和 `backends/md_converter_app/templates/base.html`，对比 rag/fc/nexus 的同步脚本；
4. 修改一个 token 颜色，重新构建对应容器，看变化。

> **2026-06-26 更新**：主题系统与门户视觉已经收尾。下一步优先级已调整为**优化 RAG / Function Calling Agent 的回答质量**，解决当前回答太简陋的问题。参见 `docs/PROJECT-STATE.md` 第 6 条。

