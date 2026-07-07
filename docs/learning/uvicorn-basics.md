# Uvicorn 零基础入门

> 目标：理解 Uvicorn 是什么，能用它启动一个 FastAPI 应用，并看懂 Kairos 中的启动命令。

## 1. 一句话定义

Uvicorn 是一个**基于 ASGI 协议的 Python Web 服务器**，专门用来运行异步 Web 框架（如 FastAPI、Starlette）。

## 2. 为什么存在

### 2.1 从 WSGI 到 ASGI

早期 Python Web 应用使用 **WSGI** 协议（如 Flask、Django 默认），它是同步的：一个请求占一个线程，处理完才能接下一个。

现代 Web 应用大量调用外部服务（数据库、API、消息队列），等待响应时线程被白白占用。**ASGI** 协议允许异步处理请求，一个线程可以同时服务多个连接，并发能力大幅提升。

### 2.2 Uvicorn 的角色

可以把 Uvicorn 理解为"发动机"：

- **FastAPI** 是"车身"：定义路由、处理业务逻辑。
- **Uvicorn** 是"发动机"：监听端口、接收请求、把请求交给 FastAPI 处理、返回响应。

没有 Uvicorn，FastAPI 应用只是代码；有了 Uvicorn，它才能对外提供 HTTP 服务。

## 3. 安装与验证

在已激活的虚拟环境中：

```bash
pip install uvicorn[standard]
```

验证：

```bash
uvicorn --version
```

Expected: 输出类似 `Running uvicorn 0.30.0 with CPython 3.12.x`

## 4. 最小动手示例

### 4.1 创建一个最小 FastAPI 应用

创建 `main.py`：

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from Uvicorn!"}
```

### 4.2 用 Uvicorn 启动

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

参数解释：
- `main:app`：从 `main.py` 中加载名为 `app` 的 FastAPI 实例。
- `--reload`：代码修改后自动重启（仅开发环境使用）。
- `--host 0.0.0.0`：监听所有网络接口，允许局域网/容器访问。
- `--port 8000`：监听 8000 端口。

打开浏览器访问 http://127.0.0.1:8000/，Expected: `{"message":"Hello from Uvicorn!"}`

### 4.3 停止服务

在终端按 `Ctrl + C`。

## 5. 核心概念

### 5.1 ASGI 应用对象

Uvicorn 要求被启动的对象是一个 **ASGI 应用**。FastAPI 实例本身就是 ASGI 应用，所以可以直接传给 Uvicorn。

```python
app = FastAPI()  # 这就是 ASGI 应用
```

### 5.2 事件循环

Uvicorn 内部维护一个事件循环（event loop），负责调度所有异步任务。你不需要手动写 `asyncio.run(...)`，Uvicorn 会帮你管理。

### 5.3 工作进程（Workers）

单进程 Uvicorn 适合开发。生产环境通常需要多个工作进程：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

`-workers 4` 启动 4 个进程，利用多核 CPU。

更常见的生产部署是用 **Gunicorn + Uvicorn Worker**：

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

Kairos 目前每个 demo 后端只用 1 个 worker，因为服务器资源有限。

## 6. 在 Kairos 中的应用

### 6.1 Dockerfile 中的启动命令

看 `backends/rag_app/Dockerfile`：

```dockerfile
CMD ["uvicorn", "backends.rag_app.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
```

含义：
- 启动 `backends/rag_app/main.py` 中的 `app`。
- 监听容器内所有接口的 8001 端口。
- 使用 1 个工作进程。

注意：Docker 中不用 `--reload`，因为镜像是只读的，代码不会改。

### 6.2 本地开发启动命令

Kairos 本地开发时，可以直接在项目根目录运行：

```bash
venv/Scripts/python.exe -m uvicorn backends.rag_app.main:app --reload --port 8001
```

或先激活虚拟环境：

```bash
source venv/Scripts/activate
uvicorn backends.rag_app.main:app --reload --port 8001
```

### 6.3 代码中内嵌启动

有些 demo 后端在文件底部写了：

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
```

这样可以直接用 `python backends/fc_app/main.py` 启动，但 Kairos 生产环境还是通过 Dockerfile 的 `uvicorn` 命令启动。

## 7. 常见错误与排查

| 错误信息 | 可能原因 | 解决方法 |
|---------|---------|---------|
| `Error: [Errno 98] Address already in use` | 端口被占用 | 换端口：`--port 8002`，或杀掉占用进程 |
| `ModuleNotFoundError: No module named 'main'` | 模块路径写错 | 确认 `main:app` 中的 `main` 对应文件名 |
| `Application startup failed` | FastAPI 应用初始化报错 | 看更上面的 traceback，通常是 import 失败 |
| `--reload 不生效` | 用了 Docker 或某些文件系统 | 开发环境直接本地运行，Docker 生产不用 reload |

## 8. 常见面试问法

- "Uvicorn 和 Gunicorn 的区别是什么？"
- "ASGI 和 WSGI 有什么区别？"
- "生产环境如何部署 Uvicorn？"
- "为什么 FastAPI 需要 Uvicorn 才能运行？"

## 9. 下一步

继续学习：

- [FastAPI 零基础入门](fastapi-basics.md)
