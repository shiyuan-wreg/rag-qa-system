# Kairos 基础设施基础伴读设计

> **状态：** 已确认  
> **设计日期：** 2026-07-07  
> **主题：** 为概念地图中的基础设施层节点写零基础、可动手的入门教程，并配套整合练习。

---

## 1. 问题背景

`docs/learning/kairos-concept-map.md` 已完成 16 个核心节点的 7 字段框架，但默认读者已经知道每个技术是什么。对于零基础读者（当前用户状态），存在两个鸿沟：

1. **概念鸿沟**：知道"Git 是版本控制"，但不知道 `git add` / `git commit` / `git push` 具体在做什么。
2. **操作鸿沟**：知道"Docker 是容器"，但不知道怎么在 Windows + Git Bash 里安装、运行、排查。

本设计的目标是为基础设施层 4 个节点补齐**零基础、可动手**的伴读材料。

---

## 2. 目标

- 让读者在读完 4 篇教程 + 1 份整合练习后，能在 Windows + Git Bash 环境下独立操作 Kairos 项目里的 Git/Docker/Docker Compose/Nginx。
- 每篇教程都包含：概念解释、安装准备、独立最小示例、Kairos 真实使用位置、常见错误排查、自检清单。
- 概念地图保持为索引，每篇基础教程反向链接回地图对应节点。

---

## 3. 范围

### 3.1 包含

| 技术 | 对应地图节点 | 教程文件 |
|---|---|---|
| Git | `#### Git` | `docs/learning/git-basics.md` |
| Docker | `#### Docker` | `docs/learning/docker-basics.md` |
| Docker Compose | `#### Docker Compose` | `docs/learning/docker-compose-basics.md` |
| Nginx | `#### Nginx` | `docs/learning/nginx-basics.md` |
| 整合练习 | 全部 4 个 | `docs/learning/kairos-infra-lab.md` |

### 3.2 不包含

- 后端/前端/AI 层节点（Phase 2 再补）
- 生产服务器部署（已有 `deploy/PRODUCTION.md`）
- 深入原理（如 Git 内部对象模型、Docker 内核机制、Nginx location 匹配算法细节）

---

## 4. 统一教程模板

每篇基础教程按以下 8 个部分组织：

```markdown
# Xxx 零基础入门

## 1. 一句话定义
用生活化比喻或最简短的话解释它是什么。

## 2. 为什么存在
没有它之前怎么做？它解决了什么痛点？

## 3. 安装与准备
Windows + Git Bash 环境下的安装步骤、版本确认命令。

## 4. 最小动手示例
不依赖 Kairos 项目，做一个能独立跑通的小例子。

## 5. 在 Kairos 项目里哪里用了它
对照概念地图，找到真实文件/配置/命令。

## 6. 常见错误与排查
列出 2-4 个新手最可能踩的坑和解决方法。

## 7. 自检清单
- [ ] 我能解释 Xxx 是什么
- [ ] 我能运行安装确认命令
- [ ] 我能独立完成最小示例
- [ ] 我能在 Kairos 里找到它的使用位置

## 8. 下一步
推荐阅读/练习。
```

---

## 5. 每篇教程概要

### 5.1 Git 零基础入门

- 定义：保存代码历史的时间机器 + 多人协作工具
- 安装：Git for Windows + Git Bash
- 最小示例：
  - `git init`
  - `git add`
  - `git commit -m "..."`
  - `git log --oneline`
  - `git status`
- Kairos 映射：`.git/`、`deploy/PRODUCTION.md` 中的 `git pull`
- 常见错误：LF/CRLF 警告、未配置 user.name/email、改完文件忘记 add

### 5.2 Docker 零基础入门

- 定义：把应用和运行环境打包成集装箱
- 安装：Docker Desktop for Windows
- 最小示例：
  - `docker --version`
  - `docker run hello-world`
  - `docker images`
  - `docker ps -a`
  - 用 Dockerfile 构建一个最小 Python 镜像
- Kairos 映射：`backends/rag_app/Dockerfile`、`backends/fc_app/Dockerfile`
- 常见错误：Docker Desktop 未启动、镜像拉取超时、端口冲突

### 5.3 Docker Compose 零基础入门

- 定义：用一个 YAML 文件同时启动多个容器
- 安装：随 Docker Desktop 附带
- 最小示例：
  - 写一个 `docker-compose.yml` 启动 nginx + 一个简单后端
  - `docker compose up -d`
  - `docker compose down`
  - `docker compose ps`
- Kairos 映射：`deploy/docker-compose.yml`
- 常见错误：服务名拼写错误、端口冲突、`.env` 没加载

### 5.4 Nginx 零基础入门

- 定义：高性能 Web 服务器 + 反向代理
- 安装：通过 Docker 运行 nginx 镜像
- 最小示例：
  - 启动一个 nginx 容器
  - 挂载自定义 `nginx.conf`
  - 测试静态页面访问
- Kairos 映射：`deploy/nginx/nginx.conf`
- 常见错误：配置文件语法错误、路径错误、后端 502

### 5.5 整合练习：用四个工具把 Kairos 跑起来

目标：让读者走完一遍 Kairos 本地启动的核心流程。

步骤：
1. `git clone` Kairos 仓库
2. 用 `git log --oneline` 查看最近提交
3. 用 `docker --version` / `docker compose version` 确认环境
4. 用 `docker compose -f deploy/docker-compose.yml up -d` 启动（或按 `deploy/README.md`）
5. 查看 `deploy/nginx/nginx.conf`，理解 `/rag/`、`/fc/` 等路径怎么代理
6. 访问 `http://127.0.0.1:8080` 验证
7. 用 `docker compose logs -f nginx` 看日志
8. 用 `docker compose down` 关闭

---

## 6. 与概念地图的集成

每篇基础教程写完后，在 `docs/learning/kairos-concept-map.md` 对应节点的"推荐学习资源"字段末尾追加链接：

```markdown
- **推荐学习资源**：
  - 零基础入门：[docs/learning/git-basics.md](git-basics.md)
  - 项目 `.git/` 历史与 `deploy/PRODUCTION.md`
```

这样地图仍然是入口，基础教程是深入材料。

---

## 7. 验收标准

- 4 篇教程 + 1 份整合练习全部完成并提交
- 每篇教程包含全部 8 个部分
- 每篇教程至少包含 1 个可独立运行的最小示例
- 整合练习能让读者把 Kairos 本地栈跑起来
- 概念地图对应节点已添加反向链接

---

## 8. 后续扩展

基础设施层完成后，可继续用相同模式补：
- 后端服务层：Python、FastAPI、Uvicorn、RAG、FC
- 前端门户层：TypeScript、React、TailwindCSS、Vite
- AI / Agent 能力层：LLM、Function Calling
- 通用：HTTP / REST API
