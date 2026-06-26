# The Machine 全局主题(A2)实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把监控 HUD 皮肤升级为全站可选主题 `machine`(切换器名"监控"),默认仍是极简;选中后全站统一监控配色、等宽、直角、四角方括号、图标可见、分级氛围;`/nexus` 永远监控皮。

**Architecture:** machine 作为第 5 个 `data-theme` 注册进 `useTheme`/`ThemeToggle`;调色板在 `theme.css [data-theme="machine"]` 定义(含 `--grid-line`/`--noise-opacity`,触发 texture.css 全局网格+噪点轻量氛围);细节规则在 `machine-skin.css` 里**同时**作用于 `[data-theme="machine"]`(全局)与 `.machine-skin`(/nexus 强制);demo 页(含 learn)在 machine 主题下复用 `MachineSkin` 上全氛围。顺带修 `useTheme` 跨组件事件同步。

**Tech Stack:** React 18 + TypeScript + Vite + Tailwind(类名→CSS 变量,见 tailwind.config.js)。无新增依赖。

设计依据:`docs/superpowers/specs/2026-06-26-machine-global-theme-a2-design.md`(已评审,§7 全局角标确认要做)。

## Global Constraints

- 不新增依赖;不引外部字体 CDN(复用自托管 JetBrains Mono)。
- 默认主题保持 `mono-light`;不改/不渗漏现有 4 个主题(mono-light/light/deepblue/cyber)。
- `/nexus` 无论当前主题永远套 `MachineSkin`(因其后端 iframe 永久 HUD)。
- 细节规则必须**同时**覆盖 `[data-theme="machine"]` 与 `.machine-skin` 两个上下文,共用一份 CSS。
- 直角只作用于卡片级圆角(rounded-sm/…/2xl)与按钮(.btn-lift);`rounded-full`(圆点/开关旋钮/头像/角色标签)保持圆形。
- 无前端测试运行器;每个任务自动关卡 = 在 `frontends/portfolio` 下 `npm run build`(tsc && vite build)无错;再加任务内手动验收。
- React 18 自动 JSX;组件无需 `import React`;类型用 `import type`。
- 本地预览:vite dev 在 :5180(已代理 demo 到 :8080);docker 全栈在 deploy/(nginx :8080)。

---

### Task 1: 注册 machine 主题 + useTheme 跨组件事件同步

**Files:**
- Modify: `frontends/portfolio/src/hooks/useTheme.ts`
- Modify: `frontends/portfolio/src/components/ThemeToggle.tsx`

**Interfaces:**
- Produces: `Theme` 含 `'machine'`;`ALL_THEMES` 含 `'machine'`;`useTheme()` 的 `theme` 在任意组件实例间经事件实时同步。

- [ ] **Step 1: 重写 useTheme.ts**

整文件替换为:

```ts
import { useEffect, useState } from 'react'

export type Theme = 'mono-light' | 'mono' | 'light' | 'deepblue' | 'cyber' | 'machine'

const STORAGE_KEY = 'ai-demos-theme'
const SYNC_EVENT = 'ai-demos-theme-change'
const DEFAULT_THEME: Theme = 'mono-light'
export const ALL_THEMES: Theme[] = ['mono-light', 'light', 'deepblue', 'cyber', 'machine']

function getInitialTheme(): Theme {
  if (typeof window === 'undefined') return DEFAULT_THEME
  const stored = window.localStorage.getItem(STORAGE_KEY) as Theme | null
  if (stored && ALL_THEMES.includes(stored)) return stored
  return DEFAULT_THEME
}

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(getInitialTheme)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  useEffect(() => {
    if (typeof window === 'undefined') return
    const sync = () => {
      const stored = window.localStorage.getItem(STORAGE_KEY) as Theme | null
      if (stored && ALL_THEMES.includes(stored)) setThemeState(stored)
    }
    window.addEventListener(SYNC_EVENT, sync)
    window.addEventListener('storage', sync)
    return () => {
      window.removeEventListener(SYNC_EVENT, sync)
      window.removeEventListener('storage', sync)
    }
  }, [])

  const setTheme = (t: Theme) => {
    setThemeState(t)
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(STORAGE_KEY, t)
      window.dispatchEvent(new Event(SYNC_EVENT))
    }
  }

  return { theme, setTheme }
}
```

- [ ] **Step 2: ThemeToggle 加"监控"选项**

