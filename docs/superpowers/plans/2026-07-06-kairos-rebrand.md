# Kairos 重命名与重新定位实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `ai-demos` 从"AI Demo 集合"重新定位为个人工具/项目/学习文档统一门户，更名为 **Kairos**，并更新所有运行时的品牌文案、主题同步 key、部署路径与文档。

**Architecture:** 保留现有 React + Vite 门户与 iframe 嵌入各 demo 的技术架构；仅在品牌层、配置层和部署路径层做统一替换。分区导航在后续迭代中逐步实现，本次先完成品牌重命名与路径迁移。

**Tech Stack:** React + TypeScript + TailwindCSS（门户），Python FastAPI（各 demo 后端），Docker Compose（部署），Nginx（反向代理）。

## Global Constraints

- GitHub 仓库名保持 `rag-qa-system` 不变
- 域名保持 `shiyuan-wreg.cloud` 不变
- 历史 spec/plan/dev-log/CHANGELOG 条目中的 `ai-demos` 引用保留，不修改历史记录
- 所有运行时的 `ai-demos-theme` key 必须同步替换为 `kairos-theme`，前后端一致
- 首页 Hero 副标题统一为 `Kairos · Personal Workspace`
- 本地目录从 `ai-demos/` 重命名为 `kairos/`，服务器部署目录从 `/opt/ai-demos` 迁移到 `/opt/kairos`
- 每次 task 完成后独立验证，最后做全栈验证

---

## File Structure

本次改动涉及以下文件（按任务分组）：

### 前端门户品牌
- `frontends/portfolio/index.html`
- `frontends/portfolio/src/components/NavBar.tsx`
- `frontends/portfolio/src/components/Hero.tsx`
- `frontends/portfolio/src/components/Logo.tsx`
- `frontends/portfolio/src/pages/Changelog.tsx`
- `frontends/portfolio/src/pages/Me.tsx`
- `frontends/portfolio/src/hooks/useTheme.ts`
- `frontends/portfolio/src/hooks/useMotionPreference.ts`
- `frontends/portfolio/src/main.tsx`

### 后端主题同步 key
- `backends/rag_app/main.py`
- `backends/fc_app/main.py`
- `backends/nexus_app/templates/index.html`
- `backends/md_converter_app/converter.py`
- `backends/md_converter_app/templates/base.html`
- `backends/iconforge_app/templates/home.html`

### 部署与运维
- `deploy/PRODUCTION.md`
- `deploy/phase4-workbench-deploy.sh`
- 服务器实际目录 `/opt/ai-demos` → `/opt/kairos`

### 项目元数据
- `README.md`
- `docs/PROJECT-STATE.md`
- `docs/dev-log.md`
- `CHANGELOG.md`
- `docs/career/CLAUDE.md`（可选）
- `frontends/nexus-learning-web/CLAUDE.md`（可选）

---

## Task 0: 本地目录重命名

**Files:**
- Modify: 目录名 `ai-demos/` → `kairos/`

**Interfaces:**
- Consumes: 无
- Produces: 后续所有 task 都在 `kairos/` 目录下执行

**说明：** 目录重命名会影响当前工作目录和 Docker 卷挂载。本计划提供两种方案，选择其一即可。

### 方案 A：直接重命名（推荐，一次性）

- [ ] **Step 1: 停止本地 Docker stack**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml down
```

- [ ] **Step 2: 提交当前未保存的改动**

```bash
git status --short
git add -A
git commit -m "chore: checkpoint before renaming ai-demos to kairos" || echo "nothing to commit"
```

- [ ] **Step 3: 关闭 Claude Code 会话并回到 Git Bash 重命名目录**

在 Git Bash 中执行：

```bash
cd /c/Users/hzs17/Desktop
mv ai-demos kairos
```

- [ ] **Step 4: 重新进入 `kairos/` 目录并继续后续 task**

```bash
cd /c/Users/hzs17/Desktop/kairos
git status --short
```

Expected: 干净的工作树，或仅有未跟踪文件。

### 方案 B：使用 Git Worktree（隔离，不影响原目录）

- [ ] **Step 1: 在当前仓库创建新 worktree**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git worktree add ../kairos master
```

- [ ] **Step 2: 后续 task 全部在 `kairos/` worktree 中执行**

