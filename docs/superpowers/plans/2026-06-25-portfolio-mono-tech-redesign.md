# Portfolio 黑白高级科技风重构 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 ai-demos 门户外壳从「靛蓝紫 AI 模板风」重构为「黑白高级感科技风」(默认 `mono-light` 纸白,含暗色 `mono`、科技 hero、纯黑白选中特效、Lucide 图标身份)。

**Architecture:** 现有架构是 Tailwind 把 CSS 变量(`frontends/portfolio/src/styles/theme.css`)映射成工具类(`tailwind.config.js`),主题靠 `document.documentElement[data-theme]` 切换,组件消费语义化工具类(`bg-surface` / `text-primary` / `border-border` 等)。因此重构 = 新增两套主题变量 + 新增质感/字体 token + 重制各组件类名与结构,**不动架构**。旧三主题(light/deepblue/cyber)保留以便回退。

**Tech Stack:** React 18 + TypeScript + Vite + Tailwind CSS 3 + react-router-dom;新增 `lucide-react`(图标)、`@fontsource/inter` + `@fontsource/jetbrains-mono`(本地打包字体)。

## Global Constraints

- **设计依据**:`docs/superpowers/specs/2026-06-25-portfolio-mono-tech-redesign.md`(尤其「最终确认决策」节)。实时参考效果:`docs/superpowers/specs/previews/mono-tech-preview.html`。
- **默认主题** = `mono-light`;`mono`(暗)作为切换器暗色档;`light/deepblue/cyber` **保留不删**。
- **纯黑白,零色相**:选中/当前态靠「冷冽底 + snap 偏移模糊 + 扫描线 + 抬升提亮」四特效区分,不引入任何彩色 accent。
- **保持匿名**:个人页无姓名/学校/自我介绍(2026-06-24 多次确认),用角色定位代替。
- **图标可集中替换**:全部经一个 `Icon` 组件 + slug→图标映射表;用户后续换指定图标只改这一处。
- **元信息用等宽字体**:编号 / 技术栈标签 / 版本号 / 日期一律 `font-mono` + `tracking` + 偏小字号。
- **无障碍**:所有动效包 `@media (prefers-reduced-motion: reduce)` 降级。
- **验证方式**:门户无 JS 单测框架(测试是后端 pytest)。每个任务的验证 = `npm run build`(`tsc && vite build`)通过 + 从 worktree 重建并在 `http://127.0.0.1:8080` 目视确认 + 关键路由 200。
- **工作目录**:`frontends/portfolio`;**compose 必须从 worktree 跑**(主仓库与 worktree 共用 `deploy-*` 容器,详见 redesign 进度账本)。
- **构建/预览命令**(每个任务验证用,从 worktree 根):
  ```bash
  bash deploy/build-frontends.sh
  docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml up -d --no-build
  for p in / /me /changelog /rag/ /learn/; do curl -s -o /dev/null -w "%{http_code} $p\n" http://127.0.0.1:8080$p; done
  ```
  快速前端单独构建(不进 Docker,先验证 tsc/vite 通过):`cd frontends/portfolio && npm run build`

---

## File Structure(本计划涉及的文件)

**新增:**
- `src/styles/theme.css` 内追加 `mono` / `mono-light` 变量块(修改现有文件)
- `src/styles/texture.css`(质感层:网格 + 噪点;由 `styles.css` import)
- `src/components/Icon.tsx`(Lucide 封装 + slug→图标映射,可集中替换)
- `src/components/GlitchTitle.tsx`(hero glitch 标题)
- `src/components/Typewriter.tsx`(打字机副标题)
- `src/components/FakeTerminal.tsx`(假终端记忆点)
- `src/components/Hero.tsx`(组合上面三者 + 网格/辉光/下滚箭头)
- `src/hooks/useScrollReveal.ts`(IntersectionObserver 滚动入场)

**修改:**
- `tailwind.config.js`(加 `surface-cold` / `border-strong` / `cold-sheen` 等 token 映射)
- `src/hooks/useTheme.ts`(Theme 类型加 `mono`/`mono-light`,默认改 `mono-light`)
- `src/components/ThemeToggle.tsx`(切换器加两档)
- `src/data/works.ts`(`icon` 字段从 `{letter,bg,text}` 改为 `{ name: IconName }` + 加 `index` 编号)
- `src/components/WorkCard.tsx`(重制:编号 + Lucide 图标 + mono chips + 四特效)
- `src/components/NavBar.tsx`(mono 化:等宽导航项 + 下划线 hover)
- `src/components/Tag.tsx`(改等宽描边 chip,去彩色)
- `src/pages/Home.tsx`(接入 `<Hero/>` + bento 网格)
- `src/pages/Me.tsx`、`src/pages/Changelog.tsx`、`src/components/DemoFrame.tsx`/`Demo.tsx`、`src/components/AnnouncementBoard.tsx`(套 mono 风格 + 等宽元信息)
- `index.html`、`src/main.tsx`(字体引入)

---

## Task 1：新增 mono / mono-light 主题 token,设为默认

**Files:**
- Modify: `frontends/portfolio/src/styles/theme.css`(在 `[data-theme="cyber"]{...}` 块之后、`:root{ --space-* }` 块之前追加)
- Modify: `frontends/portfolio/src/hooks/useTheme.ts`
- Modify: `frontends/portfolio/src/components/ThemeToggle.tsx`

**Interfaces:**
- Produces:`data-theme="mono-light"` / `data-theme="mono"` 两套 CSS 变量(变量名与现有主题完全一致,新增 `--surface-cold` / `--border-strong` / `--cold-sheen` / `--grid-line` / `--noise-opacity`);`Theme` 类型联合新增两值;默认 `mono-light`。

- [ ] **Step 1：在 `theme.css` 追加 mono-light 与 mono 变量块**

