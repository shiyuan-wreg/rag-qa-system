# Docker 零基础入门

> 目标：理解 Docker 是什么，能在 Windows + Docker Desktop 里运行和构建容器。

## 1. 一句话定义

Docker 是一个**容器化工具**，能把应用和它的运行环境打包成一个"集装箱"（容器），保证在不同机器上运行结果一致。

## 2. 为什么存在

没有 Docker 时，部署应用常遇到这样的问题：

```
"这个程序在我电脑上能跑，怎么到你服务器上就跑不了了？"
```

原因通常是环境差异：Python 版本不同、依赖库没装、系统配置不一样。

Docker 解决方式：把应用代码 + 依赖 + 运行环境一起打包成镜像；无论在哪台机器，只要运行这个镜像，环境就一致。

## 3. 安装与准备

1. 下载 Docker Desktop for Windows：https://www.docker.com/products/docker-desktop/
2. 安装过程中如果提示启用 WSL 2，选择启用。
3. 安装完成后启动 Docker Desktop，等待左下角显示 `Engine running`。
4. 打开 Git Bash，验证安装：

```bash
docker --version
docker compose version
```

Expected: 输出类似 `Docker version 26.x.x` 和 `Docker Compose version v2.x.x`

## 4. 最小动手示例

### 4.1 运行第一个容器

```bash
docker run hello-world
```

Expected: 终端打印 `Hello from Docker!`，表示 Docker 能正常拉取镜像并运行容器。

### 4.2 查看镜像和容器

```bash
docker images
docker ps -a
```

Expected: `docker images` 列出本地镜像；`docker ps -a` 列出所有容器（包括已停止的）。

### 4.3 用 Dockerfile 构建一个最小 Python 镜像

在空目录下创建两个文件：

`Dockerfile`：

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY hello.py .
CMD ["python", "hello.py"]
```

`hello.py`：

```python
print("Hello from inside a container!")
```

构建并运行：

```bash
docker build -t my-python-app .
docker run my-python-app
```

Expected: 输出 `Hello from inside a container!`

## 5. 在 Kairos 项目里哪里用了它

- Kairos 每个 demo 后端都有 Dockerfile：
  - `backends/rag_app/Dockerfile`
  - `backends/fc_app/Dockerfile`
  - `backends/nexus_app/Dockerfile`
  - `backends/md_converter_app/Dockerfile`
  - `backends/iconforge_app/Dockerfile`
- 这些 Dockerfile 定义了每个后端运行需要什么 Python 版本、安装哪些依赖、启动命令是什么。
- 生产服务器 `/opt/kairos` 使用这些镜像运行服务。

## 6. 常见错误与排查

**错误 1：Docker Desktop 没启动**
- 现象：`docker run hello-world` 提示连接失败
- 解决：打开 Docker Desktop，等待状态变为 running

**错误 2：拉取镜像超时**
- 现象：`docker pull` 或 `docker run` 长时间无响应
- 原因：中国大陆访问 Docker Hub 不稳定
- 解决：先尝试拉取常见镜像如 `python:3.12-slim` 看是否成功；可在 Docker Desktop 设置中配置镜像加速器

**错误 3：端口冲突**
- 现象：`docker run -p 8000:8000 ...` 提示端口已被占用
- 解决：换一个宿主机端口，例如 `-p 8001:8000`

## 7. 自检清单

- [ ] 我能解释 Docker 镜像和容器的区别
- [ ] 我能运行 `docker run hello-world`
- [ ] 我能用 `docker images` 和 `docker ps -a` 查看本地镜像/容器
- [ ] 我能用 Dockerfile 构建并运行一个最小 Python 应用
- [ ] 我能在 Kairos 仓库里找到后端的 Dockerfile

## 8. 下一步

- 学习 `docker run` 的常用参数：`-p`、`-v`、`-e`、`-d`
- 学习 `docker compose` 同时管理多个容器
- 阅读 Docker 官方 Get Started
