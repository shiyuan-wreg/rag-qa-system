# 本地运行

统一作品集门户(Phase 1)的本地启动方式。

## 前置条件

1. **Docker Desktop 正在运行**(Windows 上需先启动 Docker Desktop,等引擎就绪)。
2. 仓库根目录有 `.env`,且含 `DASHSCOPE_API_KEY=<你的通义千问 Key>`(从 `.env.example` 复制后填入)。

## 启动

```bash
# 1. 构建前端静态产物(portfolio + 学习站)
bash deploy/build-frontends.sh

# 2. 构建并启动所有容器
docker compose -f deploy/docker-compose.yml up -d --build

# 3. 浏览器访问
#    http://127.0.0.1:8080
```

## 访问路径

| 路径 | 内容 |
|---|---|
| `/` | 门户首页(作品卡片) |
| `/me` | 个人页 |
| `/rag/` | RAG 文档问答 demo |
| `/fc/` | Function Calling demo |
| `/learn/` | Nexus 交互式学习站 |

## 停止

```bash
docker compose -f deploy/docker-compose.yml down
```

## 常见问题

- **改了前端代码**:重新执行第 1、2 步(`build-frontends.sh` + `up --build`)。
- **改了后端代码**:执行第 2 步并带 `--build`。
- **拉取基础镜像超时**(国内网络):先手动 `docker pull nginx:1.27-alpine` 和 `docker pull python:3.12-slim` 缓存,或在 Docker Desktop 配置镜像加速器,再执行第 2 步。
- **后端报 API Key 未配置**:确认 `.env` 在仓库根目录且 `DASHSCOPE_API_KEY` 有值;compose 通过 `env_file: ../.env` 注入。
