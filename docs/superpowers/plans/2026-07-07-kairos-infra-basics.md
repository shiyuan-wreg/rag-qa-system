# Kairos 基础设施基础伴读实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 Kairos 概念地图的基础设施层节点编写 4 篇零基础、可动手的基础教程（Git / Docker / Docker Compose / Nginx）和 1 份整合练习文档，让读者能在 Windows + Git Bash 环境下操作 Kairos 项目中的这四个工具。

**Architecture:** 每篇教程采用统一 8 段结构（定义/原因/安装/最小示例/Kairos 映射/错误排查/自检清单/下一步），教程与概念地图通过反向链接集成；最终用一份整合练习把四个工具串联起来，完成 Kairos 本地栈启动。

**Tech Stack:** Markdown 文档，无需代码依赖；涉及命令在 Windows + Git Bash + Docker Desktop 环境下运行。

## Global Constraints

- 所有教程文件位于 `docs/learning/` 目录
- 每篇教程必须包含 8 个部分：一句话定义、为什么存在、安装与准备、最小动手示例、在 Kairos 项目里哪里用了它、常见错误与排查、自检清单、下一步
- 每篇教程必须包含至少 1 个不依赖 Kairos 项目的独立最小示例
- 所有命令必须适配 Windows + Git Bash 环境
- 安装步骤必须假设读者是零基础（没有预装 Git、Docker 等）
- Kairos 映射必须引用仓库中的真实文件/配置
- 概念地图对应节点的"推荐学习资源"字段必须反向链接到基础教程
- 整合练习必须让读者能把 Kairos 本地栈跑起来并访问 `http://127.0.0.1:8080`
- 每次 Task 完成后独立提交；最终推送 `origin/master`

---

## File Structure

- **Create:** `docs/learning/git-basics.md`
  - 负责：Git 零基础教程
- **Create:** `docs/learning/docker-basics.md`
  - 负责：Docker 零基础教程
- **Create:** `docs/learning/docker-compose-basics.md`
  - 负责：Docker Compose 零基础教程
- **Create:** `docs/learning/nginx-basics.md`
  - 负责：Nginx 零基础教程
- **Create:** `docs/learning/kairos-infra-lab.md`
  - 负责：四工具整合练习
- **Modify:** `docs/learning/kairos-concept-map.md`
  - 负责：在 Git、Docker、Docker Compose、Nginx 节点的"推荐学习资源"字段添加反向链接

---

## Task 1: 编写 Git 零基础教程

**Files:**
- Create: `docs/learning/git-basics.md`

**Interfaces:**
- Consumes: design doc 中的统一 8 段结构
- Produces: 可独立阅读的 Git 入门教程

- [ ] **Step 1: 创建文件并写入标题与元信息**

```markdown
# Git 零基础入门

> 目标：理解 Git 是什么，能在 Windows + Git Bash 里完成最基本的版本控制操作。
```

- [ ] **Step 2: 写入"一句话定义"和"为什么存在"**

```markdown
## 1. 一句话定义

Git 是一个**分布式版本控制系统**，帮你保存代码每一次修改的历史，并支持多人协作。

## 2. 为什么存在

没有 Git 时，你想保存代码的旧版本，只能手动复制文件夹：

```
project_v1/
project_v2_final/
project_v2_final_really/
```

问题：
- 不知道每个版本改了什么
- 改错了无法快速回退
- 多人同时改一个文件会互相覆盖

Git 解决方式：每次修改都生成一个"快照"（commit），记录修改内容、作者、时间和说明；多个开发者各自在本地工作，最后把修改合并到一起。
```

- [ ] **Step 3: 写入"安装与准备"**

```markdown
## 3. 安装与准备

1. 下载 Git for Windows：https://git-scm.com/download/win
2. 安装时保持默认选项即可。
3. 安装完成后，在开始菜单找到 **Git Bash** 并打开。
4. 验证安装：

```bash
git --version
```

Expected: 输出类似 `git version 2.45.0.windows.1`

5. 配置你的名字和邮箱（会出现在每次提交里）：

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"
```
```

- [ ] **Step 4: 写入"最小动手示例"**

```markdown
## 4. 最小动手示例