`frontends/portfolio/src/components/ThemeToggle.tsx` 的 `THEMES` 数组末尾加一项:

```tsx
const THEMES: { key: Theme; label: string }[] = [
  { key: 'mono-light', label: '极简' },
  { key: 'light', label: '浅色' },
  { key: 'deepblue', label: '深蓝' },
  { key: 'cyber', label: '赛博' },
  { key: 'machine', label: '监控' },
]
```

- [ ] **Step 3: 构建**

在 `frontends/portfolio` 下:`npm run build` → 成功无 TS 错误。

- [ ] **Step 4: 手动验收**

`npm run dev`:切换器出现"监控";点它 → `<html data-theme="machine">`;刷新保持;切回其他主题正常。(此时仅 data-theme 切换,配色在 Task 2 才出现。)

- [ ] **Step 5: 提交**

```bash
git add frontends/portfolio/src/hooks/useTheme.ts frontends/portfolio/src/components/ThemeToggle.tsx
git commit -m "feat(portfolio): register machine theme + cross-instance useTheme sync"
```

---

### Task 2: machine 调色板(theme.css)

**Files:**
- Modify: `frontends/portfolio/src/styles/theme.css`(在 `[data-theme="cyber"]` 块之后、`[data-theme="mono-light"]` 之前或文件主题区任意处新增一块)

**Interfaces:**
- Consumes: Tailwind 类→变量映射。
- Produces: `[data-theme="machine"]` 全套站点标准变量 + `--grid-line`/`--noise-opacity`。

- [ ] **Step 1: 新增 machine 主题变量块**

在 `theme.css` 主题块区追加:

```css
/* ===== machine(The Machine 监控 HUD · 暗色) ===== */
[data-theme="machine"] {
  --bg-base: #0a0a0c;
  --bg-soft: #111114;
  --bg-soft-rgb: 17, 17, 20;
  --bg-hero:
    radial-gradient(680px 360px at 50% -8%, rgba(255, 215, 0, 0.06), transparent 70%),
    linear-gradient(180deg, #0c0c0f 0%, #0a0a0c 60%, #08080a 100%);

  --surface-default: #0e0e11;
  --surface-raised: #14141a;
  --surface-hover: #1b1b22;
  --surface-soft: #111114;
  --surface-cold: #0c0e13;

  --border-default: rgba(255, 215, 0, 0.25);
  --border-subtle: rgba(255, 215, 0, 0.10);
  --border-strong: rgba(255, 215, 0, 0.45);

  --text-primary: #ffd700;
  --text-secondary: #e6cf7a;
  --text-tertiary: #9a8c5a;
  --text-muted: #6b6347;
  --text-link: #ffd700;

  --accent-primary: #ffd700;
  --accent-primary-text: #0a0a0c;
  --accent-secondary-bg: rgba(255, 215, 0, 0.12);
  --accent-secondary-text: #ffd700;

  --glow-accent: rgba(255, 215, 0, 0.18);

  --shadow-sm: 0 0 8px rgba(255, 215, 0, 0.08);
  --shadow-md: 0 0 16px rgba(255, 215, 0, 0.10);
  --shadow-lg: 0 0 24px rgba(255, 215, 0, 0.14);
  --shadow-glow: 0 0 0 1px rgba(255, 215, 0, 0.25), 0 0 20px rgba(255, 215, 0, 0.15);

  --font-sans: "JetBrains Mono", "MiSans", "HarmonyOS Sans SC", "PingFang SC",
               "Microsoft YaHei", ui-monospace, monospace;

  /* 触发 texture.css 的全局网格 + 噪点(内容页轻量氛围) */
  --grid-line: rgba(255, 215, 0, 0.06);
  --noise-opacity: 0.03;

  /* 供细节规则复用 */
  --machine-bg: #0a0a0c;
  --machine-yellow: #ffd700;
  --machine-red: #ff4500;
}
```

- [ ] **Step 2: 构建** → `npm run build` 成功。

- [ ] **Step 3: 手动验收**

切到"监控":首页/个人/更新等内容页变深底琥珀黄 + 等宽 + 隐约网格/噪点(无扫描线)。卡片此时仍是圆角(Task 3/4 处理)。其他主题不受影响。

- [ ] **Step 4: 提交**

```bash
git add frontends/portfolio/src/styles/theme.css
git commit -m "feat(portfolio): machine theme palette (global recolor + light grid/noise)"
```

