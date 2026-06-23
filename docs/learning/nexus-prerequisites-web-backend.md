# Nexus 前置技术学习文档：Web 后端基础

- **文档日期**：2026-06-23
- **适用对象**：准备理解/参与 Nexus Phase 2 开发，但尚不熟悉 Web 后端基础的同学
- **学习目标**：理解 HTTP、FastAPI、反向代理、SSE 的基本概念和用法，能看懂 Nexus 的设计和代码

---

## 写在最前面

这份文档不是设计文档，而是**学习文档**。它的目标是用最直白的方式，补齐理解 Nexus Phase 2 所需的前置 Web 后端知识。

如果你已经熟悉其中某一部分，可以直接跳过对应章节。

---

## 1. HTTP 与 REST API 基础

### 1.1 HTTP 是什么

HTTP（HyperText Transfer Protocol，超文本传输协议）是浏览器和服务器之间**请求-响应**的通信规则。

你可以把 HTTP 想象成写信：
- **请求（Request）**：你写一封信给服务器，问它要东西或告诉它做某事。
- **响应（Response）**：服务器回一封信，告诉你结果。

#### 1.1.1 HTTP 请求的组成部分

```
POST /chat HTTP/1.1
Host: www.example.com
Content-Type: application/json

{"query": "Python 列表和元组区别"}
```

各部分含义：

| 部分 | 示例 | 说明 |
|---|---|---|
| 方法（Method） | `POST` | 告诉服务器要做什么 |
| 路径（URL Path） | `/chat` | 资源地址 |
| 协议版本 | `HTTP/1.1` | 不用太关心 |
| Headers | `Host`、`Content-Type` | 元信息，说明数据格式等 |
| Body | `{"query": "..."}` | 实际传输的数据 |

#### 1.1.2 常见 HTTP 方法

| 方法 | 用途 | 例子 |
|---|---|---|
| GET | 获取资源 | 获取会话列表 |
| POST | 提交数据/创建资源 | 发送聊天消息 |
| PUT | 更新资源 | 更新会话标题 |
| DELETE | 删除资源 | 删除某个会话 |

#### 1.1.3 HTTP 响应的组成部分

```
HTTP/1.1 200 OK
Content-Type: application/json

{"answer": "列表可变，元组不可变。"}
```

| 部分 | 示例 | 说明 |
|---|---|---|
| 状态码 | `200` | 请求结果的状态 |
| Headers | `Content-Type` | 说明响应体格式 |
| Body | `{"answer": "..."}` | 实际返回的数据 |

#### 1.1.4 常见 HTTP 状态码

| 状态码 | 含义 | 场景 |
|---|---|---|
| 200 | OK，成功 | 正常返回 |
| 201 | Created，已创建 | 创建资源成功 |
| 400 | Bad Request，请求错误 | 参数格式不对 |
| 401 | Unauthorized，未授权 | 需要登录 |
| 404 | Not Found，资源不存在 | URL 写错了 |
| 500 | Internal Server Error | 服务器内部出错 |

### 1.2 什么是 API

API（Application Programming Interface，应用程序接口）是程序之间交互的约定。

举例：
- 你写了一个函数 `add(a, b)`，别人调用它就能做加法。这个函数就是你程序的 API。
- 同理，服务器暴露一个 `POST /chat` 接口，浏览器调用它就能聊天。这个 URL 就是 Web API。

### 1.3 什么是 REST API

REST（Representational State Transfer）是一种设计 Web API 的风格。核心思想：

> 用 URL 表示资源，用 HTTP 方法操作资源。

举例：

| 操作 | 方法 | URL | 含义 |
|---|---|---|---|
| 获取所有会话 | GET | `/sessions` | 读取会话集合 |
| 创建会话 | POST | `/sessions` | 在集合中新增一个 |
| 获取某个会话 | GET | `/sessions/123` | 读取 ID 为 123 的会话 |
| 更新某个会话 | PUT | `/sessions/123` | 修改 ID 为 123 的会话 |
| 删除某个会话 | DELETE | `/sessions/123` | 删除 ID 为 123 的会话 |
| 发送消息 | POST | `/chat` | 发起一次对话 |

