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
