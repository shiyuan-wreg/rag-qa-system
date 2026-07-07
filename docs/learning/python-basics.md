# Python 零基础入门

> 目标：理解 Python 是什么，能在 Windows + Git Bash 里写简单脚本，并看懂 Kairos 后端代码的基本结构。

## 1. 一句话定义

Python 是一门**解释型、高级、通用编程语言**，语法接近自然语言，适合快速开发 Web 后端、数据处理、自动化脚本和 AI 应用。

## 2. 为什么存在

在 Kairos 项目里，Python 被选为后端主要语言，原因有三：

1. **生态成熟**：FastAPI、LangChain、Chroma、OpenAI SDK 等 AI 工程组件都优先支持 Python。
2. **语法简洁**：同样的功能，Python 代码通常比 Java/C++ 短很多，适合快速迭代。
3. **异步支持**：Python 3.5+ 引入 `async`/`await`，能高效处理大量并发网络请求，现代 Web 后端必备。

Kairos 中所有 demo 后端（rag_app、fc_app、nexus_app、md_converter_app、iconforge_app）和共享核心模块（core/agent.py、core/llm.py 等）都用 Python 编写。

## 3. 安装与验证

### 3.1 安装 Python

1. 访问 https://www.python.org/downloads/
2. 下载 **Python 3.12.x**（Kairos 项目使用 3.12）。
3. 安装时勾选 **"Add Python to PATH"**，然后点击 Install Now。

### 3.2 验证安装

打开 Git Bash，输入：

```bash
python --version
```

Expected: `Python 3.12.x`

如果提示找不到命令，检查安装时是否勾选了 "Add Python to PATH"，或手动把安装路径加入系统环境变量。

## 4. 最小动手示例

### 4.1 运行第一个 Python 程序

在空目录下创建 `hello.py`：

```python
print("Hello, Python!")
```

运行：

```bash
python hello.py
```

Expected: 终端打印 `Hello, Python!`

### 4.2 变量与数据类型

```python
name = "Kairos"      # 字符串
version = 1          # 整数
score = 0.95         # 浮点数
is_ready = True      # 布尔值
items = ["rag", "fc", "nexus"]  # 列表
config = {"host": "0.0.0.0", "port": 8001}  # 字典
```

要点：
- Python 不需要声明类型，变量类型由赋值决定。
- 列表用 `[]`，字典用 `{}`，元组用 `()`（不可变列表）。

### 4.3 函数

```python
def greet(name):
    return f"Hello, {name}!"

message = greet("Kairos")
print(message)
```

Expected: `Hello, Kairos!`

`f"..."` 是 f-string，用于在字符串中嵌入变量，是 Python 3.6+ 的写法。

### 4.4 类与对象

Kairos 后端大量使用类来组织代码：

```python
class Agent:
    def __init__(self, name):
        self.name = name

    def chat(self, message):
        return f"[{self.name}] {message}"

agent = Agent("RAG")
print(agent.chat("你好"))
```

Expected: `[RAG] 你好`

要点：
- `__init__` 是构造函数，创建对象时自动执行。
- `self` 代表当前对象实例，必须作为第一个参数。

### 4.5 模块与导入

当项目变大，代码会拆到多个文件。Kairos 中常见写法：

```python
from core.agent import Agent
from core.llm import LLMClient
```

含义：从 `core/agent.py` 文件中导入 `Agent` 类，从 `core/llm.py` 中导入 `LLMClient` 类。

## 5. 虚拟环境与包管理

### 5.1 为什么需要虚拟环境

Python 项目依赖各种第三方库（如 fastapi、openai、httpx）。如果所有项目都装到系统 Python 里，会互相冲突。

**虚拟环境**就是给每个项目一个独立的 Python 环境。

### 5.2 创建虚拟环境

在 Kairos 项目根目录下：

```bash
python -m venv venv
```

这会创建一个 `venv/` 目录，里面有一套独立的 Python 和 pip。

### 5.3 激活虚拟环境

Git Bash 中：

```bash
source venv/Scripts/activate
```

激活后，命令行前面会出现 `(venv)` 提示：

```bash
(venv)
```

### 5.4 安装依赖

Kairos 根目录有 `requirements.txt`，里面列出了项目需要的包：