```css
/* ===== mono-light(黑白科技风 · 纸白 · 新默认) ===== */
[data-theme="mono-light"] {
  --bg-base: #fafafa;
  --bg-soft: #ffffff;
  --bg-soft-rgb: 255, 255, 255;
  --bg-hero:
    radial-gradient(680px 360px at 50% -8%, rgba(0,0,0,0.05), transparent 70%),
    linear-gradient(180deg, #ffffff 0%, #fafafa 60%, #f4f4f5 100%);

  --surface-default: #ffffff;
  --surface-raised: #ffffff;
  --surface-hover: #f4f4f5;
  --surface-soft: #f8f8f9;
  --surface-cold: #eceff3;            /* 选中态冷冽底 */

  --border-default: rgba(0,0,0,0.10);
  --border-subtle:  rgba(0,0,0,0.06);
  --border-strong:  rgba(0,0,0,0.22);

  --text-primary: #09090b;
  --text-secondary: #3f3f46;
  --text-tertiary: #71717a;
  --text-muted: #a1a1aa;
  --text-link: #09090b;

  --accent-primary: #09090b;
  --accent-primary-text: #fafafa;
  --accent-secondary-bg: rgba(0,0,0,0.06);
  --accent-secondary-text: #09090b;

  --glow-accent: rgba(0,0,0,0.06);
  --cold-sheen: rgba(80,110,150,0.10);

  --shadow-sm: 0 0 0 1px rgba(0,0,0,0.04);
  --shadow-md: 0 0 0 1px rgba(0,0,0,0.06), 0 8px 24px rgba(0,0,0,0.06);
  --shadow-lg: 0 0 0 1px rgba(0,0,0,0.08), 0 16px 48px rgba(0,0,0,0.08);
  --shadow-glow: 0 0 0 1px rgba(0,0,0,0.10), 0 14px 40px rgba(0,0,0,0.10);

  --grid-line: rgba(0,0,0,0.045);
  --noise-opacity: 0.02;
}

/* ===== mono(黑白科技风 · 墨黑 · 暗色档) ===== */
[data-theme="mono"] {
  --bg-base: #0a0a0b;
  --bg-soft: #0e0e10;
  --bg-soft-rgb: 14, 14, 16;
  --bg-hero:
    radial-gradient(680px 360px at 50% -8%, rgba(255,255,255,0.10), transparent 70%),
    linear-gradient(180deg, #0d0d0f 0%, #0a0a0b 60%, #08080a 100%);

  --surface-default: #0f0f11;
  --surface-raised: #161618;
  --surface-hover: #1c1c20;
  --surface-soft: #121214;
  --surface-cold: #0c0e13;

  --border-default: rgba(255,255,255,0.10);
  --border-subtle:  rgba(255,255,255,0.06);
  --border-strong:  rgba(255,255,255,0.22);

  --text-primary: #f4f4f5;
  --text-secondary: #a1a1aa;
  --text-tertiary: #71717a;
  --text-muted: #52525b;
  --text-link: #fafafa;

  --accent-primary: #fafafa;
  --accent-primary-text: #0a0a0b;
  --accent-secondary-bg: rgba(255,255,255,0.08);
  --accent-secondary-text: #f4f4f5;

  --glow-accent: rgba(255,255,255,0.10);
  --cold-sheen: rgba(150,180,230,0.10);

  --shadow-sm: 0 0 0 1px rgba(255,255,255,0.04);
  --shadow-md: 0 0 0 1px rgba(255,255,255,0.06), 0 8px 24px rgba(0,0,0,0.45);
  --shadow-lg: 0 0 0 1px rgba(255,255,255,0.08), 0 16px 48px rgba(0,0,0,0.55);
  --shadow-glow: 0 0 0 1px rgba(255,255,255,0.14), 0 0 28px rgba(255,255,255,0.06);

  --grid-line: rgba(255,255,255,0.045);
  --noise-opacity: 0.025;
}
```

- [ ] **Step 2：更新 `useTheme.ts`(类型 + 默认 + 校验列表)**

```ts
export type Theme = 'mono-light' | 'mono' | 'light' | 'deepblue' | 'cyber'

const STORAGE_KEY = 'ai-demos-theme'
const DEFAULT_THEME: Theme = 'mono-light'
const ALL_THEMES: Theme[] = ['mono-light', 'mono', 'light', 'deepblue', 'cyber']

function getInitialTheme(): Theme {
  if (typeof window === 'undefined') return DEFAULT_THEME
  const stored = window.localStorage.getItem(STORAGE_KEY) as Theme | null
  if (stored && ALL_THEMES.includes(stored)) return stored
  return DEFAULT_THEME
}
```
(其余 `useTheme` 函数体不变。)

- [ ] **Step 3：更新 `ThemeToggle.tsx` 的 THEMES 列表**

```ts
const THEMES: { key: Theme; label: string }[] = [
  { key: 'mono-light', label: '极简' },
  { key: 'mono', label: '墨黑' },
  { key: 'light', label: '浅色' },
  { key: 'deepblue', label: '深蓝' },
  { key: 'cyber', label: '赛博' },
]
```

- [ ] **Step 4：构建验证**

Run: `cd frontends/portfolio && npm run build`
Expected: 构建成功(`tsc` 无类型错误,`vite build` 产出 dist)。

- [ ] **Step 5：视觉验证 + 提交**

从 worktree 根重建并访问 `http://127.0.0.1:8080`:首页应整体变为纸白(默认 mono-light),切换器有「极简/墨黑」两档可切。
```bash
git add frontends/portfolio/src/styles/theme.css frontends/portfolio/src/hooks/useTheme.ts frontends/portfolio/src/components/ThemeToggle.tsx
git commit -m "feat(portfolio): add mono/mono-light themes, set mono-light default"
```

---

## Task 2：接入本地字体(Inter + JetBrains Mono)

