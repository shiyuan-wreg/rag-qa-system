# Docker Compose 零基础入门

> 目标：理解 Docker Compose 是什么，能用一个 YAML 文件启动多个容器。

## 1. 一句话定义

Docker Compose 是一个**多容器编排工具**，让你用一个 `docker-compose.yml` 文件定义和启动多个相互依赖的容器。

## 2. 为什么存在

一个项目通常不止一个服务。以 Kairos 为例：

- 前端门户（Nginx 托管静态文件）
- RAG 后端
- FC 后端
- Nginx 反向代理

如果手动用 `docker run` 启动每一个，要记很多命令，还要手动配置网络让它们互相通信。

Docker Compose 解决方式：把所有服务写进一个 YAML 文件，一条命令启动全部。

## 3. 安装与准备

1. 确保已安装 Git for Windows（因为后面要用 Git Bash 运行命令）。如果还没安装，先下载安装：https://git-scm.com/download/win
2. Docker Compose 随 Docker Desktop 一起安装，无需单独下载。

验证：

```bash
docker compose version
```

Expected: 输出类似 `Docker Compose version v2.x.x`

注意：旧版本使用 `docker-compose`（带连字符），新版本使用 `docker compose`（空格）。本教程使用新版命令。

## 4. 最小动手示例

创建一个练习目录，里面放两个文件：

`docker-compose.yml`：

```yaml
version: "3.8"

services:
  web:
    image: nginx:alpine
    ports:
      - "8080:80"
    volumes:
      - ./html:/usr/share/nginx/html:ro

  app:
    image: python:3.12-slim
    command: python -m http.server 8000
    ports:
      - "8000:8000"
    working_dir: /app
    volumes:
      - ./html:/app:ro
```

`html/index.html`：

```html
<!DOCTYPE html>
<html>
  <body>
    <h1>Hello from Docker Compose!</h1>
  </body>
</html>
```

启动服务：

```bash
docker compose up -d
```

Expected: 终端显示创建网络、启动容器。

查看运行状态：

```bash
docker compose ps
```

Expected: `web` 和 `app` 两个服务都显示为 `running`。

访问测试：

- 浏览器打开 http://127.0.0.1:8080，看到 Nginx 页面
- 浏览器打开 http://127.0.0.1:8000，看到 Python 目录列表

停止并删除服务：

```bash
docker compose down
```

## 5. 在 Kairos 项目里哪里用了它

- Kairos 的主编排文件是 `deploy/docker-compose.yml`。
- 它定义了所有服务：
  - `rag`、`fc`、`nexus`、`md_converter`、`iconforge` 五个后端
  - `nginx` 反向代理
  - `certbot`（SSL 证书）
- 本地启动命令：

```bash
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml up -d --build
```

- 生产部署命令：

```bash
docker compose -f deploy/docker-compose.yml up -d --build
```

## 6. 常见错误与排查

**错误 1：服务名拼写错误**
- 现象：`docker compose logs web` 提示 `no such service`
- 解决：查看 `docker-compose.yml` 中定义的服务名，区分大小写

**错误 2：端口冲突**
- 现象：`docker compose up` 提示 `Bind for 0.0.0.0:8080 failed`
- 解决：修改 `ports` 中的宿主机端口，或停止占用该端口的程序

**错误 3：`.env` 文件没加载**
- 现象：服务启动后报错缺少 API Key
- 解决：确认 `.env` 文件存在且与 `docker-compose.yml` 同目录；Compose 默认会自动读取

## 7. 自检清单

- [ ] 我能解释 Docker Compose 和 Dockerfile 的区别
- [ ] 我能写一个简单的 `docker-compose.yml`
- [ ] 我能用 `docker compose up -d` 启动多服务
- [ ] 我能用 `docker compose ps` 查看服务状态
- [ ] 我能用 `docker compose down` 停止并清理服务
- [ ] 我能在 Kairos 仓库里找到 `deploy/docker-compose.yml`

## 8. 下一步

- 学习 `docker compose logs` 查看日志
- 学习 `depends_on` 控制服务启动顺序
- 尝试用 `docker compose` 启动 Kairos 本地栈