在桌面上创建一个练习目录：

```bash
cd /c/Users/$USER/Desktop
mkdir git-practice
cd git-practice
git init
```

Expected: `Initialized empty Git repository in ...`

创建一个文件并提交：

```bash
echo "hello git" > readme.txt
git status
```

Expected: `readme.txt` 显示为 `Untracked files`。

把文件加入暂存区并提交：

```bash
git add readme.txt
git commit -m "first commit: add readme"
git log --oneline
```

Expected: 输出一条提交记录，包含短 SHA 和提交信息。

修改文件再提交一次：

```bash
echo "another line" >> readme.txt
git add readme.txt
git commit -m "second commit: append line"
git log --oneline
```

Expected: 现在有两条提交记录。
```

- [ ] **Step 5: 写入"在 Kairos 项目里哪里用了它"**

```markdown
## 5. 在 Kairos 项目里哪里用了它

- 整个 Kairos 仓库就是一个 Git 仓库，根目录下的 `.git/` 文件夹保存所有历史。
- 远程仓库地址在仓库根目录运行 `git remote -v` 可看到：`https://github.com/shiyuan-wreg/rag-qa-system.git`
- `deploy/PRODUCTION.md` 中的生产部署流程包含服务器执行 `git pull origin master`。
- 品牌重塑分支 `feat/kairos-rebrand` 已合并到 `master`，通过 `git log --oneline` 可以看到这段历史。
```

- [ ] **Step 6: 写入"常见错误与排查"**

```markdown
## 6. 常见错误与排查

**错误 1：提交时提示 `Please tell me who you are`**
- 原因：没有配置 `user.name` 和 `user.email`
- 解决：见 Step 3 的配置命令

**错误 2：Windows 下 Git 提示 `LF will be replaced by CRLF`**
- 原因：Windows 换行符是 CRLF，Linux/macOS 是 LF，Git 自动转换时提示
- 解决：通常是无害警告；Kairos 仓库已有 `.gitattributes` 处理，可忽略

**错误 3：改完文件后 `git status` 没变化**
- 原因：可能改完没有保存文件，或者不在 Git 仓库目录下
- 解决：确认保存文件，并确认当前目录下有 `.git/` 文件夹
```

- [ ] **Step 7: 写入"自检清单"和"下一步"**

```markdown
## 7. 自检清单

- [ ] 我能解释 Git 是什么、和手动复制文件夹备份的区别
- [ ] 我能用 `git init` 创建仓库
- [ ] 我能用 `git add` + `git commit` 提交修改
- [ ] 我能用 `git log --oneline` 查看提交历史
- [ ] 我能在 Kairos 仓库里找到 `.git/` 和远程仓库地址

## 8. 下一步

- 学习 `git status`、`git diff`、`git restore` 等日常命令
- 尝试 `git branch` 和 `git merge` 理解分支合并
- 阅读 Pro Git 官方中文版
```

- [ ] **Step 8: 验证文件结构完整**

运行：

```bash
grep -c "^## " docs/learning/git-basics.md
```

Expected: `8`（8 个二级标题）

- [ ] **Step 9: 提交**

```bash
git add docs/learning/git-basics.md
git commit -m "docs(learning): add Git basics tutorial"
```

---

## Task 2: 编写 Docker 零基础教程

**Files:**
- Create: `docs/learning/docker-basics.md`

**Interfaces:**
- Consumes: design doc 中的统一 8 段结构
- Produces: 可独立阅读的 Docker 入门教程

- [ ] **Step 1: 创建文件并写入标题与元信息**

```markdown
# Docker 零基础入门

