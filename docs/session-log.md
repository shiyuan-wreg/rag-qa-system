# 会话日志（Session Log）

## 2026-07-06

### 会话目标

用户离开半小时期间，继续推进 ai-demos 项目。用户授权二选一：RAG 更新 或 Cloudflare 域名托管。

### 选择的方向

选择 **RAG P1 — 强制首轮检索（must-retrieve）**，原因：
- 是 PROJECT-STATE 中明确的 P1 下一步
- 代码在本地，Docker 已启动，可立即验证
- Cloudflare 需要账号/配置偏好确认，30 分钟内难以闭环

### 完成内容

1. 实现 `core/agent.py` 的 `require_first_tool` 机制
2. 在 `backends/rag_app/main.py` 启用 `Agent(require_first_tool="search_docs")`
3. 本地 Docker 验证通过：英文查询触发 search_docs，返回带 [1] 引用的详细回答
4. 提交并 push：`0adaab6`、`f983439`
5. 用户返回后，补写扩展版学习文档：`docs/learning/rag-must-retrieve-guide.md` + `.docx`
6. 更新 CHANGELOG.md：新增 v2.1.1

### 遇到的问题

- 本地 venv 缺 openai 包，`tests/test_agent.py` 跑不了（已知问题，容器内正常）
- Git Bash 下 curl/Python 发中文表单会乱码，属测试环境限制，非代码 bug

### 未做事项

- 生产服务器未部署
- Cloudflare 域名托管未开始
- RAG P1 后续（rerank/hybrid/top_k）未开始

### 最终状态

- `master` 最新提交：`f983439`
- 本地 Docker 全服务 running
- 所有改动已 push GitHub