完成后可删除原目录：

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git worktree remove ../kairos  # 或保留作为备份
```

---

## Task 1: 更新前端门户品牌文案

**Files:**
- Modify: `frontends/portfolio/index.html:6`
- Modify: `frontends/portfolio/src/components/NavBar.tsx:53`
- Modify: `frontends/portfolio/src/components/Hero.tsx:14`
- Modify: `frontends/portfolio/src/components/Logo.tsx:5`
- Modify: `frontends/portfolio/src/pages/Changelog.tsx:6`
- Modify: `frontends/portfolio/src/pages/Me.tsx:38`

**Interfaces:**
- Consumes: 无
- Produces: 前端页面标题、导航、Hero、Logo alt 等全部显示 "Kairos"

- [ ] **Step 1: 修改 `index.html` 标题**

```html
<title>Kairos</title>
```

- [ ] **Step 2: 修改 `NavBar.tsx` 品牌文本**

将：
```tsx
<span className="font-bold text-primary">个人集成学习网站</span>
```
改为：
```tsx
<span className="font-bold text-primary">Kairos</span>
```

- [ ] **Step 3: 修改 `Hero.tsx` 副标题**

将：
```tsx
<p className="font-mono text-xs tracking-[0.2em] uppercase text-secondary mb-6">个人集成学习网站 · Personal Lab</p>
```
改为：
```tsx
<p className="font-mono text-xs tracking-[0.2em] uppercase text-secondary mb-6">Kairos · Personal Workspace</p>
```

- [ ] **Step 4: 修改 `Logo.tsx` alt 文本**

将：
```tsx
alt="ai-demos"
```
改为：
```tsx
alt="Kairos"
```

- [ ] **Step 5: 修改 `Changelog.tsx` 文档标题**

将：
```tsx
useDocumentTitle('更新公告 · 个人集成学习网站')
```
改为：
```tsx
useDocumentTitle('更新公告 · Kairos')
```

- [ ] **Step 6: 修改 `Me.tsx` 文档标题**

将：
```tsx
useDocumentTitle('个人 · 个人集成学习网站')
```
改为：
```tsx
useDocumentTitle('个人 · Kairos')
```

- [ ] **Step 7: 本地验证前端无语法错误**

```bash
cd frontends/portfolio
npm run build
```

Expected: build 成功，无 TypeScript 错误。

- [ ] **Step 8: 提交**

```bash
git add frontends/portfolio/index.html frontends/portfolio/src/components/NavBar.tsx frontends/portfolio/src/components/Hero.tsx frontends/portfolio/src/components/Logo.tsx frontends/portfolio/src/pages/Changelog.tsx frontends/portfolio/src/pages/Me.tsx
git commit -m "feat(portfolio): rebrand to Kairos — update titles, nav, hero, logo alt"
```

---

## Task 2: 更新主题同步 localStorage key

**Files:**
- Modify: `frontends/portfolio/src/hooks/useTheme.ts:5-6`
- Modify: `frontends/portfolio/src/hooks/useMotionPreference.ts:3-4`
- Modify: `frontends/portfolio/src/main.tsx:18`
- Modify: `backends/rag_app/main.py:89`
- Modify: `backends/fc_app/main.py:288`
- Modify: `backends/nexus_app/templates/index.html:10`
- Modify: `backends/md_converter_app/converter.py:11`
- Modify: `backends/md_converter_app/templates/base.html:10`
- Modify: `backends/iconforge_app/templates/home.html:10`

**Interfaces:**
- Consumes: 无
- Produces: 所有主题同步脚本统一读取 `kairos-theme`

- [ ] **Step 1: 修改前端 `useTheme.ts`**

将：
```ts
const STORAGE_KEY = 'ai-demos-theme'
const SYNC_EVENT = 'ai-demos-theme-change'
```
改为：
```ts
const STORAGE_KEY = 'kairos-theme'
const SYNC_EVENT = 'kairos-theme-change'
```

- [ ] **Step 2: 修改前端 `useMotionPreference.ts`**

将：
```ts
const STORAGE_KEY = 'ai-demos-parallax'
const SYNC_EVENT = 'ai-demos-parallax-change'
```
改为：
```ts
const STORAGE_KEY = 'kairos-parallax'
const SYNC_EVENT = 'kairos-parallax-change'
```

- [ ] **Step 3: 修改前端 `main.tsx`**

将：
```ts
? (window.localStorage.getItem('ai-demos-theme') as Theme | null)
```
改为：
```ts
? (window.localStorage.getItem('kairos-theme') as Theme | null)
```

- [ ] **Step 4: 修改所有后端主题同步 key**

在以下 6 个文件中，将 `var KEY='ai-demos-theme'` 替换为 `var KEY='kairos-theme'`：

- `backends/rag_app/main.py`
- `backends/fc_app/main.py`
- `backends/nexus_app/templates/index.html`
- `backends/md_converter_app/converter.py`
- `backends/md_converter_app/templates/base.html`
- `backends/iconforge_app/templates/home.html`

可以用一次替换命令完成：

```bash
cd /c/Users/hzs17/Desktop/kairos
sed -i "s/ai-demos-theme/kairos-theme/g" \
  backends/rag_app/main.py \
  backends/fc_app/main.py \
  backends/nexus_app/templates/index.html \
  backends/md_converter_app/converter.py \
  backends/md_converter_app/templates/base.html \
  backends/iconforge_app/templates/home.html