> 目标：理解 Docker 是什么，能在 Windows + Docker Desktop 里运行和构建容器。
```

- [ ] **Step 2: 写入"一句话定义"和"为什么存在"**

```markdown
## 1. 一句话定义

Docker 是一个**容器化工具**，能把应用和它的运行环境打包成一个"集装箱"（容器），保证在不同机器上运行结果一致。

## 2. 为什么存在

没有 Docker 时，部署应用常遇到这样的问题：

```
"这个程序在我电脑上能跑，怎么到你服务器上就跑不了了？"
```

原因通常是环境差异：Python 版本不同、依赖库没装、系统配置不一样。

Docker 解决方式：把应用代码 + 依赖 + 运行环境一起打包成镜像；无论在哪台机器，只要运行这个镜像，环境就一致。
```

- [ ] **Step 3: 写入"安装与准备"**

```markdown
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
```

- [ ] **Step 4: 写入"最小动手示例"**

```markdown
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
```

- [ ] **Step 5: 写入"在 Kairos 项目里哪里用了它"**

```markdown
## 5. 在 Kairos 项目里哪里用了它

- Kairos 每个 demo 后端都有 Dockerfile：
  - `backends/rag_app/Dockerfile`
  - `backends/fc_app/Dockerfile`
  - `backends/nexus_app/Dockerfile`
  - `backends/md_converter_app/Dockerfile`
  - `backends/iconforge_app/Dockerfile`
- 这些 Dockerfile 定义了每个后端运行需要什么 Python 版本、安装哪些依赖、启动命令是什么。
- 生产服务器 `/opt/kairos` 使用这些镜像运行服务。
```

- [ ] **Step 6: 写入"常见错误与排查"**

```markdown
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
```

- [ ] **Step 7: 写入"自检清单"和"下一步"**

```markdown
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
```

- [ ] **Step 8: 验证文件结构完整**

运行：

```bash
grep -c "^## " docs/learning/docker-basics.md
```

Expected: `8`

- [ ] **Step 9: 提交**

```bash
git add docs/learning/docker-basics.md
git commit -m "docs(learning): add Docker basics tutorial"
```

---

## Task 3: 编写 Docker Compose 零基础教程

**Files:**
- Create: `docs/learning/docker-compose-basics.md`

**Interfaces:**
- Consumes: design doc 中的统一 8 段结构；Task 2 中的 Docker 基础概念
- Produces: 可独立阅读的 Docker Compose 入门教程

- [ ] **Step 1: 创建文件并写入标题与元信息**

```markdown
# Docker Compose 零基础入门

> 目标：理解 Docker Compose 是什么，能用一个 YAML 文件启动多个容器。
```

- [ ] **Step 2: 写入"一句话定义"和"为什么存在"**

```markdown
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
```

- [ ] **Step 3: 写入"安装与准备"**

```markdown
## 3. 安装与准备

Docker Compose 随 Docker Desktop 一起安装，无需单独下载。

验证：

```bash
docker compose version
```

Expected: 输出类似 `Docker Compose version v2.x.x`

注意：旧版本使用 `docker-compose`（带连字符），新版本使用 `docker compose`（空格）。本教程使用新版命令。
```

- [ ] **Step 4: 写入"最小动手示例"**

```markdown
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
```

- [ ] **Step 5: 写入"在 Kairos 项目里哪里用了它"**

```markdown
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
```

- [ ] **Step 6: 写入"常见错误与排查"**

```markdown
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
```

- [ ] **Step 7: 写入"自检清单"和"下一步"**

```markdown
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
```

- [ ] **Step 8: 验证文件结构完整**

运行：

```bash
grep -c "^## " docs/learning/docker-compose-basics.md
```

Expected: `8`

- [ ] **Step 9: 提交**

```bash
git add docs/learning/docker-compose-basics.md
git commit -m "docs(learning): add Docker Compose basics tutorial"
```

---

## Task 4: 编写 Nginx 零基础教程

**Files:**
- Create: `docs/learning/nginx-basics.md`

**Interfaces:**
- Consumes: design doc 中的统一 8 段结构
- Produces: 可独立阅读的 Nginx 入门教程

- [ ] **Step 1: 创建文件并写入标题与元信息**

```markdown
# Nginx 零基础入门