REST API 通常返回 JSON 数据：

```json
{
  "session_id": "123",
  "messages": [
    {"role": "user", "content": "你好"},
    {"role": "assistant", "content": "你好！有什么可以帮你的？"}
  ]
}
```

### 1.4 JSON 基础

JSON（JavaScript Object Notation）是一种轻量级数据格式，Web API 中最常用。

```json
{
  "name": "Nexus",
  "version": 2,
  "is_active": true,
  "tags": ["AI", "Agent", "FastAPI"],
  "config": {
    "model": "qwen-turbo"
  }
}
```

基本规则：
- 键（key）用双引号包裹。
- 值（value）可以是字符串、数字、布尔值、数组、对象、null。
- 数组用 `[]`，对象用 `{}`。

### 1.5 动手练习

1. 打开浏览器，访问 `https://httpbin.org/get`，观察返回的 JSON。
2. 用 curl 或 Postman 测试：
   ```bash
   curl -X POST https://httpbin.org/post -H "Content-Type: application/json" -d '{"name":"test"}'
   ```

---

## 2. FastAPI 入门

### 2.1 FastAPI 是什么

FastAPI 是一个用 Python 写 Web 后端（API 服务）的框架。

特点：
- **快**：性能接近 Node.js 和 Go。
- **简单**：用 Python 类型注解就能自动生成接口文档。
- **异步支持**：原生支持 `async/await`，适合处理 SSE、高并发。

### 2.2 最小 FastAPI 程序

创建 `main.py`：

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "Hello World"}
```

运行：

```bash
pip install fastapi uvicorn
uvicorn main:app --reload
```

访问 `http://127.0.0.1:8000/`，返回：

```json
{"message": "Hello World"}
```

访问 `http://127.0.0.1:8000/docs`，还能看到自动生成的 API 文档。

### 2.3 处理 POST 请求

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class ChatRequest(BaseModel):
    query: str

@app.post("/chat")
def chat(request: ChatRequest):
    return {"answer": f"你问的是：{request.query}"}
```

请求：

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "Python 列表和元组区别"}'
```

响应：

```json
{"answer": "你问的是：Python 列表和元组区别"}
```

### 2.4 异步接口

FastAPI 支持异步函数，适合处理耗时操作（如调用 LLM）：

```python
@app.post("/chat")
async def chat(request: ChatRequest):
    # 这里可以 await 异步操作
    result = await some_async_call(request.query)
    return {"answer": result}
```

### 2.5 FastAPI 在 Nexus 中的作用

Nexus 的 Web 后端用 FastAPI 实现：
- 接收浏览器发来的 HTTP 请求。
- 调用 Orchestrator 处理用户问题。
- 通过 SSE 把 Agent 的中间过程实时推送给浏览器。

### 2.6 动手练习

1. 安装 FastAPI 和 uvicorn。
2. 写一个 `/weather` 接口，接收 `city` 参数，返回模拟天气数据。
3. 访问 `/docs`，看看自动生成的接口文档。

---

## 3. 反向代理与 nginx

### 3.1 反向代理是什么

反向代理（Reverse Proxy）是部署在服务器前端的程序，它对外暴露一个统一入口，根据请求内容转发给内部不同的后端服务。

#### 生活类比

一栋办公楼有很多部门，但对外只有一个前台电话：
- 你说"找财务部"，前台转接到财务部分机。
- 你说"找技术部"，前台转接到技术部分机。

**反向代理就是这个前台**。

#### 技术场景

ai-demos 有多个后端服务：
- `rag_app` 运行在 8001 端口
- `fc_app` 运行在 8002 端口
- `nexus_app` 运行在 8003 端口

