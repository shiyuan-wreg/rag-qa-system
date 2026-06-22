# Nexus 开发日志

## 2026-06-18

### 今日目标

完成 Nexus Phase 1：Multi-Agent 内核 + 消息总线。

### 完成内容

- ✅ LLM Client 抽象（`core/llm.py`）
- ✅ 内存异步消息总线（`core/message_bus.py`）
- ✅ Agent 基类（`core/agents/base.py`）
- ✅ 6 个专业 Agent：Orchestrator、Planner、Retriever、Executor、Summarizer、Critic
- ✅ 命令行入口（`main.py`）
- ✅ 14 个新测试，加上 6 个 baseline 测试，共 20 个测试全部通过
- ✅ 完整设计文档和实现计划

### 关键决策

1. **默认 LLM 选择通义千问**
   - 原计划默认 Kimi，但发现 Kimi 的 coding plan 不包含 API 调用额度。
   - 决定代码支持多模型切换，默认用通义千问，后续有 Kimi 额度时可无缝切换。

2. **使用内存消息总线**
   - Phase 1 采用 `asyncio.Queue` 实现，零部署，适合个人使用。
   - 为团队版预留 Redis/RabbitMQ 替换接口。

3. **Retriever 和 Executor 使用 mock**
   - Phase 1 聚焦 Agent 协作架构，不依赖真实 RAG 和 Tool Registry。
   - Phase 2 将接入真实 Chroma 向量库和 Tool Registry。

4. **使用 worktree 隔离开发**
   - 在 `.claude/worktrees/nexus-phase1` 中完成开发，避免污染 master。
   - 最终 fast-forward 合并回 master，删除 worktree 和分支。

### 遇到的问题

1. **subagent 初始在原目录而非 worktree 工作**
   - 第一个 subagent 在原始 repo 中 commit，导致 worktree 和 master 都出现 commit。
   - 解决：reset master，cherry-pick commit 到 worktree，后续所有 subagent 都明确要求在 worktree 中执行。

2. **`asyncio.get_event_loop()` 弃用警告**
   - 在 `core/message_bus.py` 和 `core/agents/orchestrator.py` 中发现使用 `asyncio.get_event_loop()`。
   - 修复：替换为 `asyncio.get_running_loop()`。

3. **Windows 终端编码问题**
   - 测试输出中的中文和特殊字符显示为乱码。
   - 解决：测试中避免依赖中文字符串匹配，改用 "Error:" 前缀和返回值特征判断。

### 测试状态

```bash
20 passed in 4.88s
```

### 下一步计划

- Phase 2：接入真实 RAG 多集合和 Tool Registry
- Phase 3：Web UI + SSE 流式交互
- Phase 4：SQLite 记忆持久化

### 相关文档

- 设计文档：`docs/superpowers/specs/2026-06-18-nexus-personal-ai-workflow-agent-design.md`
- 实现计划：`docs/superpowers/plans/2026-06-18-phase1-multi-agent-kernel.md`
- 更新日志：`CHANGELOG.md`

---

## 2026-06-22

### 今日目标

把分散的多个 Web 项目整合为统一作品集门户「个人集成学习网站」,完成 Phase 1。

### 完成内容(分支 feat/portfolio-phase1,13 提交,20 测试通过)

- ✅ 设计 + 计划文档(spec / plan),brainstorming→writing-plans→subagent-driven 全流程
- ✅ 清理:抽离 `agent-console-ai`(独立到桌面成自有仓库)、删除 `legacy/`
- ✅ monorepo 重组:`backends/`(rag_app, fc_app)、`frontends/`(portfolio, nexus-learning-web)、`deploy/`
- ✅ React 门户外壳:首页作品网格 + 导航 + iframe demo 页 + 学习跳转 + 个人页
- ✅ Dockerfile(rag/fc)+ nginx 反代 + docker-compose,本地一键 `up`
- ✅ 本地跑通:/、/me、/rag/、/fc/、/learn/ 全 200;子路径反代验证通过

### 关键决策