> 目标：理解 Nginx 是什么，能配置简单的静态文件托管和反向代理。
```

- [ ] **Step 2: 写入"一句话定义"和"为什么存在"**

```markdown
## 1. 一句话定义

Nginx 是一个**高性能 Web 服务器和反向代理服务器**，既能托管静态网站，也能把请求转发给后端服务。

## 2. 为什么存在

一个 Web 应用通常有：

- 前端静态页面（HTML/CSS/JS）
- 多个后端 API 服务

没有 Nginx 时：
- 前端和后端要分别开不同端口访问
- 后端服务直接暴露在互联网上，不安全
- 静态文件服务性能不好

Nginx 解决方式：
- 用一个域名/端口对外提供服务
- 根据 URL 路径把请求分发给不同后端（反向代理）
- 高效托管静态文件
- 处理 HTTPS/SSL
```

- [ ] **Step 3: 写入"安装与准备"**

```markdown
## 3. 安装与准备

本教程通过 Docker 运行 Nginx，不需要在 Windows 上直接安装。

验证 Docker 可用：

```bash
docker --version
```

Expected: 已安装 Docker Desktop 并处于 running 状态。
```

- [ ] **Step 4: 写入"最小动手示例"**

```markdown
## 4. 最小动手示例

### 4.1 托管静态页面

创建练习目录和文件：

```bash
mkdir nginx-practice
cd nginx-practice
mkdir html
cat > html/index.html << 'EOF'
<!DOCTYPE html>
<html>
  <body>
    <h1>Hello from Nginx!</h1>
  </body>
</html>
EOF
```

运行 Nginx 容器：

```bash
docker run -d -p 8080:80 -v $(pwd)/html:/usr/share/nginx/html:ro --name my-nginx nginx:alpine
```

访问 http://127.0.0.1:8080，看到 `Hello from Nginx!`。

停止并删除容器：

```bash
docker stop my-nginx
docker rm my-nginx
```

### 4.2 配置反向代理

创建 `nginx.conf`：

```nginx
events {}

http {
    server {
        listen 80;

        location / {
            root /usr/share/nginx/html;
        }

        location /api/ {
            proxy_pass http://httpbin.org/;
        }
    }
}
```

运行：

```bash
docker run -d -p 8080:80 -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro --name my-nginx nginx:alpine
```

访问 http://127.0.0.1:8080/anything 会被转发到 httpbin.org。
```

- [ ] **Step 5: 写入"在 Kairos 项目里哪里用了它"**

```markdown
## 5. 在 Kairos 项目里哪里用了它

- Kairos 的 Nginx 配置文件位于 `deploy/nginx/nginx.conf`。
- 它做了几件事：
  - 托管门户静态文件（`root /usr/share/nginx/html`）
  - 把 `/rag/` 代理到 `rag` 后端服务
  - 把 `/fc/` 代理到 `fc` 后端服务
  - 把 `/nexus/` 代理到 `nexus` 后端服务
  - 把 `/doctomd/` 代理到 `md_converter` 后端服务
  - 把 `/iconforge/` 代理到 `iconforge` 后端服务
  - 监听 80 端口并 301 跳转到 443 HTTPS
- 生产服务器上，Nginx 是外部请求进入 Kairos 的唯一入口。
```

- [ ] **Step 6: 写入"常见错误与排查"**

```markdown
## 6. 常见错误与排查

**错误 1：配置文件语法错误**
- 现象：容器启动后立即退出
- 排查：查看日志 `docker logs my-nginx`
- 解决：检查 `nginx.conf` 大括号是否配对