用户不可能直接访问 `8001`、`8002`、`8003` 这些端口。反向代理（nginx）对外暴露 80/443 端口，根据 URL 路径转发：

```
用户访问 www.shiyuan-wreg.cloud/rag/chat
                │
                ▼
           nginx（反向代理）
                │
                ▼
         转发到 rag_app:8001/chat
```

### 3.2 反向代理的好处

| 好处 | 说明 |
|---|---|
| 统一入口 | 用户只用一个域名，不用记多个端口。 |
| 路径隔离 | `/rag/`、`/fc/`、`/nexus/` 互不干扰。 |
| SSL/HTTPS | 证书配在 nginx，后端服务不用管加密。 |
| 静态文件托管 | nginx 直接返回 HTML/CSS/JS，更高效。 |
| 负载均衡 | 未来某个服务可以多开实例，nginx 分配流量。 |

### 3.3 nginx 配置示例

```nginx
server {
    listen 80;
    server_name www.shiyuan-wreg.cloud;

    # 门户网站（静态文件）
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # RAG 后端
    location /rag/ {
        proxy_pass http://rag:8001/;
    }

    # FC 后端
    location /fc/ {
        proxy_pass http://fc:8002/;
    }

    # Nexus 后端（Phase 2 新增）
    location /nexus/ {
        proxy_pass http://nexus:8003/;
    }
}
```

关键配置解释：
- `listen 80`：监听 80 端口（HTTP 默认端口）。
- `server_name`：域名。
- `location /rag/`：匹配所有以 `/rag/` 开头的请求。
- `proxy_pass http://rag:8001/`：转发到 Docker 服务 `rag` 的 8001 端口。
- `root /usr/share/nginx/html`：静态文件根目录。

### 3.4 动手练习

1. 安装 nginx（本地或 WSL）。
2. 配置一个简单反向代理：访问 `http://localhost/api/` 转发到 `http://127.0.0.1:8000/`。
3. 启动一个 FastAPI 服务在 8000 端口，测试通过 nginx 访问。

---

## 4. SSE（Server-Sent Events）详解

### 4.1 SSE 是什么

SSE 是一种让服务器向浏览器**单向实时推送数据**的技术，基于普通 HTTP。

类比：
- 普通 HTTP：你问一句，服务器答一句，结束。
- SSE：你问一句，服务器边想边说，源源不断地把中间过程推给你。

### 4.2 为什么 Nexus 用 SSE

Nexus 的 Agent 处理一个问题可能需要多个步骤：
1. Planner 规划
2. Retriever 检索
3. Executor 执行工具
4. Summarizer 总结
5. Critic 评估

如果用普通 POST，用户要等所有步骤完成才能看到结果。用 SSE，用户可以**实时看到每一步**。

### 4.3 SSE 消息格式

SSE 消息是纯文本，格式固定：

```
event: 事件类型
data: JSON 数据

```

注意：
- 每条消息以**两个换行**（`\n\n`）结束。
- `event:` 行可选，没有时浏览器默认当作 `message` 事件。
- `data:` 行可以有多行。

### 4.4 完整例子

服务器推送：

```
event: planner_thought
data: {"content": "需要检索知识库"}

event: tool_call
data: {"agent": "retriever", "tool": "search_docs", "args": {"query": "Python"}}

event: tool_result
data: {"agent": "retriever", "result": [{"content": "列表可变..."}]}

event: final_answer
data: {"content": "列表可变，元组不可变。", "sources": []}

```

### 4.5 前端接收 SSE

浏览器用 `EventSource`：

```javascript
const source = new EventSource('/nexus/chat');

source.addEventListener('planner_thought', (event) => {
    const data = JSON.parse(event.data);
    console.log('Planner 思考:', data.content);
});

source.addEventListener('tool_call', (event) => {
    const data = JSON.parse(event.data);
    console.log('工具调用:', data);
});

source.addEventListener('final_answer', (event) => {
    const data = JSON.parse(event.data);
    console.log('最终回答:', data.content);
    source.close();  // 接收完毕，关闭连接
});
```