```

- [ ] **Step 5: 验证替换无遗漏**

```bash
grep -R "ai-demos-theme" backends/ frontends/portfolio/src/ || echo "no ai-demos-theme references left"
```

Expected: `no ai-demos-theme references left`

- [ ] **Step 6: 提交**

```bash
git add frontends/portfolio/src/hooks/useTheme.ts frontends/portfolio/src/hooks/useMotionPreference.ts frontends/portfolio/src/main.tsx backends/rag_app/main.py backends/fc_app/main.py backends/nexus_app/templates/index.html backends/md_converter_app/converter.py backends/md_converter_app/templates/base.html backends/iconforge_app/templates/home.html
git commit -m "feat(theme): rename ai-demos-theme to kairos-theme across portal and demo backends"
```

---

## Task 3: 更新部署文档与脚本路径

**Files:**
- Modify: `deploy/PRODUCTION.md:7,20,26,46`
- Modify: `deploy/phase4-workbench-deploy.sh:11,18`

**Interfaces:**
- Consumes: 无
- Produces: 部署文档和脚本中的路径统一为 `/opt/kairos`

- [ ] **Step 1: 修改 `deploy/PRODUCTION.md`**

将所有 `/opt/ai-demos` 替换为 `/opt/kairos`。

可用命令：

```bash
sed -i 's|/opt/ai-demos|/opt/kairos|g' deploy/PRODUCTION.md
```

- [ ] **Step 2: 修改 `deploy/phase4-workbench-deploy.sh`**

将所有 `/opt/ai-demos` 替换为 `/opt/kairos`。

```bash
sed -i 's|/opt/ai-demos|/opt/kairos|g' deploy/phase4-workbench-deploy.sh
```

- [ ] **Step 3: 验证无遗漏**

```bash
grep -R "/opt/ai-demos" deploy/ || echo "no old deploy path left"
```

Expected: `no old deploy path left`

- [ ] **Step 4: 提交**

```bash
git add deploy/PRODUCTION.md deploy/phase4-workbench-deploy.sh
git commit -m "docs(deploy): update deploy paths from /opt/ai-demos to /opt/kairos"
```

---

## Task 4: 更新 README 与项目元数据

**Files:**
- Modify: `README.md:92,126,127`
- Modify: `docs/PROJECT-STATE.md`（新增/更新部分使用 Kairos）
- Modify: `docs/dev-log.md`（追加部署/重命名记录）
- Modify: `CHANGELOG.md`（新增条目使用 Kairos）
- Modify（可选）: `docs/career/CLAUDE.md`
- Modify（可选）: `frontends/nexus-learning-web/CLAUDE.md`

**Interfaces:**
- Consumes: 无
- Produces: README 中的本地路径与项目名统一为 Kairos；状态文档反映新品牌

- [ ] **Step 1: 修改 `README.md` 中的本地路径说明**

将文中出现的 `ai-demos/` 目录引用改为 `kairos/`，例如：

```markdown
kairos/
```

将 clone 后的进入目录说明改为：

```bash
git clone https://github.com/shiyuan-wreg/ai-demos.git
cd ai-demos   # 或重命名为 kairos 后进入 kairos/
```

或更明确地：

```bash
git clone https://github.com/shiyuan-wreg/ai-demos.git kairos
cd kairos
```

- [ ] **Step 2: 修改 `README.md` 中的项目名引用**

将 README 开头的项目名/标题从 "个人集成学习网站" 或 "ai-demos" 改为 "Kairos"。

- [ ] **Step 3: 更新 `docs/PROJECT-STATE.md`**

在文档顶部和最新状态段落中，将品牌名改为 Kairos，并追加一条记录：

```markdown
## 2026-07-06 品牌重命名