**错误 2：路径代理不匹配**
- 现象：访问 `/rag` 404，访问 `/rag/` 正常
- 原因：Nginx 的 `location` 路径匹配带斜杠和不带斜杠规则不同
- 解决：Kairos 配置中已统一使用带斜杠路径

**错误 3：后端 502**
- 现象：Nginx 返回 502 Bad Gateway
- 原因：后端容器没启动，或 Nginx 解析不到后端 IP
- 解决：确认后端服务在 `docker-compose.yml` 中已定义并运行；必要时 `docker compose restart nginx`
```

- [ ] **Step 7: 写入"自检清单"和"下一步"**

```markdown
## 7. 自检清单

- [ ] 我能解释 Nginx 反向代理的作用
- [ ] 我能用 Docker 启动 Nginx 并托管静态页面
- [ ] 我能写一个简单的 `nginx.conf` 配置反向代理
- [ ] 我能理解 Kairos 中 `/rag/`、`/fc/` 等路径是怎么代理的

## 8. 下一步

- 学习 `location` 匹配规则
- 学习 HTTPS/SSL 配置
- 阅读 Nginx 官方 Beginner's Guide
```

- [ ] **Step 8: 验证文件结构完整**

运行：

```bash
grep -c "^## " docs/learning/nginx-basics.md
```

Expected: `8`

- [ ] **Step 9: 提交**

```bash
git add docs/learning/nginx-basics.md
git commit -m "docs(learning): add Nginx basics tutorial"
```

---

## Task 5: 编写整合练习

**Files:**
- Create: `docs/learning/kairos-infra-lab.md`

**Interfaces:**
- Consumes: Task 1-4 的四个基础教程
- Produces: 一份让读者把 Kairos 本地栈跑起来的逐步练习

- [ ] **Step 1: 创建文件并写入标题与目标**

```markdown
# Kairos 基础设施整合练习

> 目标：综合运用 Git、Docker、Docker Compose、Nginx 四个工具，把 Kairos 项目在本地跑起来。
```

- [ ] **Step 2: 写入环境准备清单**

```markdown
## 1. 环境准备

在开始之前，请确认：

- [ ] 已安装 Git for Windows，并能打开 Git Bash
- [ ] 已安装 Docker Desktop，且 Engine 处于 running 状态
- [ ] 已完成 `git-basics.md` 中的最小示例
- [ ] 已完成 `docker-basics.md` 中的最小示例
- [ ] 已完成 `docker-compose-basics.md` 中的最小示例
- [ ] 已完成 `nginx-basics.md` 中的最小示例

如未完成，请先回到对应教程练习。
```

- [ ] **Step 3: 写入 Step-by-Step 练习**

```markdown
## 2. 用 Git 获取 Kairos 代码

1. 在 Git Bash 中进入你想放项目的目录：

```bash
cd /c/Users/$USER/Desktop
```

2. 克隆仓库：

```bash
git clone https://github.com/shiyuan-wreg/rag-qa-system.git kairos
```

Expected: 下载完成后出现一个 `kairos/` 目录。

3. 进入目录并查看提交历史：

```bash
cd kairos
git log --oneline -5
```

Expected: 看到最近 5 条提交记录，包括概念地图相关提交。

## 3. 查看基础设施相关文件

1. 查看 Docker 相关文件：

```bash
ls backends/rag_app/Dockerfile
ls backends/fc_app/Dockerfile
ls deploy/docker-compose.yml
```

Expected: 三个文件都存在。

2. 查看 Nginx 配置：

```bash
ls deploy/nginx/nginx.conf
```

Expected: 文件存在。

3. 查看 `.env` 文件是否存在：

```bash
ls -la .env
```

Expected: `.env` 文件存在（如果没有，需要创建并填入 API Key，见 `deploy/README.md`）。

## 4. 构建并启动 Kairos

1. 构建前端：

```bash
bash deploy/build-frontends.sh
```

Expected: 命令执行完成，生成 `frontends/portfolio/dist/` 等目录。