**Files:**
- Modify: `frontends/portfolio/package.json`(新增依赖)
- Modify: `frontends/portfolio/src/main.tsx`(import 字体)
- Modify: `frontends/portfolio/src/styles/theme.css`(`:root` 的 `--font-sans` / `--font-mono`)

**Interfaces:**
- Produces:全站 `font-sans` = Inter→几何黑体回退;`font-mono` = JetBrains Mono。Tailwind 已映射 `fontFamily.sans/mono`,无需改 config。

- [ ] **Step 1：安装字体包(本地打包,不依赖 CDN)**

Run: `cd frontends/portfolio && npm i @fontsource/inter @fontsource/jetbrains-mono`
Expected: 两个包写入 `dependencies`。

- [ ] **Step 2：在 `main.tsx` 顶部 import 所需字重**

```ts
import '@fontsource/inter/400.css'
import '@fontsource/inter/500.css'
import '@fontsource/inter/600.css'
import '@fontsource/inter/700.css'
import '@fontsource/inter/800.css'
import '@fontsource/jetbrains-mono/400.css'
import '@fontsource/jetbrains-mono/500.css'
```
(放在现有 `import './styles.css'` 之前。)

- [ ] **Step 3：更新 `theme.css` 的字体变量**

```css
:root {
  --font-sans: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI",
               "MiSans", "HarmonyOS Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  /* --space-* / --radius-* / --max-* 等其余变量保持不变 */
}
```

- [ ] **Step 4：构建验证**

Run: `cd frontends/portfolio && npm run build`
Expected: 构建成功,dist 中含字体 woff2 资源。

- [ ] **Step 5：视觉验证 + 提交**

访问首页:正文应变为 Inter(西文)字形;后续等宽元信息将用 JetBrains Mono。
```bash
git add frontends/portfolio/package.json frontends/portfolio/package-lock.json frontends/portfolio/src/main.tsx frontends/portfolio/src/styles/theme.css
git commit -m "feat(portfolio): bundle Inter + JetBrains Mono fonts locally"
```

---

## Task 3：质感层(全局网格 + 噪点)

**Files:**
- Create: `frontends/portfolio/src/styles/texture.css`
- Modify: `frontends/portfolio/src/styles.css`(`@import './styles/texture.css';`)

**Interfaces:**
- Produces:`body::before`(网格,顶部清晰向下渐隐)、`body::after`(噪点)两层固定背景,z-index 置底,`pointer-events:none`。

- [ ] **Step 1:创建 `texture.css`**

```css
/* 质感层:全局网格 + 噪点。强度极低,看不见但有质感。 */
body::before {
  content: "";
  position: fixed;
  inset: 0;
  z-index: -2;
  pointer-events: none;
  background-image:
    linear-gradient(var(--grid-line) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
  background-size: 54px 54px;
  -webkit-mask-image: radial-gradient(ellipse at 50% -5%, #000 35%, transparent 80%);
          mask-image: radial-gradient(ellipse at 50% -5%, #000 35%, transparent 80%);
}
body::after {
  content: "";
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  opacity: var(--noise-opacity);
  mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
@media (prefers-reduced-motion: reduce) { /* 静态层无需处理,占位说明 */ }
```

> 注意:`body` 必须不挡住伪元素 —— 现有 `theme.css` 里 `body{ background-color: var(--bg-base) }` 是实色,会盖住 `z-index:-1/-2` 的伪元素吗?不会:伪元素 z-index 为负,位于 body 背景之上、内容之下,正确。如发现被盖,将 body 背景改为 `transparent` 并把底色移到 `html`。

- [ ] **Step 2:在 `styles.css` 顶部追加 import**

```css
@import './styles/texture.css';
```
(放在文件最前,Tailwind 指令之前或之后均可,保持现有 `@tailwind` 指令不动。)

- [ ] **Step 3:构建验证**

Run: `cd frontends/portfolio && npm run build`
Expected: 构建成功。

- [ ] **Step 4:视觉验证 + 提交**

访问首页:背景应能看到极淡网格(顶部明显、向下渐隐),纯色表面带轻微颗粒。亮/暗主题切换网格颜色应自适应。
```bash
git add frontends/portfolio/src/styles/texture.css frontends/portfolio/src/styles.css
git commit -m "feat(portfolio): add subtle grid + noise texture layer"
```

---

## Task 4:Tailwind 追加 mono 专用 token 映射

**Files:**
- Modify: `frontends/portfolio/tailwind.config.js`

**Interfaces:**
- Produces:工具类 `bg-surface-cold`、`border-strong`、阴影/底色可在组件中直接用。

- [ ] **Step 1:在 `tailwind.config.js` 的 `theme.extend.colors` 内补充**

`surface` 对象加一行 `cold`,`border` 对象加一行 `strong`:
```js
surface: {
  DEFAULT: 'var(--surface-default)',
  raised: 'var(--surface-raised)',
  hover: 'var(--surface-hover)',
  soft: 'var(--surface-soft)',
  cold: 'var(--surface-cold)',
},
border: {
  DEFAULT: 'var(--border-default)',
  subtle: 'var(--border-subtle)',
  strong: 'var(--border-strong)',
},
```

- [ ] **Step 2:构建验证**

Run: `cd frontends/portfolio && npm run build`
Expected: 构建成功;`bg-surface-cold` / `border-strong` 可用。

- [ ] **Step 3:提交**

```bash
git add frontends/portfolio/tailwind.config.js
git commit -m "feat(portfolio): map surface-cold/border-strong tailwind tokens"
```

---

## Task 5:Icon 组件(Lucide 封装,可集中替换)+ works 数据迁移

**Files:**
- Modify: `frontends/portfolio/package.json`(加 `lucide-react`)
- Create: `frontends/portfolio/src/components/Icon.tsx`
- Modify: `frontends/portfolio/src/data/works.ts`(`icon` 字段重构 + 加 `index`)
- Modify: `frontends/portfolio/src/components/IconBox.tsx`(改为渲染 Lucide 图标 + 编号)