1. **整合方案 C**(统一外壳 + iframe):快速上线、保留已有成果、可演进到方案 A。
2. **首页/个人页不放个人信息**(姓名/自我介绍/学校),要"普通网站"观感。
3. **agent-console-ai 独立**(鸿蒙课设):不并入,需问答能力走 HTTP API 调用沿用。
4. **纯净 Ubuntu + Docker** 部署路线(不用宝塔),练硬技能;服务器(首尔免备案)+域名已购。

### 遇到的问题与修复

1. **node_modules/dist 被误提交**(portfolio 缺 .gitignore,68MB):reset 重做成单干净提交 + 补 .gitignore + 根级安全网。
2. **子路径反代坑**:RAG/FC 内联前端往绝对 `/chat` 提交,挂 `/rag/` 下会失效;改为相对路径(chat/clear/eval)。
3. **Windows CRLF**:`.sh`/Dockerfile 被转 CRLF 会导致 bash/容器报错;加 `.gitattributes` 强制 LF。
4. **Docker Desktop 未启动 + 国内拉镜像超时**:手动启动引擎 + 预拉 nginx/python 基础镜像。
5. **agent-console-ai 残留目录被进程占用删不掉**:桌面副本已安全提交,待释放后手动删。

### 测试状态

```bash
20 passed in 4.86s
```

### 下一步

- 决定 feat/portfolio-phase1 是否合并 master
- Phase 2:Nexus Web 后端(SSE 多智能体可视化)
- Phase 3:cs-quiz 集成;Phase 4:部署首尔服务器

### 相关文档

- 交接状态:`docs/PROJECT-STATE.md`(重进先读)
- 设计:`docs/superpowers/specs/2026-06-22-personal-portfolio-integration-design.md`
- 计划:`docs/superpowers/plans/2026-06-22-portfolio-phase1-monorepo-and-shell.md`
- 学习:`docs/learning/portfolio-integration-guide.md`
- 运行:`deploy/README.md`

---

## 2026-06-22(收尾·任务 A)

### 做了什么
- 核实 git 实况:`feat/portfolio-phase1` 已**合并入 `master`**(线性/快进,分支已删),存档文档原写"尚未合并"系过期 → 已修正 `PROJECT-STATE.md`。
- `agent-console-ai/` 残留目录已是**空目录**,但被进程句柄锁定(疑 DevEco Studio),`rm`/`Remove-Item` 均报 busy;未被 git 跟踪、无功能影响,**重启后 `rm -rf` 即可清**。桌面副本 d02f65d(1515 文件)完整。

### 状态
- `master` 本地领先 `origin/master` 36 提交,**未推送**(待用户确认对外动作)。
- docker stack 仍关闭。

### 下一步
- Phase 2:Nexus Web 后端(`backends/nexus_app`,FastAPI + SSE 多智能体可视化)。
- 重启后清 `agent-console-ai/` 空残留;按需 `git push`。

---

## 2026-06-22(部署启动·未完结)

### 做了什么
- 修正部署配置,支持生产 HTTPS:
  - `deploy/docker-compose.yml`:nginx 暴露 80/443,挂载 `/etc/letsencrypt`,新增 certbot 自动续期容器
  - `deploy/nginx/nginx.conf`:HTTP→HTTPS 跳转、443 SSL 配置、转发头
  - 新增 `deploy/init-ssl.sh`:首次 certbot standalone 申请证书
- 本地提交并推送 `master` 到 GitHub:本地领先 origin 37 提交 → 已同步(`1b7fc3b`)。

### 阻塞
- 服务器 SSH 登录凭证未拿到。用户创建了密钥对,但尚未提供私钥文件(`.pem`)路径;备用方案是回阿里云控制台重置 root 密码。

### 待继续
1. 拿到 SSH 私钥文件路径或 root 密码
2. SSH 登录 8.213.145.110,安装 Docker + Docker Compose
3. `git clone` 到 `/opt/ai-demos`
4. 上传 `.env`(含 `DASHSCOPE_API_KEY`)
5. 运行 `bash deploy/init-ssl.sh hzs1716775963@126.com`
6. `bash deploy/build-frontends.sh` + `docker compose -f deploy/docker-compose.yml up -d --build`
7. 验证 `https://www.shiyuan-wreg.cloud`