2. 启动本地栈：

```bash
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml up -d --build
```

Expected: 命令执行时间较长，最终所有服务都处于 `Started` 状态。

3. 查看运行状态：

```bash
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml ps
```

Expected: `nginx`、`rag`、`fc`、`nexus` 等服务都显示为 `running`。

## 5. 验证 Nginx 反向代理

1. 访问门户首页：

浏览器打开 http://127.0.0.1:8080

Expected: 看到 Kairos 门户首页。

2. 验证 RAG 后端代理：

浏览器打开 http://127.0.0.1:8080/rag/

Expected: 看到 RAG 文档问答页面。

3. 验证 FC 后端代理：

浏览器打开 http://127.0.0.1:8080/fc/

Expected: 看到 Function Calling Agent 页面。

4. 查看 Nginx 日志：

```bash
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml logs -f nginx
```

Expected: 看到 Nginx 接收请求和转发的日志。

## 6. 查看 Git 状态

```bash
git status
```

Expected: 工作区干净，或只有构建生成的 `dist/` 等被 `.gitignore` 忽略的文件。

## 7. 关闭本地栈

```bash
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml down
```

Expected: 所有容器停止并删除。
```

- [ ] **Step 4: 写入自检清单与故障排查**

```markdown
## 8. 自检清单

- [ ] 我能用 `git clone` 获取 Kairos 代码
- [ ] 我能找到 Kairos 的 Dockerfile、docker-compose.yml、nginx.conf
- [ ] 我能用 Docker Compose 启动 Kairos 本地栈
- [ ] 我能通过 http://127.0.0.1:8080 访问门户
- [ ] 我能通过 `/rag/`、`/fc/` 等子路径访问后端 demo
- [ ] 我能用 `docker compose down` 关闭本地栈

## 9. 常见故障

**故障 1：本地 RAG 无法检索**
- 原因：本机直连 `api.jina.ai` 可能超时，但容器内应可访问
- 排查：`docker compose logs rag` 查看日志
- 解决：确认 `.env` 中 `JINA_API_KEY` 已配置；中国大陆可尝试在容器网络内测试连通性

**故障 2：Nginx 502**
- 原因：后端容器 IP 变化，Nginx 未重新解析
- 解决：`docker compose restart nginx`

**故障 3：前端构建失败**
- 原因：Node 依赖未安装或网络问题
- 解决：`cd frontends/portfolio && npm install` 后再运行 `build-frontends.sh`
```

- [ ] **Step 5: 写入下一步**

```markdown
## 10. 下一步

完成本练习后，你已经能用 Kairos 的基础设施了。接下来可以：

1. 深入学习后端层：Python、FastAPI、Uvicorn
2. 深入学习前端层：TypeScript、React、Vite、TailwindCSS
3. 学习 AI/Agent 层：LLM、Function Calling、RAG
```

- [ ] **Step 6: 验证文件结构完整**

运行：

```bash
grep -c "^## " docs/learning/kairos-infra-lab.md
```

Expected: `10`

- [ ] **Step 7: 提交**

```bash
git add docs/learning/kairos-infra-lab.md
git commit -m "docs(learning): add Kairos infra integration lab"
```

---

## Task 6: 更新概念地图反向链接

**Files:**
- Modify: `docs/learning/kairos-concept-map.md`

**Interfaces:**
- Consumes: Task 1-4 创建的 4 篇基础教程
- Produces: 概念地图节点与基础教程的双向链接

- [ ] **Step 1: 修改 Git 节点的推荐学习资源**

在 `docs/learning/kairos-concept-map.md` 中找到 `#### Git` 节点下的 `推荐学习资源` 字段，追加一行：

```markdown
- 零基础入门：[docs/learning/git-basics.md](git-basics.md)
```

- [ ] **Step 2: 修改 Docker 节点的推荐学习资源**

在 `#### Docker` 节点下的 `推荐学习资源` 字段追加：