**Interfaces:**
- Produces:
  - `IconName` 类型(`'file-search' | 'terminal' | 'workflow' | 'graduation-cap' | 'file-text'`)
  - `<Icon name={IconName} className?={string} />` 组件 —— **后续换图标库只改此文件的映射表**
  - `Work.icon: IconName`、`Work.index: string`(如 `'01'`)
- Consumes(后续 Task 6):`WorkCard` 用 `work.index` 与 `<Icon name={work.icon} />`。

- [ ] **Step 1:安装 lucide-react**

Run: `cd frontends/portfolio && npm i lucide-react`

- [ ] **Step 2:创建 `Icon.tsx`(集中映射,换源只改这里)**

```tsx
import { FileSearch, Terminal, Workflow, GraduationCap, FileText, type LucideIcon } from 'lucide-react'

export type IconName = 'file-search' | 'terminal' | 'workflow' | 'graduation-cap' | 'file-text'

// 换图标库时:只改这张表(把右侧组件替换为新库组件即可)
const MAP: Record<IconName, LucideIcon> = {
  'file-search': FileSearch,
  'terminal': Terminal,
  'workflow': Workflow,
  'graduation-cap': GraduationCap,
  'file-text': FileText,
}

export default function Icon({ name, className = 'w-5 h-5', strokeWidth = 1.6 }: {
  name: IconName
  className?: string
  strokeWidth?: number
}) {
  const C = MAP[name]
  return <C className={className} strokeWidth={strokeWidth} aria-hidden="true" />
}
```

- [ ] **Step 3:迁移 `works.ts`(改 `Work` 类型 + 每条 icon/index)**

把 `Work` 类型中 `icon: { letter; bg; text }` 改为:
```ts
import type { IconName } from '../components/Icon'

export type Work = {
  slug: string
  index: string            // 编号,如 '01'
  title: string
  desc: string
  tech: string[]
  github?: string
  path: string
  icon: IconName
  changelog: { version: string; date: string; items: string[] }[]
}
```
并把 5 条数据的 `icon`/`index` 改为(其余字段不变):
```ts
// rag:     index: '01', icon: 'file-search'
// fc:      index: '02', icon: 'terminal'
// nexus:   index: '03', icon: 'workflow'
// learn:   index: '04', icon: 'graduation-cap'
// doctomd: index: '05', icon: 'file-text'
```
(注意:删除每条里旧的 `icon: { letter, bg, text }` 整块。)

- [ ] **Step 4:简化 `IconBox.tsx`(改成 Lucide 容器,供复用)**

```tsx
import Icon, { type IconName } from './Icon'

export default function IconBox({ name }: { name: IconName }) {
  return (
    <div className="w-10 h-10 rounded-md border border-border flex items-center justify-center text-secondary shrink-0">
      <Icon name={name} />
    </div>
  )
}
```

- [ ] **Step 5:构建验证**

Run: `cd frontends/portfolio && npm run build`
Expected: 可能报 `WorkCard.tsx` 仍用旧 `work.icon.letter` 的类型错误 —— **这是预期的**,Task 6 修复。先确认错误仅来自 WorkCard/其它消费方,且 `Icon.tsx`/`works.ts`/`IconBox.tsx` 三者自身类型正确。

- [ ] **Step 6:提交**

```bash
git add frontends/portfolio/package.json frontends/portfolio/package-lock.json frontends/portfolio/src/components/Icon.tsx frontends/portfolio/src/data/works.ts frontends/portfolio/src/components/IconBox.tsx
git commit -m "feat(portfolio): add replaceable Lucide Icon component, migrate works to icon name + index"
```

---

## Task 6:WorkCard 重制(编号 + Lucide 图标 + mono chips + 四特效)

**Files:**
- Modify: `frontends/portfolio/src/components/WorkCard.tsx`
- Modify: `frontends/portfolio/src/components/Tag.tsx`(改等宽描边 chip)
- Modify: `frontends/portfolio/src/styles/texture.css`(追加卡片选中特效 CSS —— 因含 `::after`/`@keyframes`,放 CSS 文件比 Tailwind 类更合适)

**Interfaces:**
- Consumes:`work.index`、`work.icon`(Task 5);`<Icon/>`、`<Tag/>`。
- Produces:`.work-card` / `.work-card__scan` / `.work-card__inner` class 约定 + `:hover`/`.is-active` 触发四特效。

- [ ] **Step 1:在 `texture.css` 末尾追加卡片选中特效**

```css
/* WorkCard 选中态四特效:冷冽底 + snap 偏移模糊 + 扫描线 + 抬升提亮。纯黑白。 */
.work-card { position: relative; overflow: hidden;
  transition: border-color .25s, transform .28s cubic-bezier(.2,.7,.2,1), background .35s, box-shadow .3s; }
.work-card::after { content:""; position:absolute; inset:0; z-index:0; pointer-events:none; opacity:0; transition:opacity .35s;
  background: radial-gradient(420px 160px at 80% -10%, var(--cold-sheen), transparent 70%); }
.work-card__scan { position:absolute; left:0; right:0; top:0; height:34%; z-index:0; pointer-events:none; opacity:0;
  background: linear-gradient(180deg, var(--cold-sheen), transparent); }
.work-card__inner { position: relative; z-index: 1; }
.work-card:hover, .work-card:focus-visible, .work-card.is-active {
  transform: translateY(-3px); border-color: var(--border-strong);
  background: var(--surface-cold);
  box-shadow: 0 0 0 1px var(--border-strong), 0 14px 40px rgba(0,0,0,.16), 0 0 40px var(--glow-accent); }
.work-card:hover::after, .work-card:focus-visible::after, .work-card.is-active::after { opacity: 1; }
.work-card:hover .work-card__scan, .work-card.is-active .work-card__scan { animation: work-scan .7s ease-out 1; }
.work-card:hover .work-card__inner, .work-card.is-active .work-card__inner { animation: work-snap .3s cubic-bezier(.2,.7,.2,1) 1; }
@keyframes work-scan { 0%{opacity:.9; transform:translateY(-40%)} 100%{opacity:0; transform:translateY(320%)} }
@keyframes work-snap { 0%{transform:translateX(-5px); filter:blur(3px)} 60%{transform:translateX(1px); filter:blur(.6px)} 100%{transform:translateX(0); filter:blur(0)} }
@media (prefers-reduced-motion: reduce) {
  .work-card:hover, .work-card.is-active { transform:none }
  .work-card__scan, .work-card__inner { animation:none !important }
}
```