---

### Task 3: 全局细节规则(machine-skin.css 扩展)

**Files:**
- Modify: `frontends/portfolio/src/styles/machine-skin.css`

**Interfaces:**
- Consumes: `.hud-frame` 标记类(Task 4 加到组件)、`--corner` 技法。
- Produces: 直角 / `.hud-frame` 四角方括号 / 按钮直角 / 图标反相 / 黄滚动条,作用于 `[data-theme="machine"]` 与 `.machine-skin`。

- [ ] **Step 1: 替换现有"侧边栏作品项 + 信息卡"块为通用 .hud-frame 块**

把 machine-skin.css 中以注释 `/* ---------- 侧边栏作品项 + 信息卡:四角方括号边框 ---------- */` 开头、到 `.machine-skin .demo-info-card { --corner-len: 12px; }` 结束的整段,替换为:

```css
/* ---------- 四角方括号边框:全局 .hud-frame + /nexus 侧边栏/信息卡 ---------- */
/* 8 段 1px 渐变画四角;颜色走 --corner 便于状态切换 */
[data-theme="machine"] .hud-frame,
[data-theme="machine"] .sidebar-link,
.machine-skin .hud-frame,
.machine-skin .sidebar-link,
.machine-skin .demo-info-card {
  --corner: rgba(255, 215, 0, 0.4);
  --corner-len: 9px;
  border: 1px solid var(--border-subtle);
  border-radius: 0;
  background-image:
    linear-gradient(var(--corner), var(--corner)), linear-gradient(var(--corner), var(--corner)),
    linear-gradient(var(--corner), var(--corner)), linear-gradient(var(--corner), var(--corner)),
    linear-gradient(var(--corner), var(--corner)), linear-gradient(var(--corner), var(--corner)),
    linear-gradient(var(--corner), var(--corner)), linear-gradient(var(--corner), var(--corner));
  background-repeat: no-repeat;
  background-size:
    var(--corner-len) 1px, 1px var(--corner-len),
    var(--corner-len) 1px, 1px var(--corner-len),
    var(--corner-len) 1px, 1px var(--corner-len),
    var(--corner-len) 1px, 1px var(--corner-len);
  background-position:
    top left, top left, top right, top right,
    bottom left, bottom left, bottom right, bottom right;
}
.machine-skin .sidebar-link:hover {
  border-color: var(--border-default);
  --corner: rgba(255, 215, 0, 0.7);
}
.machine-skin .sidebar-link[aria-current="page"] {
  border-color: var(--machine-yellow);
  --corner: var(--machine-yellow);
  box-shadow: var(--shadow-sm);
}
/* 大卡片角标略大 */
[data-theme="machine"] .hud-frame,
.machine-skin .demo-info-card { --corner-len: 12px; }

/* ---------- 直角(卡片级圆角去圆;圆点/旋钮/头像 rounded-full 保留) ---------- */
[data-theme="machine"] :is(.rounded-sm, .rounded, .rounded-md, .rounded-lg, .rounded-xl, .rounded-2xl),
.machine-skin :is(.rounded-sm, .rounded, .rounded-md, .rounded-lg, .rounded-xl, .rounded-2xl) {
  border-radius: 0;
}
[data-theme="machine"] .btn-lift,
.machine-skin .btn-lift { border-radius: 0; }

/* ---------- 图标反相可见(近黑 SVG) ---------- */
[data-theme="machine"] .demo-icon,
.machine-skin .demo-icon { filter: invert(1); }

/* ---------- 黄色滚动条 ---------- */
[data-theme="machine"] ::-webkit-scrollbar { width: 8px; }
[data-theme="machine"] ::-webkit-scrollbar-thumb { background: var(--accent-primary); }
[data-theme="machine"] ::-webkit-scrollbar-track { background: var(--bg-base); }
```

> 注:原 `.machine-skin .demo-icon { filter: invert(1); }` 与 `.machine-skin .sidebar-link span { border-radius: 0; }` 若已存在于文件别处,删除重复项,统一到此处(图标反相已并入上面;图标框直角由通用 rounded 规则覆盖)。

- [ ] **Step 2: 构建** → `npm run build` 成功。

- [ ] **Step 3: 手动验收**