```markdown
- 零基础入门：[docs/learning/docker-basics.md](docker-basics.md)
```

- [ ] **Step 3: 修改 Docker Compose 节点的推荐学习资源**

在 `#### Docker Compose` 节点下的 `推荐学习资源` 字段追加：

```markdown
- 零基础入门：[docs/learning/docker-compose-basics.md](docker-compose-basics.md)
```

- [ ] **Step 4: 修改 Nginx 节点的推荐学习资源**

在 `#### Nginx` 节点下的 `推荐学习资源` 字段追加：

```markdown
- 零基础入门：[docs/learning/nginx-basics.md](nginx-basics.md)
```

- [ ] **Step 5: 验证链接已添加**

运行：

```bash
grep -c "docs/learning/git-basics.md" docs/learning/kairos-concept-map.md
grep -c "docs/learning/docker-basics.md" docs/learning/kairos-concept-map.md
grep -c "docs/learning/docker-compose-basics.md" docs/learning/kairos-concept-map.md
grep -c "docs/learning/nginx-basics.md" docs/learning/kairos-concept-map.md
```

Expected: 每条命令都输出 `1`。

- [ ] **Step 6: 提交**

```bash
git add docs/learning/kairos-concept-map.md
git commit -m "docs(learning): link infra nodes to basic tutorials"
```

---

## Task 7: 最终检查与推送

**Files:**
- Read-only review: `docs/learning/git-basics.md`
- Read-only review: `docs/learning/docker-basics.md`
- Read-only review: `docs/learning/docker-compose-basics.md`
- Read-only review: `docs/learning/nginx-basics.md`
- Read-only review: `docs/learning/kairos-infra-lab.md`
- Read-only review: `docs/learning/kairos-concept-map.md`

**Interfaces:**
- Consumes: Task 1-6 的所有输出
- Produces: 可推送的完整学习资产

- [ ] **Step 1: 运行结构检查**

```bash
grep -c "^## " docs/learning/git-basics.md
grep -c "^## " docs/learning/docker-basics.md
grep -c "^## " docs/learning/docker-compose-basics.md
grep -c "^## " docs/learning/nginx-basics.md
grep -c "^## " docs/learning/kairos-infra-lab.md
```

Expected: 分别输出 `8`、`8`、`8`、`8`、`10`。

- [ ] **Step 2: 检查是否有占位符**

```bash
grep -iE "TBD|TODO|implement later|fill in details" docs/learning/git-basics.md docs/learning/docker-basics.md docs/learning/docker-compose-basics.md docs/learning/nginx-basics.md docs/learning/kairos-infra-lab.md || echo "No placeholders found"
```

Expected: `No placeholders found`

- [ ] **Step 3: 查看提交历史**

```bash
git log --oneline -8
```

Expected: 看到 Task 1-6 的 6 个提交，以及之前的概念地图提交。

- [ ] **Step 4: 推送到远程**

```bash
git push origin master
```

Expected: 成功推送，无冲突。

---

## Self-Review

### Spec Coverage

| Spec 要求 | 对应 Task |
|---|---|
| 4 篇基础设施基础教程 | Task 1-4 |
| 统一 8 段结构 | Task 1-4 |
| 每篇包含独立最小示例 | Task 1-4 Step 4 |
| 每篇包含 Kairos 映射 | Task 1-4 Step 5 |
| 整合练习 | Task 5 |
| 概念地图反向链接 | Task 6 |
| 最终推送 | Task 7 |

无遗漏。

### Placeholder Scan

- 无 "TBD" / "TODO" / "implement later" / "fill in details"
- 每个 Task 的代码块包含实际可运行的命令
- 每个验证命令给出 Expected 输出

### Type Consistency

- 所有文件路径统一使用 `docs/learning/`
- 所有命令统一适配 Windows + Git Bash
- 所有链接使用相对路径 `[file](file)`

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-07-07-kairos-infra-basics.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