- [ ] **Step 2:重制 `Tag.tsx` 为等宽描边 chip(去彩色)**

```tsx
export default function Tag({ children }: { children: React.ReactNode }) {
  return (
    <span className="font-mono text-[11px] tracking-wide text-tertiary border border-border-subtle rounded px-2 py-0.5">
      {children}
    </span>
  )
}
```
(删除原 `color` prop 与彩色映射;调用方不再传 `color`。)

- [ ] **Step 3:重制 `WorkCard.tsx`**

```tsx
import { Link } from 'react-router-dom'
import { Work } from '../data/works'
import Icon from './Icon'
import Tag from './Tag'

export default function WorkCard({ work }: { work: Work }) {
  return (
    <Link
      to={work.path}
      className="work-card group block bg-surface border border-border rounded-lg p-5 shadow-sm"
    >
      <span className="work-card__scan" />
      <div className="work-card__inner">
        <div className="flex items-center justify-between">
          <span className="font-mono text-xs tracking-widest text-muted">{work.index}</span>
          <span className="w-9 h-9 rounded-md border border-border flex items-center justify-center text-secondary transition-colors group-hover:text-primary group-hover:border-strong">
            <Icon name={work.icon} />
          </span>
        </div>
        <h3 className="mt-4 font-semibold text-primary tracking-tight">{work.title}</h3>
        <p className="mt-1.5 text-sm text-secondary line-clamp-2">{work.desc}</p>
        <div className="mt-4 flex flex-wrap gap-2">
          {work.tech.map((t) => (
            <Tag key={t}>{t}</Tag>
          ))}
        </div>
      </div>
    </Link>
  )
}
```

- [ ] **Step 4:构建验证**

Run: `cd frontends/portfolio && npm run build`
Expected: 构建成功(Task 5 遗留的类型错误此时消除)。若其它文件(如 Me.tsx)仍用旧 `Tag color=` 或 `IconBox letter=`,记录下来在 Task 8/9 修复;若阻断构建则一并在此最小修正。

- [ ] **Step 5:视觉验证 + 提交**

首页作品卡应为:左上等宽编号、右上线性图标、mono 描边技术栈;**悬停**出现冷冽底 + 内容 snap 模糊 + 扫描线 + 抬升。
```bash
git add frontends/portfolio/src/components/WorkCard.tsx frontends/portfolio/src/components/Tag.tsx frontends/portfolio/src/styles/texture.css
git commit -m "feat(portfolio): redesign WorkCard with index/icon/mono-chips + monochrome focus effects"
```

---

## Task 7:Hero 区(glitch 标题 + 打字机 + 假终端 + 网格辉光)

**Files:**
- Create: `frontends/portfolio/src/components/GlitchTitle.tsx`
- Create: `frontends/portfolio/src/components/Typewriter.tsx`
- Create: `frontends/portfolio/src/components/FakeTerminal.tsx`
- Create: `frontends/portfolio/src/components/Hero.tsx`
- Modify: `frontends/portfolio/src/styles/texture.css`(追加 glitch + 终端 CSS)
- Modify: `frontends/portfolio/src/pages/Home.tsx`(用 `<Hero/>` 替换旧首屏 `<section>`)

**Interfaces:**
- Produces:`<Hero/>` 自给自足(无 props);`<GlitchTitle text="..." />`、`<Typewriter text="..." speed?={number} />`、`<FakeTerminal lines={{type:'cmd'|'out', text:string}[]} />`。
- Consumes:Home 用 `<Hero/>`。

- [ ] **Step 1:在 `texture.css` 追加 glitch + 终端样式(glitch 参数取自定稿)**