项目从 `ai-demos` 重命名为 **Kairos**，定位为个人工具/项目/学习文档统一门户。本地目录 `ai-demos/` 已重命名为 `kairos/`，服务器部署目录同步迁移至 `/opt/kairos`。
```

- [ ] **Step 4: 在 `docs/dev-log.md` 追加记录**

在 2026-07-06 日记录下追加：

```markdown
### 品牌重命名（2026-07-06）

- ✅ 项目更名为 **Kairos**
- ✅ 前端门户品牌文案、标题、Hero 副标题全部更新
- ✅ 前后端主题同步 key 从 `ai-demos-theme` 改为 `kairos-theme`
- ✅ 部署路径从 `/opt/ai-demos` 更新为 `/opt/kairos`
- ✅ 本地目录从 `ai-demos/` 重命名为 `kairos/`
```

- [ ] **Step 5: 在 `CHANGELOG.md` 新增条目**

在最新版本条目或新增一条：

```markdown
## [0.7.0] - 2026-07-06

### Changed
- 项目品牌从 `ai-demos` / "个人集成学习网站" 重命名为 **Kairos**
- 重新定位为个人工具、项目成果与学习文档的统一门户
- 部署目录从 `/opt/ai-demos` 迁移到 `/opt/kairos`
```

- [ ] **Step 6（可选）: 更新 CLAUDE.md 中的项目引用**

如需更新，将 `frontends/nexus-learning-web/CLAUDE.md` 和 `docs/career/CLAUDE.md` 中的当前项目名引用改为 Kairos，历史内容保留。

- [ ] **Step 7: 提交**

```bash
git add README.md docs/PROJECT-STATE.md docs/dev-log.md CHANGELOG.md
git commit -m "docs: rebrand project metadata to Kairos"
```

---

## Task 5: 服务器部署目录迁移

**Files:**
- Modify: 服务器目录 `/opt/ai-demos` → `/opt/kairos`

**Interfaces:**
- Consumes: Task 3 中更新的部署脚本
- Produces: 服务器上的代码目录与部署文档一致

- [ ] **Step 1: SSH 到服务器并停止当前 stack**

```bash
ssh shiyuan-prod
cd /opt/ai-demos
docker compose -f deploy/docker-compose.yml down
```

- [ ] **Step 2: 重命名服务器目录**

```bash
sudo mv /opt/ai-demos /opt/kairos
ls -ld /opt/kairos
```

Expected: `/opt/kairos` 目录存在，原 `/opt/ai-demos` 已不存在。

- [ ] **Step 3: 在新目录中拉取最新代码并部署**

```bash
cd /opt/kairos
git pull origin master
bash deploy/build-frontends.sh
docker compose -f deploy/docker-compose.yml up -d --build
```

Expected: 所有容器重建并启动成功。

- [ ] **Step 4: 验证 7 路由 200**

```bash
D=www.shiyuan-wreg.cloud
for p in "" rag fc nexus doctomd learn iconforge; do
  curl -s -k -o /dev/null -w "/$p/ %{http_code}\n" --resolve $D:443:127.0.0.1 "https://$D/$p/"
done
```

Expected: 全部 200。

---

## Task 6: 本地 Docker 全栈验证

**Files:**
- 验证对象：本地 `http://127.0.0.1:8080` 全栈

**Interfaces:**
- Consumes: 前面所有 task 的改动
- Produces: 本地环境验证通过

- [ ] **Step 1: 在本地 `kairos/` 目录中启动 Docker stack**

```bash
cd /c/Users/hzs17/Desktop/kairos
bash deploy/build-frontends.sh
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml up -d --build
```

- [ ] **Step 2: 验证 7 路由 200**

```bash
for p in / /rag/ /fc/ /nexus/ /doctomd/ /learn/ /iconforge/; do
  curl -s -o /dev/null -w "$p %{http_code}\n" "http://127.0.0.1:8080$p"
done
```

Expected: 全部 200。

- [ ] **Step 3: 验证主题同步 key 生效**

在浏览器中打开 `http://127.0.0.1:8080`，切换主题后检查 DevTools → Application → Local Storage：

Expected: key 为 `kairos-theme`，不再是 `ai-demos-theme`。

- [ ] **Step 4: 验证 RAG must-retrieve 仍然工作**

```bash
curl -s "http://127.0.0.1:8080/rag/chat" -d "query=What is Python list vs tuple?" | python3 -c "import sys,json; d=json.load(sys.stdin); print('tool_calls:', [t.get('name') for t in d.get('tool_calls', [])]); print('[1] in answer:', '[1]' in d.get('answer',''))"
```