```bash
pip install -r requirements.txt
```

### 5.5 requirements.txt 是什么

它就是一个清单，告诉 pip 要装哪些包、什么版本。例如：

```text
fastapi==0.111.0
uvicorn[standard]==0.30.0
openai==1.35.0
httpx==0.27.0
```

- `==` 表示精确版本。
- `uvicorn[standard]` 表示安装 uvicorn 及其推荐额外依赖。

### 5.6 退出虚拟环境

```bash
deactivate
```

## 6. 异步编程：async / await

### 6.1 为什么需要异步

Web 后端经常要等待网络响应（如调用大模型 API、查数据库）。如果用一个请求占满一个线程，并发能力很差。

异步编程让程序在等待 IO 时去做别的事，提高并发效率。

### 6.2 最小示例

```python
import asyncio

async def say_hello():
    await asyncio.sleep(1)
    print("Hello after 1 second")

asyncio.run(say_hello())
```

Expected: 等待 1 秒后打印 `Hello after 1 second`

要点：
- `async def` 定义异步函数。
- `await` 表示"在这里等待某个异步操作完成"。
- `asyncio.run(...)` 启动事件循环，运行最外层异步函数。

### 6.3 在 Kairos 中的应用

看 `core/llm.py` 中的简化片段：

```python
async def achat(self, messages):
    response = await self.client.chat.completions.create(...)
    return response.choices[0].message.content
```

- `achat` 是异步函数。
- `await` 等待大模型 API 返回结果。
- 等待期间，服务器可以处理其他请求。

### 6.4 常见错误

**错误 1：在普通函数里 await**

```python
def main():
    result = await some_async_function()  # 报错！
```

修正：

```python
async def main():
    result = await some_async_function()
```

**错误 2：直接调用 async 函数却不运行事件循环**

```python
say_hello()  # 返回的是一个协程对象，不会执行
```

修正：

```python
asyncio.run(say_hello())
```

## 7. Kairos 项目中的 Python 实例

### 7.1 后端入口文件结构

以 `backends/rag_app/main.py` 为例：

```python
from fastapi import FastAPI
from core.agent import Agent

app = FastAPI()
agent = Agent(...)

@app.post("/chat")
async def chat(message: str):
    answer = await agent.chat(message)
    return {"answer": answer}
```

逐行解释：
- `from fastapi import FastAPI`：导入 FastAPI 框架。
- `app = FastAPI()`：创建一个 FastAPI 应用实例。
- `@app.post("/chat")`：定义一个 POST 路由。
- `async def chat(...)`：异步处理函数。
- `return {"answer": answer}`：返回 JSON 响应。

### 7.2 共享核心模块

`core/agent.py` 中的 `Agent` 类是 Kairos 的核心：

```python
class Agent:
    def __init__(self, llm_client, tools):
        self.llm_client = llm_client
        self.tools = tools

    async def chat(self, message):
        # ...调用 LLM、处理工具调用、返回答案
```

各 demo 后端都创建自己的 `Agent` 实例，但共用同一套 `Agent` 逻辑。

## 8. 常见错误与排查

| 错误信息 | 可能原因 | 解决方法 |
|---------|---------|---------|
| `ModuleNotFoundError: No module named 'fastapi'` | 没装依赖或没激活虚拟环境 | `source venv/Scripts/activate && pip install -r requirements.txt` |
| `SyntaxError: invalid syntax` | Python 版本过低或语法写错 | 确认使用 Python 3.10+ |
| `RuntimeWarning: coroutine 'xxx' was never awaited` | async 函数没加 await | 调用处加 `await` |
| `ImportError: attempted relative import with no known parent package` | 模块导入路径问题 | 用 `python -m` 运行，或调整导入路径 |

## 9. 常见面试问法

- "Python 的 GIL 是什么？它带来了什么限制？"
- "Python 中异步编程怎么写？async/await 和线程有什么区别？"
- "什么是虚拟环境？为什么要用虚拟环境？"
- "Python 的列表和元组有什么区别？"
- "解释型语言和编译型语言有什么区别？"

## 10. 下一步

继续学习：

- [Uvicorn 零基础入门](uvicorn-basics.md)
- [FastAPI 零基础入门](fastapi-basics.md)