```css
/* glitch 黑白版:静止恒定轻错位 + 偶发自然爆发(两层互质时长,每次窗口~8%) */
.glitch { position: relative; display: inline-block; }
.glitch::before, .glitch::after { content: attr(data-text); position: absolute; top: 0; left: 0; width: 100%;
  overflow: hidden; pointer-events: none; will-change: transform, clip-path, opacity; }
.glitch::before { color: var(--text-secondary); opacity:.45; transform: translateX(-.5px); clip-path: inset(0 0 52% 0); }
.glitch::after  { color: var(--text-tertiary);  opacity:.45; transform: translateX(.5px);  clip-path: inset(50% 0 0 0); }
.glitch.is-on::before { animation: glA 5.7s ease-in-out infinite; }
.glitch.is-on::after  { animation: glB 4.3s ease-in-out infinite; }
@keyframes glA {
  0%,5%,28%,54%,77%,100%{transform:translateX(-.5px);clip-path:inset(0 0 52% 0);opacity:.45}
  7%{transform:translateX(-3px);clip-path:inset(14% 0 60% 0);opacity:.8}
  11%{transform:translateX(2px);clip-path:inset(30% 0 40% 0);opacity:.6}
  15%{transform:translateX(-2px);clip-path:inset(8% 0 66% 0);opacity:.78}
  19%{transform:translateX(2px);clip-path:inset(22% 0 50% 0);opacity:.62}
  23%{transform:translateX(-1px);clip-path:inset(12% 0 58% 0);opacity:.55}
  56%{transform:translateX(-3px);clip-path:inset(6% 0 70% 0);opacity:.8}
  60%{transform:translateX(2px);clip-path:inset(20% 0 50% 0);opacity:.6}
  64%{transform:translateX(-2px);clip-path:inset(12% 0 58% 0);opacity:.72}
  68%{transform:translateX(2px);clip-path:inset(28% 0 44% 0);opacity:.6}
  72%{transform:translateX(-1px);clip-path:inset(16% 0 54% 0);opacity:.55}
}
@keyframes glB {
  0%,31%,58%,79%,100%{transform:translateX(.5px);clip-path:inset(50% 0 0 0);opacity:.45}
  33%{transform:translateX(3px);clip-path:inset(58% 0 6% 0);opacity:.8}
  37%{transform:translateX(-2px);clip-path:inset(66% 0 18% 0);opacity:.6}
  41%{transform:translateX(2px);clip-path:inset(54% 0 28% 0);opacity:.72}
  45%{transform:translateX(-1px);clip-path:inset(72% 0 4% 0);opacity:.58}
  49%{transform:translateX(2px);clip-path:inset(60% 0 14% 0);opacity:.6}
  81%{transform:translateX(3px);clip-path:inset(56% 0 10% 0);opacity:.8}
  85%{transform:translateX(-2px);clip-path:inset(64% 0 20% 0);opacity:.6}
  89%{transform:translateX(2px);clip-path:inset(52% 0 30% 0);opacity:.72}
  93%{transform:translateX(-1px);clip-path:inset(70% 0 6% 0);opacity:.58}
}
.blink { display:inline-block; width:.6ch; background: currentColor; animation: blink .9s step-end infinite; }
@keyframes blink { 50% { opacity: 0 } }
.term { border:1px solid var(--border-default); border-radius:12px; background: var(--surface-soft); overflow:hidden; }
.term__bar { display:flex; align-items:center; gap:7px; padding:11px 14px; border-bottom:1px solid var(--border-subtle); }
.term__dot { width:11px; height:11px; border-radius:50%; background: var(--border-strong); display:inline-block; }
.term__body { padding:16px 18px; line-height:1.9; }
@media (prefers-reduced-motion: reduce) { .glitch.is-on::before, .glitch.is-on::after, .blink { animation: none } }
```

- [ ] **Step 2:创建 `GlitchTitle.tsx`**

```tsx
export default function GlitchTitle({ text, className = '' }: { text: string; className?: string }) {
  return (
    <h1
      data-text={text}
      className={`glitch is-on text-4xl md:text-6xl font-extrabold tracking-tight text-primary ${className}`}
    >
      {text}
    </h1>
  )
}
```

- [ ] **Step 3:创建 `Typewriter.tsx`**

```tsx
import { useEffect, useState } from 'react'

export default function Typewriter({ text, speed = 70, className = '' }: {
  text: string; speed?: number; className?: string
}) {
  const [n, setN] = useState(0)
  const reduce = typeof window !== 'undefined'
    && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
  useEffect(() => {
    if (reduce) { setN(text.length); return }
    if (n >= text.length) return
    const id = setTimeout(() => setN(n + 1), speed)
    return () => clearTimeout(id)
  }, [n, text, speed, reduce])
  return (
    <span className={`font-mono ${className}`}>
      {text.slice(0, n)}<span className="blink" aria-hidden="true" />
    </span>
  )
}
```

- [ ] **Step 4:创建 `FakeTerminal.tsx`**

```tsx
export type TermLine = { type: 'cmd' | 'out'; text: string }

export default function FakeTerminal({ lines, title = 'shiyuan-wreg.cloud — zsh' }: {
  lines: TermLine[]; title?: string
}) {
  return (
    <div className="term font-mono text-[13px] text-secondary max-w-xl mx-auto text-left">
      <div className="term__bar">
        <span className="term__dot" /><span className="term__dot" /><span className="term__dot" />
        <span className="ml-2 text-[11px] text-muted tracking-wide">{title}</span>
      </div>
      <div className="term__body">
        {lines.map((l, i) => (
          <div key={i} className={l.type === 'cmd' ? 'text-primary' : 'text-tertiary'}>
            {l.type === 'cmd' ? <span className="text-muted">$ </span> : '  '}{l.text}
          </div>
        ))}
      </div>
    </div>
  )
}
```

- [ ] **Step 5:创建 `Hero.tsx`(组合 + 网格辉光 + 下滚箭头)**

```tsx
import { Link } from 'react-router-dom'
import GlitchTitle from './GlitchTitle'
import Typewriter from './Typewriter'
import FakeTerminal from './FakeTerminal'
import Button from './Button'

export default function Hero() {
  return (
    <section className="relative overflow-hidden bg-hero border-b border-border-subtle">
      <div className="relative max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-20 md:py-28 text-center">
        <p className="font-mono text-xs tracking-[0.2em] uppercase text-tertiary mb-6">个人集成学习网站 · Personal Lab</p>
        <GlitchTitle text="构建可运行的 AI / Agent 应用" />
        <Typewriter
          text="RAG · Function-Calling · Multi-Agent · 已部署生产环境"
          className="block mt-6 text-sm md:text-base text-secondary"
        />
        <div className="mt-9 flex items-center justify-center gap-3">
          <Link to="/rag"><Button>浏览作品</Button></Link>
          <Link to="/learn"><Button variant="secondary">开始学习</Button></Link>
        </div>
        <div className="mt-12">
          <FakeTerminal lines={[
            { type: 'cmd', text: 'curl https://www.shiyuan-wreg.cloud/rag/api/ask' },
            { type: 'out', text: '→ 200 OK · 检索 4 段 · 生成回答 (1.2s)' },
            { type: 'cmd', text: 'docker compose ps' },
            { type: 'out', text: 'rag ✓  fc ✓  nexus ✓  doctomd ✓  nginx ✓' },
          ]} />
        </div>
      </div>
    </section>
  )
}
```

