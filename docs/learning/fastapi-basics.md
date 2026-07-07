# FastAPI 零基础入门

> 目标：理解 FastAPI 是什么，能写简单的 API 接口，并看懂 Kairos 后端的路由和请求处理。

## 1. 一句话定义

FastAPI 是一个**现代、高性能的 Python Web 框架**，基于 Starlette 和 Pydantic，原生支持异步和自动生成 OpenAPI 文档。

## 2. 为什么存在

在 Kairos 中选择 FastAPI 的原因：

1. **性能高**：基于 Starlette（异步 ASGI 框架），并发能力强。
2. **开发快**：用 Python 类型声明参数，自动完成请求校验、序列化、文档生成。
3. **类型安全**：集成 Pydantic，请求/响应数据自动校验，减少运行时错误。
4. **自动生成文档**：访问 `/docs` 就能拿到交互式 API 文档。

Kairos 所有 demo 后端（rag_app、fc_app、nexus_app、md_converter_app、iconforge_app）都用 FastAPI 提供 HTTP 接口。

## 3. 安装与验证

在已激活的虚拟环境中：

```bash
pip install fastapi uvicorn[standard]
```

验证：

```python
python -c "import fastapi; print(fastapi.__version__)"
```

Expected: 输出类似 `0.111.0`

## 4. 最小动手示例

### 4.1 创建第一个 API

创建 `main.py`：

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}
```

启动：

```bash
uvicorn main:app --reload --port 8000
```

访问 http://127.0.0.1:8000/，Expected: `{"message":"Hello, FastAPI!"}`

访问 http://127.0.0.1:8000/docs，Expected: 看到自动生成的 Swagger UI 文档。

### 4.2 路径参数

```python
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

访问 http://127.0.0.1:8000/items/42，Expected: `{"item_id":42}`

如果传非数字，如 `/items/abc`，FastAPI 会自动返回 422 错误。

### 4.3 查询参数

```python
@app.get("/search/")
def search(q: str, limit: int = 10):
    return {"query": q, "limit": limit}
```

访问 http://127.0.0.1:8000/search/?q=python&limit=5，Expected: `{"query":"python","limit":5}`

### 4.4 请求体

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = None

@app.post("/items/")
def create_item(item: Item):
    return {"item_name": item.name, "item_price": item.price}
```

用 curl 测试：

```bash
curl -X POST http://127.0.0.1:8000/items/ \
  -H "Content-Type: application/json" \
  -d '{"name":"apple","price":3.5}'
```

Expected: `{"item_name":"apple","item_price":3.5}`

### 4.5 表单数据

Kairos 前端 demo 常用 `fetch` 发表单：

```python
from fastapi import Form

@app.post("/chat/")
async def chat(message: str = Form(...)):
    return {"reply": f"你说了: {message}"}
```

注意：表单接口需要 `python-multipart`：

```bash
pip install python-multipart
```

## 5. 核心概念

### 5.1 路由装饰器

FastAPI 用装饰器把 URL 路径映射到处理函数：

```python
@app.get("/users")      # 获取数据
@app.post("/users")     # 创建数据
@app.put("/users/{id}") # 全量更新
@app.delete("/users/{id}")  # 删除数据
```

这四种方法对应 HTTP 的 GET/POST/PUT/DELETE。

### 5.2 Pydantic 模型

Pydantic 是 FastAPI 的数据校验核心：

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str = None  # 可选字段
```

当请求体传入时，FastAPI 自动：
- 检查类型是否匹配
- 缺少必填字段时返回 422
- 把 JSON 转成 Python 对象

### 5.3 异步路由

如果处理函数里要等待 IO（如调用大模型 API），用 `async def`：

```python
@app.post("/chat/")
async def chat(message: str = Form(...)):
    answer = await call_llm(message)
    return {"answer": answer}
```

Kairos 后端几乎所有路由都是异步的。

### 5.4 依赖注入

FastAPI 支持依赖注入，用于复用通用逻辑（如数据库连接、认证）：

```python
from fastapi import Depends

def get_db():
    db = create_db_connection()
    try:
        yield db
    finally:
        db.close()

@app.get("/items/")
def read_items(db = Depends(get_db)):
    return db.query_items()
```

Kairos 中目前依赖注入用得较少，但 DocHub 的认证部分会用到。

## 6. 在 Kairos 中的应用

### 6.1 RAG 后端路由

看 `backends/rag_app/main.py` 简化版：

```python
from fastapi import FastAPI, Form
from core.agent import Agent

app = FastAPI()
agent = Agent(...)

@app.post("/chat")
async def chat(message: str = Form(...)):
    answer = await agent.chat(message)
    return {"answer": answer}

@app.post("/clear")
async def clear():
    agent.clear_history()
    return {"status": "ok"}
```

- `/chat` 接收表单字段 `message`，调用 Agent 生成回答。
- `/clear` 清空对话历史。

### 6.2 自动文档的价值

启动 Kairos 本地栈后，访问：

- http://127.0.0.1:8080/rag/docs
- http://127.0.0.1:8080/fc/docs
- http://127.0.0.1:8080/nexus/docs

可以看到每个后端的所有接口、参数、请求/响应格式，甚至能直接在线调试。

### 6.3 CORS 配置

Kairos 前端通过 iframe 访问后端，需要配置跨域：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

生产环境建议把 `allow_origins=["*"]` 改为具体域名。

## 7. 常见错误与排查

| 错误信息 | 可能原因 | 解决方法 |
|---------|---------|---------|
| `422 Unprocessable Entity` | 请求参数类型/格式不匹配 | 检查前端传的 Content-Type 和字段名 |
| `404 Not Found` | 路径写错或缺少前导斜杠 | 确认 `@app.get("/xxx")` 路径 |
| `TypeError: 'coroutine' object is not iterable` | async 函数没加 await | 调用异步函数时加 `await` |
| `ModuleNotFoundError: No module named 'python_multipart'` | 没装表单解析依赖 | `pip install python-multipart` |
| `/docs 空白` | 静态资源加载被拦截 | 检查浏览器控制台网络请求 |

## 8. 常见面试问法

- "FastAPI 和 Flask 的区别是什么？"
- "FastAPI 的依赖注入怎么用？"
- "Pydantic 在 FastAPI 中起什么作用？"
- "什么是 ASGI？为什么 FastAPI 基于 ASGI？"
- "FastAPI 如何自动生成 API 文档？"

## 9. 下一步

后端层基础教程已完成。你可以：

- 回到 [Kairos 技术概念地图](kairos-concept-map.md)，把 Python、Uvicorn、FastAPI 标记为已掌握
- 继续学习前端层：TypeScript / React / Vite / TailwindCSS
- 继续学习 AI 层：LLM / Function Calling / RAG