注意：`EventSource` 默认只能用 GET 方法，且不能自定义 headers。如果需要 POST，可以使用 `fetch` + `ReadableStream` 手动解析 SSE。

### 4.6 FastAPI 中实现 SSE

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json
import asyncio

app = FastAPI()

async def event_stream():
    for i in range(5):
        yield f"event: number\ndata: {json.dumps({'value': i})}\n\n"
        await asyncio.sleep(1)

@app.get("/sse")
def sse():
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

### 4.7 SSE 与 WebSocket 的区别

| 特性 | SSE | WebSocket |
|---|---|---|
| 通信方向 | 服务器 → 客户端 | 双向 |
| 协议 | 普通 HTTP | 独立协议 |
| 复杂度 | 低 | 高 |
| 自动重连 | 浏览器原生支持 | 需自己实现 |
| 适用场景 | 服务器推送流式数据 | 实时双向通信（如聊天室、游戏） |

Nexus 只需要服务器向浏览器推送，SSE 足够且更简单。

### 4.8 动手练习

1. 用 FastAPI 写一个 `/sse` 接口，每秒推送一个数字，持续 5 秒。
2. 写一个 HTML 页面，用 `EventSource` 接收并显示这些数字。

---

## 5. 这些技术在 Nexus 中的关系

把前面学过的知识串起来：

```
浏览器
  │  ① HTTP POST /nexus/chat  {"query": "..."}
  ▼
nginx（反向代理，监听 80/443）
  │  ② 根据 /nexus/ 路径转发
  ▼
FastAPI 后端（nexus_app:8003）
  │  ③ 调用 Orchestrator 处理
  ▼
Orchestrator + 多个 Agent
  │  ④ 通过 SSE 逐步返回事件
  ▼
浏览器实时看到：Planner 思考 → 工具调用 → 最终结果
```

---

## 6. 推荐学习路径

如果你是零基础，建议按这个顺序学习：

1. **HTTP / REST API**（1-2 小时）
   - 理解请求、响应、方法、状态码、JSON。
2. **FastAPI 入门**（2-3 小时）
   - 能写 GET/POST 接口，理解 async。
3. **反向代理 / nginx**（1 小时）
   - 理解路径转发和统一入口。
4. **SSE**（1 小时）
   - 理解消息格式和前端接收方式。

每学完一个，可以回看 Nexus Phase 2 设计文档的对应部分，会更容易理解。

---

## 7. 参考资源

| 主题 | 资源 |
|---|---|
| HTTP 基础 | [MDN - HTTP 概述](https://developer.mozilla.org/zh-CN/docs/Web/HTTP/Overview) |
| REST API | [RESTful API 教程 - 菜鸟](https://www.runoob.com/w3cnote/restful-style.html) |
| FastAPI | [FastAPI 官方中文文档](https://fastapi.tiangolo.com/zh/) |
| nginx 反向代理 | [nginx 反向代理入门 - 菜鸟](https://www.runoob.com/nginx/nginx-reverse-proxy.html) |
| SSE | [MDN - 使用服务器发送事件](https://developer.mozilla.org/zh-CN/docs/Web/API/Server-sent_events/Using_server-sent_events) |
| JSON | [JSON 教程 - 菜鸟](https://www.runoob.com/json/json-tutorial.html) |

---

## 8. 自测问题

1. HTTP 请求由哪几部分组成？
2. GET 和 POST 有什么区别？
3. 状态码 200、404、500 分别代表什么？
4. FastAPI 中的 `@app.get("/")` 是什么意思？
5. 反向代理的主要作用是什么？
6. SSE 消息以什么标记结束？
7. SSE 和 WebSocket 的主要区别是什么？

如果你能不查资料回答出这 7 个问题，说明本章基础已经掌握，可以继续看 Nexus Phase 2 设计文档了。