- [ ] **Step 6:在 `Home.tsx` 用 `<Hero/>` 替换旧首屏 section**

删除 Home.tsx 中从 `<section className="relative overflow-hidden bg-hero ...">` 到其闭合 `</section>` 的整段(旧 h1/p/按钮),替换为:
```tsx
import Hero from '../components/Hero'
// ...
return (
  <div>
    <Hero />
    <AnnouncementBoard />
    {/* 其余「精选作品」section 不变 */}
```

- [ ] **Step 7:构建验证**

Run: `cd frontends/portfolio && npm run build`
Expected: 构建成功。

- [ ] **Step 8:视觉验证 + 提交**

首页首屏:网格+冷白辉光底、glitch 黑白大标题(静止轻错位、偶发自然爆发)、等宽打字机副标题、假终端逐行展示。
```bash
git add frontends/portfolio/src/components/GlitchTitle.tsx frontends/portfolio/src/components/Typewriter.tsx frontends/portfolio/src/components/FakeTerminal.tsx frontends/portfolio/src/components/Hero.tsx frontends/portfolio/src/styles/texture.css frontends/portfolio/src/pages/Home.tsx
git commit -m "feat(portfolio): add tech hero (glitch title + typewriter + fake terminal)"
```

---

## Task 8:NavBar mono 化(等宽导航 + 下划线 hover)

**Files:**
- Modify: `frontends/portfolio/src/components/NavBar.tsx`

**Interfaces:**
- Consumes:无新依赖。Produces:导航视觉对齐 mono 风格(等宽小标签 + 滑出下划线 + 品牌单色)。

- [ ] **Step 1:更新品牌块与导航项类名**

将品牌图标块由彩色 `bg-accent` 保持(accent 在 mono 下即黑/白),但导航项标签改等宽 + hover 滑出下划线。把桌面端 `ITEMS.map` 渲染改为:
```tsx
{ITEMS.map((it) => (
  <Link
    key={it.to}
    to={it.to}
    className={`group relative font-mono text-xs tracking-wide uppercase transition-colors ${
      isActive(it.to) ? 'text-primary' : 'text-tertiary hover:text-primary'
    }`}
  >
    {it.label}
    <span className={`absolute -bottom-[18px] left-0 h-px bg-accent transition-all duration-300 ${
      isActive(it.to) ? 'w-full' : 'w-0 group-hover:w-full'
    }`} />
  </Link>
))}
```
(品牌文字 `个人集成学习网站` 保持 `font-bold text-primary`;`AI` 角标块保留。)

- [ ] **Step 2:构建验证**

Run: `cd frontends/portfolio && npm run build`
Expected: 构建成功。

- [ ] **Step 3:视觉验证 + 提交**

导航项应为等宽大写小标签,hover 时下划线由左滑出;当前页下划线常驻。
```bash
git add frontends/portfolio/src/components/NavBar.tsx
git commit -m "feat(portfolio): mono-style navbar (mono labels + sliding underline)"
```

---

## Task 9:Me / Changelog / AnnouncementBoard / Demo 套 mono 风格

**Files:**
- Modify: `frontends/portfolio/src/pages/Me.tsx`
- Modify: `frontends/portfolio/src/pages/Changelog.tsx`
- Modify: `frontends/portfolio/src/components/AnnouncementBoard.tsx`
- Modify: `frontends/portfolio/src/components/DemoFrame.tsx` 和/或 `src/pages/Demo.tsx`
- Modify(按需):`frontends/portfolio/src/components/DemoInfoCard.tsx`、`SidebarNav.tsx`

**Interfaces:**
- Consumes:`<Icon/>`、`<Tag/>`(无 color)、`work.index`。统一约定:版本号/日期/编号用 `font-mono text-xs tracking-wide text-muted`;卡片用 `bg-surface border border-border rounded-lg`,去除彩色 accent 条。

- [ ] **Step 1:Me.tsx —— 替换彩色 hero glow 与图标用法**
  - hero 区背景由原彩色渐变改为 `bg-hero`(已是黑白)+ 复用网格;头像/角标用单色。
  - 技能分组卡标题加等宽编号(如 `01 / 语言`);技能项用 `<Tag>` 等宽 chip。
  - 若 Me 仍调用旧 `IconBox letter=.../` 或 `Tag color=...`,改为新签名(`<IconBox name=.../>` 或 `<Tag>`)。
  - 保持匿名:不加姓名/学校/自我介绍。

- [ ] **Step 2:Changelog.tsx + AnnouncementBoard.tsx —— 卡片 mono 化**
  - 每条版本:左侧 `font-mono` 版本号 `v0.3` + 日期;卡片发丝边框、去彩色。
  - 首页公告板单卡:套 `bg-surface border border-border` + 等宽版本号 + 整卡可点(逻辑不变,仅换类名)。

- [ ] **Step 3:Demo 页工具栏/iframe 容器 —— 极简化**
  - iframe 外层加 `border border-border rounded-lg`;工具栏标题用等宽显示「编号 + demo 名」;刷新/新窗口按钮用 `<Icon/>`(可加 `refresh-cw` / `external-link` 到 Icon 映射表)。
  - 若需新图标,在 `Icon.tsx` 的 `MAP` 与 `IconName` union 同步补充。

- [ ] **Step 4:全量构建验证**

Run: `cd frontends/portfolio && npm run build`
Expected: 构建成功,无残留旧 `icon.letter` / `Tag color=` 类型错误。

- [ ] **Step 5:视觉验证 + 提交**

逐页访问 `/me`、`/changelog`、`/rag`(demo 页):均为统一黑白风、等宽元信息、发丝边框。
```bash
git add frontends/portfolio/src/pages/Me.tsx frontends/portfolio/src/pages/Changelog.tsx frontends/portfolio/src/components/AnnouncementBoard.tsx frontends/portfolio/src/components/DemoFrame.tsx frontends/portfolio/src/pages/Demo.tsx frontends/portfolio/src/components/DemoInfoCard.tsx frontends/portfolio/src/components/SidebarNav.tsx frontends/portfolio/src/components/Icon.tsx
git commit -m "feat(portfolio): apply mono style to Me/Changelog/Announcement/Demo pages"
```

