# Kairos 重命名完成报告

> 完成日期：2026-07-07  
> 操作人：Claude Code (subagent-driven development)  
> 最终仓库：`C:\Users\hzs17\Desktop\kairos`  
> 最终 commit：`c2f825a`

---

## 1. 完成了什么

项目已从 `ai-demos` 全面重命名为 **Kairos**，并完成生产部署验证。

### 1.1 品牌层

- 前端门户标题改为 `Kairos`
- 导航栏品牌文本改为 `Kairos`
- Hero 副标题改为 `Kairos · Personal Workspace`
- Logo alt 文本改为 `Kairos`
- 页面 document title 统一为 `... · Kairos`

### 1.2 主题同步 key

全站主题同步 localStorage key 从 `ai-demos-theme` / `ai-demos-parallax` 统一改为 `kairos-theme` / `kairos-parallax`。

涉及文件：

- `frontends/portfolio/src/hooks/useTheme.ts`
- `frontends/portfolio/src/hooks/useMotionPreference.ts`
- `frontends/portfolio/src/main.tsx`
- `frontends/nexus-learning-web/index.html`
- `backends/rag_app/main.py`
- `backends/fc_app/main.py`
- `backends/nexus_app/templates/index.html`
- `backends/md_converter_app/converter.py`
- `backends/md_converter_app/templates/base.html`
- `backends/iconforge_app/templates/home.html`

### 1.3 部署路径

- 本地项目目录：`ai-demos/` → `kairos/`
- 生产服务器部署目录：`/opt/ai-demos` → `/opt/kairos`
- `deploy/PRODUCTION.md` 和 `deploy/phase4-workbench-deploy.sh` 已更新

### 1.4 文档与元数据

- `README.md`：项目名、本地目录说明已更新，GitHub clone URL 保持不变
- `docs/PROJECT-STATE.md`：新增「2026-07-06 品牌重命名 ✅ 已完成并验证」
- `docs/dev-log.md`：追加品牌重命名记录与验证结果
- `CHANGELOG.md`：新增 `[0.7.0]` 条目
- `docs/career/CLAUDE.md` 与 `frontends/nexus-learning-web/CLAUDE.md`：可选更新
- 历史记录中的 `ai-demos` 引用全部保留，未篡改

---

## 2. 最终状态

### 2.1 本地仓库

```
C:\Users\hzs17\Desktop\kairos
├── .git/           # 普通 git 仓库（不再是 worktree）
├── .env            # 已恢复，含 DeepSeek / Jina / DocHub 密钥
├── deploy/
├── docs/
├── frontends/
├── backends/
└── ...
```

- 当前分支：`master`
- 最新 commit：`c2f825a docs: finalize Kairos rebrand status and deployment verification`
- 远程：`origin = https://github.com/shiyuan-wreg/rag-qa-system.git`
- 工作树干净

### 2.2 生产服务器

- 部署目录：`/opt/kairos`
- 域名：`https://www.shiyuan-wreg.cloud`
- HEAD：`c2f825a`
- 7 路由全部 200：
  - `/`
  - `/rag/`
  - `/fc/`
  - `/nexus/`
  - `/doctomd/`
  - `/learn/`
  - `/iconforge/`
- RAG must-retrieve 验证通过：`search_docs` 被调用，回答含 `[1]` 引用
- `/learn/` 主题 key 验证为 `kairos-theme`

---

## 3. 操作过程摘要

| 阶段 | 关键动作 | 结果 |
|---|---|---|
| 设计 | 编写 design doc 与 implementation plan | 已提交到 `docs/superpowers/{specs,plans}/2026-07-06-kairos-rebrand*` |
| 实施 | 8 个 Task 的 subagent-driven 开发 | 全部完成并逐 task review |
| 修复 | 发现 `/learn/` 仍用旧 theme key | 已修复并重新部署 |
| 合并 | `feat/kairos-rebrand` → `master` | 已 fast-forward 合并并推送 |
| 目录 | `ai-demos/` + `kairos` worktree → 单一 `kairos/` 仓库 | 已完成 |
| 部署 | 生产服务器 pull master、build、compose up | 已完成并验证 |

---

## 4. 已知限制与后续注意

1. **本地测试套件**：本机 Python 环境缺少 `openai` 包，部分 pytest 用例无法收集/运行；Docker 容器内测试正常。这与重命名无关，是既有环境限制。

2. **未跟踪文件**：`node_modules` 在目录重建过程中丢失。如需本地开发，进入 `frontends/portfolio` 和 `frontends/nexus-learning-web` 重新运行 `npm install`。

3. **iframe 主题同步**：自动化验证已确认 `/learn/` 使用 `kairos-theme`；浏览器端实时切换效果建议手动打开 `https://www.shiyuan-wreg.cloud` 切换主题确认。

4. **旧文档路径**：历史 spec/plan/learning 文档中仍有 `ai-demos` 和 `/opt/ai-demos` 引用，属于历史记录， intentionally 保留。

5. **GitHub 仓库名**：仍为 `rag-qa-system`，未改变。clone URL 也保持不变。

---

## 5. 如何继续工作

以后直接在这个目录操作：

```bash
cd C:/Users/hzs17/Desktop/kairos
```

常用命令：

```bash
# 本地开发前端
cd frontends/portfolio
npm install
npm run dev

# 本地起全栈
bash deploy/build-frontends.sh
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml up -d --build

# 生产部署
ssh shiyuan-prod
cd /opt/kairos
git pull origin master
bash deploy/build-frontends.sh
docker compose -f deploy/docker-compose.yml up -d --build
```

---

## 6. 关键 commit 链

```
c2f825a docs: finalize Kairos rebrand status and deployment verification
86dacba fix(nexus-learning-web): align iframe theme key with Kairos rebrand
17975a6 docs: add Kairos rebrand design doc and implementation plan
60381cd docs: rebrand project metadata to Kairos
b6b4541 docs(deploy): update deploy paths from /opt/ai-demos to /opt/kairos
18a622e feat(theme): rename ai-demos-theme to kairos-theme across portal and demo backends
4e9e71a feat(portfolio): rebrand to Kairos — update titles, nav, hero, logo alt
35fcaa7 chore: ignore worktrees directory
```

---

## 7. 总结

`ai-demos` 已正式更名为 **Kairos**，代码、配置、文档、生产部署全部就绪。本地目录结构已整理为单一的 `C:\Users\hzs17\Desktop\kairos` 仓库，可直接作为后续开发的主目录。
