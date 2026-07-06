# Kairos 重命名与重新定位设计

> **状态：DRAFT（待用户 review）**  
> 设计日期：2026-07-06  
> 主题：将 `ai-demos` 从"AI Demo 集合"重新定位为个人工具、项目成果与学习文档的统一门户，并更名为 **Kairos**。

---

## 1. 背景与动机

`ai-demos` 这个名称诞生于项目早期，当时内容确实以 AI Demo（RAG、FC）为主。随着项目扩展，它已经包含：

- AI/Agent 工具：RAG、Function Calling、Nexus Multi-Agent
- 个人实用工具：DocHub（文档整理）、IconForge（图标转换/清理）
- 学习内容：`/learn` 交互式学习站、学习文档
- 未来计划：cs-quiz-app、安全 Writeups、博客等

`ai-demos` 已经无法准确描述项目的综合性与"给自己用"的属性，需要一个更抽象、更具个人印记的新名字。

---

## 2. 新名字：Kairos

**Kairos**（καιρός）源自古希腊语，指"关键时机"、"恰到好处的时刻"，与单纯计时的 Chronos 相对。

寓意：这个项目不是被动展示，而是在需要时提供恰当工具、知识与项目入口的个人空间。

- 中文环境不强制配中文名，直接使用 **Kairos**
- 域名保持 `shiyuan-wreg.cloud` 不变
- GitHub 仓库名保持 `rag-qa-system` 不变

---

## 3. 定位

> **Kairos 是一个以个人为中心的数字工作台。**
>
> 第一服务对象是站长本人；对外仅作功能展示，不面向外部用户运营。
>
> 它同时承担三种角色：
> - **个人工具箱**：日常使用的实用工具入口
> - **项目成果库**：个人项目的聚合与展示
> - **知识花园**：学习文档、课程、博客的沉淀

---

## 4. 范围

### 4.1 本次改动

- 本地目录名：`ai-demos/` → `kairos/`
- 代码/文案中的显示名称："个人集成学习网站" / "ai-demos" → "Kairos"
- 前端门户品牌、标题、导航文案
- 各 demo 后端的 `localStorage` 主题同步 key（`ai-demos-theme` → `kairos-theme`）
- 部署脚本中本地/服务器路径引用（`/opt/ai-demos` → `/opt/kairos`）
- `README.md` 中的目录名与 clone URL 说明

### 4.2 不改动的范围

- GitHub 仓库名 `rag-qa-system`
- 域名 `shiyuan-wreg.cloud`
- 历史 spec/plan 文档中的 `ai-demos` 引用（保留历史准确性）
- `docs/dev-log.md`、`docs/PROJECT-STATE.md` 中的历史记录（新记录使用 Kairos）
- `agent-console-ai/` 独立目录（外部课程项目）
- `docs/career/` 中的求职材料（保留原样，按需更新简历描述）

---

## 5. 分区架构

采用方案 C：统一门户下的清晰分区。

```
Kairos
├── Tools / 工具
│   ├── Personal / 个人工具
│   │   ├── DocHub       (/doctomd/)  — Markdown 文档整理与浏览
│   │   ├── IconForge    (/iconforge/) — 图标转换与清理
│   │   └── Quiz         (/quiz/)      — 个人学习测验（cs-quiz-app 待集成）
│   └── AI / Agent 作品
│       ├── RAG          (/rag/)       — 检索增强文档问答
│       ├── FC           (/fc/)        — 函数调用 Agent
│       └── Nexus        (/nexus/)     — Multi-Agent Workflow
├── Projects / 项目
│   ├── 安全 Writeups
│   ├── 课程设计
│   └── 独立项目
├── Learn / 学习
│   ├── /learn/          — 交互式学习站
│   ├── 学习文档
│   └── 博客（未来）
└── Lab / 实验
    ├── 沙盒工具
    └── 半成品 Demo
```

### 5.1 分区说明

- **Tools / 工具**：给自己日常使用的工具。再细分为"个人工具"和"AI 作品"，因为后者更偏向能力展示，但本质仍是工具。
- **Projects / 项目**：完整项目成果的展示页，通常是外部仓库或更复杂的独立项目。
- **Learn / 学习**：学习内容与知识沉淀，包括交互课程、文档、博客。
- **Lab / 实验**：不稳定、探索性、临时性的内容，明确与正式工具/项目区分开。

### 5.2 现有模块归属

| 模块 | 路径 | 归属分区 | 说明 |
|---|---|---|---|
| RAG | `/rag/` | Tools → AI | 检索增强问答 |
| FC | `/fc/` | Tools → AI | 函数调用 Agent |
| Nexus | `/nexus/` | Tools → AI → Workflow | 多 Agent 协作工作流 |
| DocHub | `/doctomd/` | Tools → Personal | Markdown 文档整理 |
| IconForge | `/iconforge/` | Tools → Personal | 图标转换/清理 |
| cs-quiz-app | `/quiz/`（计划） | Tools → Personal | 个人学习测验 |
| /learn | `/learn/` | Learn | 交互式学习站 |
| 安全 Writeups | 外部/待集成 | Projects | 二进制安全项目 |
| agent-console-ai | 外部独立项目 | Projects | 鸿蒙课程设计 |

---

## 6. 需要修改的位置清单

### 6.1 前端门户（必须改）