---

## Task 10:滚动入场动效(useScrollReveal)

**Files:**
- Create: `frontends/portfolio/src/hooks/useScrollReveal.ts`
- Modify: `frontends/portfolio/src/styles/texture.css`(reveal 初末态)
- Modify: 作品网格容器(`Home.tsx`)与各页 section 容器,挂 `data-reveal`

**Interfaces:**
- Produces:`useScrollReveal()` —— 挂载后用 `IntersectionObserver` 给带 `[data-reveal]` 的元素加 `.is-revealed`。

- [ ] **Step 1:追加 reveal CSS 到 `texture.css`**

```css
[data-reveal] { opacity: 0; transform: translateY(8px); transition: opacity .5s ease-out, transform .5s ease-out; }
[data-reveal].is-revealed { opacity: 1; transform: none; }
@media (prefers-reduced-motion: reduce) { [data-reveal] { opacity: 1; transform: none; } }
```

- [ ] **Step 2:创建 `useScrollReveal.ts`**

```ts
import { useEffect } from 'react'

export function useScrollReveal() {
  useEffect(() => {
    const els = Array.from(document.querySelectorAll('[data-reveal]'))
    if (!('IntersectionObserver' in window) || els.length === 0) {
      els.forEach((e) => e.classList.add('is-revealed'))
      return
    }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) { en.target.classList.add('is-revealed'); io.unobserve(en.target) }
      })
    }, { threshold: 0.12 })
    els.forEach((e) => io.observe(e))
    return () => io.disconnect()
  }, [])
}
```

- [ ] **Step 3:在 Home(及各页根组件)调用 hook + 给 section 加 `data-reveal`**

在 `Home.tsx` 组件体内调用 `useScrollReveal()`;给「精选作品」`<section>` 和每个 `<WorkCard>` 外层(或网格容器)加 `data-reveal`。
> 注意:hook 在挂载时查询一次 DOM;首页内容是静态渲染,挂载即存在,可行。若某页内容异步加载,改为在该页单独调用。

- [ ] **Step 4:构建 + 视觉验证 + 提交**

Run: `cd frontends/portfolio && npm run build`(成功);访问首页向下滚,作品区应淡入上移一次。
```bash
git add frontends/portfolio/src/hooks/useScrollReveal.ts frontends/portfolio/src/styles/texture.css frontends/portfolio/src/pages/Home.tsx
git commit -m "feat(portfolio): scroll-reveal entrance animation via IntersectionObserver"
```

---

## Task 11:全站验证 + 收尾

**Files:** 无新增,仅验证与文档。

- [ ] **Step 1:全量构建**

Run: `cd frontends/portfolio && npm run build`
Expected: 成功,无 TS 错误。

- [ ] **Step 2:从 worktree 重建 Docker stack 并验证所有路由**

```bash
cd "$HOME/Desktop/ai-demos/.claude/worktrees/feat+portfolio-ui-redesign"
bash deploy/build-frontends.sh
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml up -d --no-build
for p in / /me /changelog /rag/ /fc/ /nexus/ /doctomd/ /learn/; do
  curl -s -o /dev/null -w "%{http_code} $p\n" http://127.0.0.1:8080$p; done
```
Expected:全部 `200`。确认 `:8080` 服务的 index JS 指纹 = 最新 worktree dist。

- [ ] **Step 3:逐页人工目视确认**(亮/暗主题各看一遍)
  - 首页:hero(glitch/打字机/终端)、作品卡四特效、滚动入场。
  - `/me`、`/changelog`、各 demo 页、`/learn`:统一黑白风、等宽元信息、发丝边框。
  - 主题切换器:mono-light/mono/旧三主题均可切且不崩。

- [ ] **Step 4:更新 redesign 进度账本与 PROJECT-STATE**

在 worktree `.superpowers/sdd/progress.md` 追加本次重构完成记录;按需更新 `docs/PROJECT-STATE.md`。
```bash
git add docs/PROJECT-STATE.md .superpowers/sdd/progress.md
git commit -m "docs: record mono tech redesign completion"
```

- [ ] **Step 5:交付选择(合并 + 部署)**

由用户确认满意后:用 `superpowers:finishing-a-development-branch` 决定合并方式(合并 worktree 分支回 master、推 GitHub、重新部署首尔服务器)。**部署为对外操作,执行前须用户明确同意。**

---

## Self-Review(对照 spec 检查)

- **spec「最终确认决策」逐条覆盖**:① mono-light 默认 → Task 1;② 科技 hero(glitch/打字机/终端)→ Task 7;③ glitch 定稿参数 → Task 7 Step 1(参数逐字取自 spec);④ 纯黑白四特效 → Task 6 Step 1;⑤ Lucide 可替换 → Task 5(集中映射表);⑥ 旧主题留档 → Task 1(ALL_THEMES 保留)。全部有对应任务。
- **质感层 / 字体 / 等宽元信息 / 无障碍**:Task 2/3/6/7/10 均含 `prefers-reduced-motion` 降级;元信息等宽贯穿 Task 6/8/9。
- **类型一致性**:`IconName`(Task 5 定义)在 Task 6/9 消费一致;`Work.icon: IconName` / `Work.index: string` 全程一致;`Tag` 去 `color` prop 后,Task 6 改定义、Task 9 改调用方,无遗漏(Task 6 Step 4 / Task 9 Step 4 显式扫描旧用法)。
- **已知风险**:Task 5 故意留下 WorkCard 类型错误,Task 6 修复 —— 已在两处显式标注,避免误判构建失败。
