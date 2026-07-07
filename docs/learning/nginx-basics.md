# Nginx 零基础入门

> 目标：理解 Nginx 是什么，能配置简单的静态文件托管和反向代理。

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

## 3. 安装与准备

本教程在 Windows 环境下通过 Docker 运行 Nginx，需要以下工具：

### 3.1 安装 Git for Windows

本教程中的命令使用 Git Bash 语法（例如 `cat << 'EOF'` 和 `$(pwd)`）。

1. 访问 [Git for Windows 下载页](https://git-scm.com/download/win)。
2. 下载并运行安装程序，保持默认选项即可。
3. 安装完成后，在任意文件夹空白处右键选择 **Git Bash Here** 即可打开 Git Bash。

### 3.2 安装 Docker Desktop for Windows

1. 访问 [Docker Desktop 下载页](https://www.docker.com/products/docker-desktop/)。
2. 下载并运行安装程序。
3. 安装过程中勾选 **Use WSL 2 instead of Hyper-V**（推荐启用 WSL2）。
4. 安装完成后启动 Docker Desktop，等待左下角状态变为 **Engine running**。

### 3.3 验证环境

在 Git Bash 中执行：

```bash
docker --version
docker ps
```

Expected: `docker --version` 返回版本号，`docker ps` 正常列出容器（可能为空列表），表示 Docker Desktop 正在运行。

## 4. 最小动手示例

### 4.1 托管静态页面

> 以下命令需要在 **Git Bash** 中运行（随 Git for Windows 安装）。`$(pwd)` 表示当前目录的绝对路径。

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

访问 http://127.0.0.1:8080/api/anything 会被转发到 http://httpbin.org/anything。

> Windows 下如果 volume 挂载失败，可能是因为 `$(pwd)` 返回的路径格式不被 Docker 识别。此时可尝试手动写成 Windows 路径，例如 `-v /c/Users/你的用户名/nginx-practice/nginx.conf:/etc/nginx/nginx.conf:ro`。

## 5. 在 Kairos 项目里哪里用了它

- Kairos 的 Nginx 配置文件位于 `deploy/nginx/nginx.conf`。
- 实际配置中，Nginx 会把 `/rag/`、`/fc/` 等路径前缀去掉（通过 `rewrite` 规则），再转发给后端服务。
- 它做了几件事：
  - 托管门户静态文件（`root /usr/share/nginx/html`）
  - 把 `/rag/` 代理到 `rag` 后端服务
  - 把 `/fc/` 代理到 `fc` 后端服务
  - 把 `/nexus/` 代理到 `nexus` 后端服务
  - 把 `/doctomd/` 代理到 `md_converter` 后端服务
  - 把 `/iconforge/` 代理到 `iconforge` 后端服务
  - 监听 80 端口并 301 跳转到 443 HTTPS
- 生产服务器上，Nginx 是外部请求进入 Kairos 的唯一入口。

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

## 7. 自检清单

- [ ] 我能解释 Nginx 反向代理的作用
- [ ] 我能用 Docker 启动 Nginx 并托管静态页面
- [ ] 我能写一个简单的 `nginx.conf` 配置反向代理
- [ ] 我能理解 Kairos 中 `/rag/`、`/fc/` 等路径是怎么代理的

## 8. 下一步

- 学习 `location` 匹配规则
- 学习 HTTPS/SSL 配置
- 阅读 Nginx 官方 Beginner's Guide