| 文件 | 当前内容 | 改后 |
|---|---|---|
| `frontends/portfolio/index.html` | `<title>个人集成学习网站</title>` | `<title>Kairos</title>` |
| `frontends/portfolio/src/components/NavBar.tsx` | "个人集成学习网站" | "Kairos" |
| `frontends/portfolio/src/components/Hero.tsx` | "个人集成学习网站 · Personal Lab" | "Kairos · Personal Workspace" 或类似 |
| `frontends/portfolio/src/components/Logo.tsx` | `alt="ai-demos"` | `alt="Kairos"` |
| `frontends/portfolio/src/pages/Changelog.tsx` | "更新公告 · 个人集成学习网站" | "更新公告 · Kairos" |
| `frontends/portfolio/src/pages/Me.tsx` | "个人 · 个人集成学习网站" | "个人 · Kairos" |
| `frontends/portfolio/src/hooks/useTheme.ts` | `ai-demos-theme`, `ai-demos-theme-change` | `kairos-theme`, `kairos-theme-change` |
| `frontends/portfolio/src/hooks/useMotionPreference.ts` | `ai-demos-parallax`, `ai-demos-parallax-change` | `kairos-parallax`, `kairos-parallax-change` |
| `frontends/portfolio/src/main.tsx` | `localStorage.getItem('ai-demos-theme')` | `localStorage.getItem('kairos-theme')` |

### 6.2 各 demo 后端主题同步 key（必须改）

所有后端 HTML 中的 `var KEY='ai-demos-theme'` 改为 `var KEY='kairos-theme'`：

- `backends/rag_app/main.py`
- `backends/fc_app/main.py`
- `backends/nexus_app/templates/index.html`
- `backends/md_converter_app/converter.py`
- `backends/md_converter_app/templates/base.html`
- `backends/iconforge_app/templates/home.html`

### 6.3 部署与运维（如改目录名）

| 文件 | 当前内容 | 改后 |
|---|---|---|
| `deploy/PRODUCTION.md` | `/opt/ai-demos` | `/opt/kairos` |
| `deploy/phase4-workbench-deploy.sh` | `DEPLOY_DIR="/opt/ai-demos"` | `DEPLOY_DIR="/opt/kairos"` |
| 服务器实际目录 | `/opt/ai-demos` | `/opt/kairos`（需一次迁移） |

### 6.4 文档与元数据

| 文件 | 处理方式 |
|---|---|
| `README.md` | 更新目录名 `ai-demos/` → `kairos/`，clone URL 说明保留仓库名 `rag-qa-system` |
| `CHANGELOG.md` | 历史条目保留；新增条目使用 Kairos |
| `docs/PROJECT-STATE.md` | 新增/更新部分使用 Kairos；历史记录保留 |
| `docs/dev-log.md` | 新增记录使用 Kairos；历史记录保留 |
| `frontends/nexus-learning-web/CLAUDE.md` | 可选更新为 Kairos 的子项目描述 |
| `docs/career/CLAUDE.md` | 可选更新其中的当前项目位置引用，历史求职内容保留 |

---

## 7. 风险与注意事项

### 7.1 localStorage key 变更

将 `ai-demos-theme` 改为 `kairos-theme` 后，用户本地已有的主题选择会重置为默认。影响很小，因为只是主题偏好。

**建议**：同步修改前后端所有 key，保持一致。

### 7.2 服务器部署目录迁移

如果本地目录改为 `kairos/` 且服务器部署目录也改为 `/opt/kairos`，需要一次手动迁移：

```bash
ssh shiyuan-prod
sudo mv /opt/ai-demos /opt/kairos
# 后续部署使用 /opt/kairos
```

如果暂时不想迁移服务器，可以只改本地目录名和代码显示名，部署目录保持 `/opt/ai-demos`。但这会造成本地与服务器路径不一致。

**建议**：统一改为 `/opt/kairos`，一次性解决。

### 7.3 GitHub 仓库名不变

GitHub 仓库保持 `rag-qa-system`，因此：
- `git clone` URL 不变
- README 中需要说明"本地目录建议克隆为 `kairos/`"
- 如果未来想改仓库名，需要单独评估影响（GitHub 自动重定向可兼容）

### 7.4 历史文档

spec/plan/dev-log 中的历史 `ai-demos` 引用不改动，保持历史准确性。只在新文档和运行时代码中统一使用 Kairos。

---

## 8. 视觉与文案建议

### 8.1 首页 Hero 文案

当前：
> 个人集成学习网站 · Personal Lab

建议：
> Kairos · Personal Workspace  
> 或个人工具与项目空间

### 8.2 导航结构

```
Kairos (Logo)
├── Tools
│   ├── Personal
│   └── AI / Agent
├── Projects
├── Learn
└── Lab
```

具体导航形式（下拉菜单 / 侧边栏 / 标签页）在实现阶段细化。

### 8.3 品牌色与视觉

保留现有黑白科技风 + Machine 监控主题，因为风格已经成熟且用户已验收。Kairos 不是换视觉，而是换品牌定位。

---

## 9. 后续步骤

1. **用户 review 本 design doc**，确认分区、清单、风险
2. **调用 `writing-plans` skill** 生成实施计划
3. **实施**：按 plan 逐步重命名、改文案、改 key、迁移服务器目录
4. **验证**：本地 Docker 全栈 + 生产部署验证
5. **更新 PROJECT-STATE / dev-log / CHANGELOG**

---

## 10. 待确认事项

- [ ] `/learn` 学习站是否归入 **Learn** 分区（建议：是）
- [ ] `cs-quiz-app` 是否归入 **Tools → Personal**（建议：是）
- [ ] 服务器部署目录是否从 `/opt/ai-demos` 迁移到 `/opt/kairos`（建议：是）
- [ ] 是否保留 `frontends/nexus-learning-web/CLAUDE.md` 中的 `ai-demos` 历史引用，或同步更新
- [ ] 首页 Hero 副标题最终文案
