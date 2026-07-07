# Kairos 基础设施整合练习

> 目标：综合运用 Git、Docker、Docker Compose、Nginx 四个工具，把 Kairos 项目在本地跑起来。

## 1. 环境准备

在开始之前，请确认：

- [ ] 已安装 Git for Windows，并能打开 Git Bash
- [ ] 已安装 Docker Desktop，且 Engine 处于 running 状态
- [ ] 已安装 Node.js LTS（npm 可用），下载地址：https://nodejs.org/
- [ ] 已完成 `git-basics.md` 中的最小示例
- [ ] 已完成 `docker-basics.md` 中的最小示例
- [ ] 已完成 `docker-compose-basics.md` 中的最小示例
- [ ] 已完成 `nginx-basics.md` 中的最小示例

如未完成，请先回到对应教程练习。

## 2. 用 Git 获取 Kairos 代码

1. 在 Git Bash 中进入你想放项目的目录：

```bash
cd /c/Users/$USER/Desktop
```

2. 克隆仓库：

```bash
git clone https://github.com/shiyuan-wreg/rag-qa-system.git kairos
```

> 如果目录 `kairos/` 已存在，请换一个名字或先删除旧目录。

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
ls deploy/nginx/nginx.local.conf
```

Expected: 文件存在。说明：本地实验通过 `deploy/docker-compose.local.yml` 覆盖了生产环境默认的 `deploy/nginx/nginx.conf`，所以实际生效的是 `nginx.local.conf`。

3. 查看 `.env` 文件是否存在：

```bash
ls -la .env
```

Expected: `.env` 文件存在（如果没有，可复制 `.env.example` 并根据说明填写 API Key）。需要关注的主要 Key 包括：`LLM_API_KEY`（DeepSeek 主Key）、`JINA_API_KEY`（用于 RAG 向量化）。旧的 `DASHSCOPE_API_KEY` 仅作为兼容兜底，当前主链路不再优先使用。

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

Expected: 至少包含 `nginx`、`rag`、`fc`、`nexus`、`md_converter`、`iconforge` 等服务的 `State` 为 `running`。

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
- 排查：`docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml logs rag` 查看日志
- 解决：确认 `.env` 中 `JINA_API_KEY` 已配置；中国大陆可尝试在容器网络内测试连通性

**故障 2：Nginx 502**
- 原因：后端容器 IP 变化，Nginx 未重新解析
- 解决：`docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml restart nginx`

**故障 3：前端构建失败**
- 原因：Node 依赖未安装或网络问题
- 解决：`cd frontends/portfolio && npm install` 后再运行 `build-frontends.sh`

## 10. 下一步

完成本练习后，你已经能用 Kairos 的基础设施了。接下来可以：

1. 深入学习后端层：Python、FastAPI、Uvicorn
2. 深入学习前端层：TypeScript、React、Vite、TailwindCSS
3. 学习 AI/Agent 层：LLM、Function Calling、RAG