切到"监控":`/nexus` 侧边栏/信息卡四角括号仍正常(无回归);其他卡片此时还没有 `hud-frame`(Task 4 加),但圆角已变直角、图标可见、滚动条变黄。

- [ ] **Step 4: 提交**

```bash
git add frontends/portfolio/src/styles/machine-skin.css
git commit -m "feat(portfolio): global machine detail rules (square, hud-frame brackets, icons, scrollbar)"
```

---

### Task 4: 给卡片组件加 `hud-frame` 标记类

**Files:**（每处在容器 className 里追加 `hud-frame`,不改其他类）
- Modify: `frontends/portfolio/src/components/WorkCard.tsx`(卡片 Link,约 :9)
- Modify: `frontends/portfolio/src/components/AnnouncementBoard.tsx`(约 :13)
- Modify: `frontends/portfolio/src/components/DemoFrame.tsx`(外层容器,约 :50)
- Modify: `frontends/portfolio/src/components/SidebarLayout.tsx`(aside,约 :7)
- Modify: `frontends/portfolio/src/components/DemoInfoCard.tsx`(内框,约 :10,已含 `demo-info-card`)
- Modify: `frontends/portfolio/src/pages/Me.tsx`(:44 hero、:102、:124、:134、:148 各 section;:106 skill group)
- Modify: `frontends/portfolio/src/pages/Changelog.tsx`(文章卡,约 :24)

**Interfaces:** Consumes Task 3 的 `.hud-frame` 样式。

- [ ] **Step 1: 逐个加类**

在每个上述容器的 className 字符串里加入 `hud-frame`(放在 `rounded-*`/`border` 附近即可,不影响其他类)。示例:

```tsx
// WorkCard.tsx
className="hud-frame group block bg-surface border border-border rounded-lg p-5 shadow-md ..."
// DemoInfoCard.tsx
className="hud-frame demo-info-card bg-surface-soft border border-border rounded-xl p-4"
// Changelog.tsx 文章
className="hud-frame rounded-xl border border-border bg-surface shadow-sm hover:shadow-md transition-shadow p-5"
```

Me.tsx 的 hero(:44 `rounded-2xl border bg-hero`)、技能/作品/简历/履历各 section(`rounded-xl ... p-6`)、skill group(:106 `rounded-lg`)同样追加 `hud-frame`。Me 头像占位(:51 `rounded-2xl`)**不加** `hud-frame`(只随直角规则变方,无需括号)。

- [ ] **Step 2: 构建** → `npm run build` 成功。

- [ ] **Step 3: 手动验收**

切到"监控":首页作品卡、公告板、个人页各区块、更新页文章卡都出现四角方括号 + 直角;切回其他主题这些卡恢复原样(hud-frame 在非 machine 下无样式)。

- [ ] **Step 4: 提交**

```bash
git add frontends/portfolio/src/components/WorkCard.tsx frontends/portfolio/src/components/AnnouncementBoard.tsx frontends/portfolio/src/components/DemoFrame.tsx frontends/portfolio/src/components/SidebarLayout.tsx frontends/portfolio/src/components/DemoInfoCard.tsx frontends/portfolio/src/pages/Me.tsx frontends/portfolio/src/pages/Changelog.tsx
git commit -m "feat(portfolio): mark card components with hud-frame for machine brackets"
```

---

### Task 5: 分级氛围 —— demo 页在 machine 下套 MachineSkin

**Files:**
- Modify: `frontends/portfolio/src/pages/Demo.tsx`
- Modify: `frontends/portfolio/src/pages/Learn.tsx`

**Interfaces:** Consumes `useTheme()`(Task 1)、`MachineSkin`。

- [ ] **Step 1: Demo.tsx 条件包裹**

把 `Demo.tsx` 顶部加 `import { useTheme } from '../hooks/useTheme'`;组件内取 `const { theme } = useTheme()`;包裹判断从 `slug === 'nexus'` 改为:

```tsx
const machine = slug === 'nexus' || theme === 'machine'
// ...
return (
  <PageTransition>
    <div className="h-[calc(100vh-3.5rem)] flex flex-col">
      {machine ? <MachineSkin>{content}</MachineSkin> : content}
    </div>
  </PageTransition>
)
```

- [ ] **Step 2: Learn.tsx 条件包裹**

`Learn.tsx` 引入 `useTheme` 与 `MachineSkin`;把内容抽成变量并在 `theme === 'machine'` 时包裹:

```tsx
import { useTheme } from '../hooks/useTheme'
import MachineSkin from '../components/MachineSkin'

export default function Learn() {
  const { theme } = useTheme()
  const content = (
    <div className="flex-1 min-h-0 px-4 sm:px-6 lg:px-8 py-4">
      <DemoFrame src="/learn/" title="Nexus 交互式学习站" />
    </div>
  )
  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col">
      {theme === 'machine' ? <MachineSkin>{content}</MachineSkin> : content}
    </div>
  )
}
```

（保留 Learn.tsx 原有其它结构/导入;仅加 useTheme+MachineSkin 与条件包裹。）

- [ ] **Step 3: 构建** → `npm run build` 成功。

- [ ] **Step 4: 手动验收**

切到"监控":`/rag /fc /doctomd /iconforge /learn` 都出现全氛围(扫描线/暗角/网格/四角框/HUD 文字),`/nexus` 一如既往;切到极简:这些 demo 页恢复普通外壳,仅 `/nexus` 仍监控皮。切主题即时生效(得益于 Task 1 事件同步)。

- [ ] **Step 5: 提交**

```bash
git add frontends/portfolio/src/pages/Demo.tsx frontends/portfolio/src/pages/Learn.tsx
git commit -m "feat(portfolio): full ambiance on demo pages under machine theme"
```

---

### Task 6: 全局 HUD 角标(GlobalHud)

**Files:**
- Create: `frontends/portfolio/src/components/GlobalHud.tsx`
- Modify: `frontends/portfolio/src/App.tsx`

**Interfaces:** Consumes `useTheme()`、`getLatestChangelog()`。

- [ ] **Step 1: 新建 GlobalHud**

```tsx
import { useTheme } from '../hooks/useTheme'
import { getLatestChangelog } from '../data/changelogs'

export default function GlobalHud() {
  const { theme } = useTheme()
  if (theme !== 'machine') return null
  const version = getLatestChangelog()?.version ?? '0.0.0'
  return (
    <div
      aria-hidden="true"
      className="fixed bottom-3 right-4 z-40 pointer-events-none font-mono text-[10px] tracking-widest uppercase"
      style={{ color: 'var(--accent-primary)', opacity: 0.4, textShadow: '0 0 6px rgba(255,215,0,0.25)' }}
    >
      v{version} · MONITORING
    </div>
  )
}
```

- [ ] **Step 2: App.tsx 挂载**

`App.tsx` 引入 `import GlobalHud from './components/GlobalHud'`,在 `min-h-screen` 容器内、`PageTransition` 之后渲染 `<GlobalHud />`:

```tsx
    <div className="min-h-screen bg-base">
      <NavBar />
      <PageTransition key={pathname}>
        <Routes>...</Routes>
      </PageTransition>
      <GlobalHud />
    </div>
```

- [ ] **Step 3: 构建** → `npm run build` 成功。

- [ ] **Step 4: 手动验收**

切到"监控":全站右下角出现极淡 `v0.4.1 · MONITORING`,不挡点击;切回其他主题消失。

- [ ] **Step 5: 提交**

```bash
git add frontends/portfolio/src/components/GlobalHud.tsx frontends/portfolio/src/App.tsx
git commit -m "feat(portfolio): global HUD corner readout under machine theme"
```

---

## 自检(Self-Review)

**Spec 覆盖:**

| Spec 要求 | 任务 |
|---|---|
| §2 主题注册、默认不变 | Task 1 |
| §3 调色板 + grid/noise 轻量氛围 | Task 2 |
| §4 直角/方括号/图标/滚动条,双上下文 | Task 3 |
| §4.2 卡片加 hud-frame | Task 4 |
| §5 分级氛围:demo 套 MachineSkin | Task 5 |
| §6 useTheme 事件同步 | Task 1 |
| §7 全局角标 | Task 6 |
| §10 验证 | 各任务手动验收 |
| §11 回退(仅新增) | 全程新增为主 |

**类型一致性:** `Theme` 含 machine(Task 1)被 Task 5/6 的 `theme === 'machine'` 引用;`.hud-frame`(Task 3 定义,Task 4 使用)一致;`MachineSkin` 默认导出(Task 5 引用)。

**占位符扫描:** 无 TBD;每步含完整代码。

**务实偏差:** 无前端测试运行器,以 build + 手动验收替代单测(同 A1)。