Expected: `tool_calls` 包含 `search_docs`，`[1] in answer: True`。

---

## Task 7: 生产部署最终验证

**Files:**
- 验证对象：`https://www.shiyuan-wreg.cloud`

**Interfaces:**
- Consumes: Task 5 的服务器部署
- Produces: 生产环境验证通过

- [ ] **Step 1: 验证生产 7 路由 200**

```bash
ssh shiyuan-prod 'D=www.shiyuan-wreg.cloud; for p in "" rag fc nexus doctomd learn iconforge; do curl -s -k -o /dev/null -w "/$p/ %{http_code}\n" --resolve $D:443:127.0.0.1 "https://$D/$p/"; done'
```

Expected: 全部 200。

- [ ] **Step 2: 验证生产 RAG must-retrieve**

```bash
ssh shiyuan-prod 'python3 - << PY
import json, urllib.request, urllib.parse, ssl
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
D = "www.shiyuan-wreg.cloud"
req = urllib.request.Request(f"https://{D}/rag/chat", data=b"query=What+is+the+difference+between+Python+list+and+tuple%3F", headers={"Host": D})
resp = urllib.request.urlopen(req, context=ctx, timeout=60)
body = json.loads(resp.read())
print("HTTP:", resp.status)
print("search_docs:", any(t.get("name") == "search_docs" for t in body.get("tool_calls", [])))
print("[1] citation:", "[1]" in body.get("answer", ""))
PY'
```

Expected: `HTTP: 200`, `search_docs: True`, `[1] citation: True`。

- [ ] **Step 3: 浏览器验证品牌文案**

在浏览器中打开 `https://www.shiyuan-wreg.cloud`，检查：
- 标签页标题为 `Kairos`
- 导航栏显示 `Kairos`
- Hero 副标题为 `Kairos · Personal Workspace`

- [ ] **Step 4: 浏览器验证主题同步**

打开 `/rag/` 或 `/fc/`，切换门户主题，确认 iframe 内 demo 主题同步变化。

---

## Task 8: 最终收尾

**Files:**
- Modify: `docs/PROJECT-STATE.md`
- Modify: `docs/dev-log.md`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: 所有验证通过的结果
- Produces: 项目状态文档更新

- [ ] **Step 1: 更新 `docs/PROJECT-STATE.md` 最终状态**

在文档顶部或最近更新段落中记录：

```markdown
> 最近更新:2026-07-06(**项目已重命名为 Kairos,本地目录 ai-demos/ → kairos/,服务器目录 /opt/ai-demos → /opt/kairos,生产部署验证通过。**)
```

- [ ] **Step 2: 在 `docs/dev-log.md` 追加最终验证结果**

```markdown
- ✅ 本地 Docker 全栈 7 路由 200
- ✅ 生产服务器 7 路由 200
- ✅ RAG must-retrieve 在生产环境正常工作
- ✅ 品牌文案与主题同步 key 验证通过
```

- [ ] **Step 3: 提交并推送**

```bash
git add docs/PROJECT-STATE.md docs/dev-log.md CHANGELOG.md
git commit -m "docs: finalize Kairos rebrand status and deployment verification"
git push origin master
```

---

## Self-Review

### Spec Coverage

| Spec 要求 | 对应 Task |
|---|---|
| 本地目录 `ai-demos/` → `kairos/` | Task 0 |
| 前端品牌文案改为 Kairos | Task 1 |
| 主题同步 key 统一改 `kairos-theme` | Task 2 |
| 部署路径 `/opt/ai-demos` → `/opt/kairos` | Task 3, Task 5 |
| README / PROJECT-STATE / dev-log 更新 | Task 4, Task 8 |
| Hero 副标题 `Kairos · Personal Workspace` | Task 1 |
| 本地与生产验证 | Task 6, Task 7 |

无遗漏。

### Placeholder Scan

- 无 "TBD" / "TODO" / "implement later"
- 所有代码步骤均给出具体修改内容
- 所有命令均给出预期输出

### Type Consistency

- 所有文件路径在 task 中保持一致
- `kairos-theme` 在前端和后端 task 中一致
- `/opt/kairos` 在部署文档和服务器迁移 task 中一致

### 风险提醒

1. 目录重命名会中断当前 Claude Code 会话，需要在 Task 0 中选择合适方案。
2. `localStorage` key 变更会导致本地主题偏好重置，影响很小。
3. 服务器目录迁移期间服务会短暂不可用，需选择合适时机。
