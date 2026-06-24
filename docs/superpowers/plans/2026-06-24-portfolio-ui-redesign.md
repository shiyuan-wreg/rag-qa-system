# ai-demos 门户外壳 UI 升级实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 ai-demos 的 React 门户外壳从极简网格升级为具备层次感、统一侧边栏、页面级更新公告、主题切换器(浅色/深蓝/赛博绿)和 iframe 加载反馈的专业作品集门户。

**Architecture:** 以 CSS 变量设计令牌为基础,通过 `data-theme` 属性切换三套主题;React 组件按职责拆分(Hero/卡片/侧边栏/iframe 骨架/主题切换);页面级数据(作品、changelog、学习目录)集中在 `src/data/`;所有 UI 颜色走 Tailwind 映射后的 CSS 变量,确保主题切换即时生效。

**Tech Stack:** React 18 + TypeScript + Vite + Tailwind CSS 3 + react-router-dom 6;构建验证用 `npm run build` 和 `tsc --noEmit`;Docker 验证用 `docker compose`。

## Global Constraints

- **不引入新依赖**: 不使用 `framer-motion`、`lucide-react` 等额外库(除非任务明确说明)。图标用纯字符或内联 SVG;动画用 CSS transition/keyframes。
- **颜色必须走 CSS 变量**: 所有背景、文字、边框、阴影颜色使用 `theme.css` 中定义的变量,通过 Tailwind `extend.colors` 映射。
- **主题持久化**: 用户选择保存到 `localStorage` 的 `ai-demos-theme` 键,刷新后恢复;默认 `light`。
- **保持路由不变**: `/ /rag /fc /nexus /learn /doctomd /me` 路径不变,不修改 nginx/Docker 配置。
- **移动端先简化**: 导航折叠为汉堡菜单,侧边栏垂直堆叠,不做抽屉。
- **每个任务独立可测**: 每个任务结束后运行 `npm run build` 或 `tsc --noEmit` 必须无错。
- **频繁提交**: 每个任务结束后单独 `git commit`,commit message 用中文或英文均可,但需描述清楚。

---

## 前置准备(不单独成任务,每个任务前检查)

- 工作目录: `C:\Users\hzs17\Desktop\ai-demos\frontends\portfolio`
- 确认 Node 版本: `node -v` 应输出 v20.x
- 安装依赖(若未安装): `npm install`
- 所有新增文件放在 `frontends/portfolio/src/` 下对应目录
- 运行命令前确保在 `frontends/portfolio` 目录

---

## Task 1: 主题系统基础(theme.css + Tailwind 映射 + useTheme + ThemeToggle)

**Files:**
- Create: `frontends/portfolio/src/styles/theme.css`
- Modify: `frontends/portfolio/src/styles.css`
- Modify: `frontends/portfolio/tailwind.config.js`
- Create: `frontends/portfolio/src/hooks/useTheme.ts`
- Create: `frontends/portfolio/src/components/ThemeToggle.tsx`
- Modify: `frontends/portfolio/src/main.tsx`

**Interfaces:**
- `useTheme()` returns `{ theme: 'light' | 'deepblue' | 'cyber', setTheme(t): void }`
- `ThemeToggle` is a React component with no props.
- Theme names are exported as `export type Theme = 'light' | 'deepblue' | 'cyber'`.

- [ ] **Step 1: 创建 `styles/theme.css`,写入三套主题变量**

```css
:root,
[data-theme="light"] {
  --bg-base: #ffffff;
  --bg-soft: #f8fafc;
  --bg-hero: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);

  --surface-default: #ffffff;
  --surface-raised: #ffffff;
  --surface-hover: #f1f5f9;

  --border-default: #e2e8f0;
  --border-subtle: #f1f5f9;

  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-tertiary: #64748b;
  --text-muted: #94a3b8;
  --text-link: #2563eb;

  --accent-primary: #0f172a;
  --accent-primary-text: #ffffff;
  --accent-secondary-bg: #eff6ff;
  --accent-secondary-text: #1d4ed8;

  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04);
  --shadow-md: 0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04);

  --font-sans: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
}

[data-theme="deepblue"] {
  --bg-base: #0f172a;
  --bg-soft: #1e293b;
  --bg-hero: linear-gradient(180deg, #0f172a 0%, #1e3a8a 100%);

  --surface-default: #1e293b;
  --surface-raised: #334155;
  --surface-hover: #27354f;

  --border-default: #334155;
  --border-subtle: #1e293b;

  --text-primary: #f8fafc;
  --text-secondary: #cbd5e1;
  --text-tertiary: #94a3b8;
  --text-muted: #64748b;
  --text-link: #60a5fa;

  --accent-primary: #2563eb;
  --accent-primary-text: #ffffff;
  --accent-secondary-bg: rgba(37, 99, 235, 0.15);
  --accent-secondary-text: #60a5fa;

  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.3);
}

[data-theme="cyber"] {
  --bg-base: #09090b;
  --bg-soft: #18181b;
  --bg-hero: linear-gradient(180deg, #09090b 0%, #18181b 100%);

  --surface-default: #18181b;
  --surface-raised: #27272a;
  --surface-hover: #3f3f46;

  --border-default: #27272a;
  --border-subtle: #18181b;

  --text-primary: #a3e635;
  --text-secondary: #d4d4d8;
  --text-tertiary: #a1a1aa;
  --text-muted: #71717a;
  --text-link: #a3e635;

  --accent-primary: #a3e635;
  --accent-primary-text: #09090b;
  --accent-secondary-bg: rgba(163, 230, 53, 0.12);
  --accent-secondary-text: #a3e635;

  --shadow-sm: 0 0 8px rgba(163, 230, 53, 0.08);
  --shadow-md: 0 0 16px rgba(163, 230, 53, 0.12);

  --font-sans: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "PingFang SC", "Microsoft YaHei", monospace;
}

:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-16: 64px;

  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 999px;

  --max-content: 1100px;
}

html {
  background-color: var(--bg-base);
  color: var(--text-primary);
  font-family: var(--font-sans);
}
```

- [ ] **Step 2: 修改 `styles.css`,引入 theme.css**

```css
@import './styles/theme.css';

@tailwind base;
@tailwind components;
@tailwind utilities;
```

- [ ] **Step 3: 修改 `tailwind.config.js`,映射 CSS 变量为 Tailwind 类名**

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        base: 'var(--bg-base)',
        soft: 'var(--bg-soft)',
        surface: {
          DEFAULT: 'var(--surface-default)',
          raised: 'var(--surface-raised)',
          hover: 'var(--surface-hover)',
        },
        border: {
          DEFAULT: 'var(--border-default)',
          subtle: 'var(--border-subtle)',
        },
        primary: 'var(--text-primary)',
        secondary: 'var(--text-secondary)',
        tertiary: 'var(--text-tertiary)',
        muted: 'var(--text-muted)',
        link: 'var(--text-link)',
        accent: {
          DEFAULT: 'var(--accent-primary)',
          text: 'var(--accent-primary-text)',
          secondary: {
            bg: 'var(--accent-secondary-bg)',
            text: 'var(--accent-secondary-text)',
          },
        },
      },
      backgroundImage: {
        hero: 'var(--bg-hero)',
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        md: 'var(--shadow-md)',
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
        xl: 'var(--radius-xl)',
        full: 'var(--radius-full)',
      },
      spacing: {
        18: '4.5rem',
        22: '5.5rem',
      },
      maxWidth: {
        content: 'var(--max-content)',
      },
      fontFamily: {
        sans: 'var(--font-sans)',
        mono: 'var(--font-mono)',
      },
    },
  },
  plugins: [],
}
```

- [ ] **Step 4: 创建 `hooks/useTheme.ts`**

```ts
import { useEffect, useState } from 'react'

export type Theme = 'light' | 'deepblue' | 'cyber'

const STORAGE_KEY = 'ai-demos-theme'
const DEFAULT_THEME: Theme = 'light'

function getInitialTheme(): Theme {
  if (typeof window === 'undefined') return DEFAULT_THEME
  const stored = window.localStorage.getItem(STORAGE_KEY) as Theme | null
  if (stored && ['light', 'deepblue', 'cyber'].includes(stored)) return stored
  return DEFAULT_THEME
}

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(getInitialTheme)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    window.localStorage.setItem(STORAGE_KEY, theme)
  }, [theme])

  const setTheme = (t: Theme) => setThemeState(t)

  return { theme, setTheme }
}
```

- [ ] **Step 5: 创建 `components/ThemeToggle.tsx`**

```tsx
import { useTheme, type Theme } from '../hooks/useTheme'

const THEMES: { key: Theme; label: string }[] = [
  { key: 'light', label: '浅色' },
  { key: 'deepblue', label: '深蓝' },
  { key: 'cyber', label: '赛博' },
]

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <div className="inline-flex items-center gap-1 rounded-lg border border-border p-1 bg-soft">
      {THEMES.map((t) => {
        const active = theme === t.key
        return (
          <button
            key={t.key}
            onClick={() => setTheme(t.key)}
            className={[
              'px-2.5 py-1 text-xs font-medium rounded-md transition-colors',
              active
                ? 'bg-accent text-accent-text'
                : 'text-tertiary hover:text-primary hover:bg-surface-hover',
            ].join(' ')}
            aria-pressed={active}
          >
            {t.label}
          </button>
        )
      })}
    </div>
  )
}
```

- [ ] **Step 6: 修改 `main.tsx`,确保 html 初始化时就有主题属性**

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './styles.css'

const stored = typeof window !== 'undefined'
  ? (window.localStorage.getItem('ai-demos-theme') as 'light' | 'deepblue' | 'cyber' | null)
  : null
if (stored && ['light', 'deepblue', 'cyber'].includes(stored)) {
  document.documentElement.setAttribute('data-theme', stored)
} else {
  document.documentElement.setAttribute('data-theme', 'light')
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
```

- [ ] **Step 7: 临时验证:把 ThemeToggle 放进 App.tsx 最上方**

临时修改 `App.tsx`:

```tsx
import ThemeToggle from './components/ThemeToggle'

export default function App() {
  return (
    <div className="min-h-screen bg-base">
      <ThemeToggle />
      {/* existing routes */}
    </div>
  )
}
```

- [ ] **Step 8: 运行 TypeScript 检查**

Run: `cd C:\Users\hzs17\Desktop\ai-demos\frontends\portfolio && npx tsc --noEmit`
Expected: 无错误(no errors)

- [ ] **Step 9: 运行开发服务器验证主题切换**

Run: `npm run dev`
Open: http://127.0.0.1:5173/
Expected: 能看到“浅色 / 深蓝 / 赛博”三个按钮,点击后页面背景色和文字色会变化。刷新后保持选择。

- [ ] **Step 10: 提交**

```bash
cd C:\Users\hzs17\Desktop\ai-demos
git add frontends/portfolio/src/styles/theme.css frontends/portfolio/src/styles.css frontends/portfolio/tailwind.config.js frontends/portfolio/src/hooks/useTheme.ts frontends/portfolio/src/components/ThemeToggle.tsx frontends/portfolio/src/main.tsx
git commit -m "feat(portfolio): add theme system with light/deepblue/cyber tokens and ThemeToggle"
```

---

## Task 2: 基础可复用组件(IconBox / Tag / Button / PageTransition)

**Files:**
- Create: `frontends/portfolio/src/components/IconBox.tsx`
- Create: `frontends/portfolio/src/components/Tag.tsx`
- Create: `frontends/portfolio/src/components/Button.tsx`
- Create: `frontends/portfolio/src/components/PageTransition.tsx`

**Interfaces:**
- `IconBox({ letter, bg, text })`
- `Tag({ children, color = 'blue' })` where color maps to a palette class.
- `Button({ children, variant = 'primary', ...props })` extends button attributes.
- `PageTransition({ children })` wraps a page with fade-in CSS animation.

- [ ] **Step 1: 创建 `components/IconBox.tsx`**

```tsx
export interface IconBoxProps {
  letter: string
  bg: string
  text: string
}

export default function IconBox({ letter, bg, text }: IconBoxProps) {
  return (
    <div
      className="w-10 h-10 rounded-md flex items-center justify-center text-sm font-bold shrink-0"
      style={{ backgroundColor: bg, color: text }}
    >
      {letter}
    </div>
  )
}
```

- [ ] **Step 2: 创建 `components/Tag.tsx`**

```tsx
const PALETTE: Record<string, { bg: string; text: string }> = {
  blue: { bg: '#eff6ff', text: '#1d4ed8' },
  green: { bg: '#f0fdf4', text: '#15803d' },
  purple: { bg: '#faf5ff', text: '#7e22ce' },
  cyan: { bg: '#ecfeff', text: '#0e7490' },
  orange: { bg: '#fff7ed', text: '#c2410c' },
  red: { bg: '#fef2f2', text: '#b91c1c' },
  slate: { bg: '#f1f5f9', text: '#475569' },
}

export default function Tag({ children, color = 'blue' }: { children: React.ReactNode; color?: string }) {
  const p = PALETTE[color] ?? PALETTE.blue
  return (
    <span
      className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
      style={{ backgroundColor: p.bg, color: p.text }}
    >
      {children}
    </span>
  )
}
```

- [ ] **Step 3: 创建 `components/Button.tsx`**

```tsx
import { type ButtonHTMLAttributes } from 'react'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary'
}

export default function Button({ children, variant = 'primary', className = '', ...props }: ButtonProps) {
  const base = 'inline-flex items-center justify-center px-5 py-2.5 rounded-full text-sm font-medium transition-colors'
  const styles =
    variant === 'primary'
      ? 'bg-accent text-accent-text hover:opacity-90'
      : 'bg-surface text-primary border border-border hover:bg-surface-hover'
  return (
    <button className={`${base} ${styles} ${className}`} {...props}>
      {children}
    </button>
  )
}
```

- [ ] **Step 4: 创建 `components/PageTransition.tsx`**

```tsx
import { useEffect, useState, type ReactNode } from 'react'

export default function PageTransition({ children }: { children: ReactNode }) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  return (
    <div
      className="transition-all duration-200 ease-out"
      style={{
        opacity: mounted ? 1 : 0,
        transform: mounted ? 'translateY(0)' : 'translateY(8px)',
      }}
    >
      {children}
    </div>
  )
}
```

- [ ] **Step 5: 运行 TypeScript 检查**

Run: `npx tsc --noEmit`
Expected: 无错误

- [ ] **Step 6: 提交**

```bash
git add frontends/portfolio/src/components/IconBox.tsx frontends/portfolio/src/components/Tag.tsx frontends/portfolio/src/components/Button.tsx frontends/portfolio/src/components/PageTransition.tsx
git commit -m "feat(portfolio): add reusable IconBox, Tag, Button, PageTransition components"
```

---

## Task 3: 数据层升级(works / changelogs / learnNav)

**Files:**
- Modify: `frontends/portfolio/src/data/works.ts`
- Create: `frontends/portfolio/src/data/changelogs.ts`
- Create: `frontends/portfolio/src/data/learnNav.ts`

**Interfaces:**
- `Work` 增加 `icon` 和 `changelog`。
- `ChangelogEntry` 类型: `{ version: string; date: string; items: string[] }`。
- `LearnNavItem` 类型用于侧边栏树形结构。

- [ ] **Step 1: 修改 `data/works.ts`**

```ts
export type Work = {
  slug: string
  title: string
  desc: string
  tech: string[]
  github?: string
  path: string
  icon: { letter: string; bg: string; text: string }
  changelog: { version: string; date: string; items: string[] }[]
}

export const WORKS: Work[] = [
  {
    slug: 'rag',
    title: 'RAG 文档问答',
    desc: '基于检索增强生成的私有知识库问答。',
    tech: ['RAG', 'Chroma', '通义千问', 'FastAPI'],
    path: '/rag',
    icon: { letter: 'R', bg: '#eff6ff', text: '#1d4ed8' },
    changelog: [
      { version: '0.1', date: '2026-06-22', items: ['RAG 文档问答 Demo 上线'] },
    ],
  },
  {
    slug: 'fc',
    title: 'Function Calling Agent',
    desc: '大模型自动决策并调用工具完成任务。',
    tech: ['Function Calling', '通义千问', 'FastAPI'],
    path: '/fc',
    icon: { letter: 'F', bg: '#faf5ff', text: '#7e22ce' },
    changelog: [
      { version: '0.1', date: '2026-06-22', items: ['Function Calling Agent Demo 上线'] },
    ],
  },
  {
    slug: 'nexus',
    title: 'Nexus Multi-Agent 工作流',
    desc: '多 Agent 协作的 AI 工作流助手，实时展示思考过程。',
    tech: ['Multi-Agent', 'FastAPI', 'SSE', '通义千问'],
    path: '/nexus',
    icon: { letter: 'N', bg: '#ecfeff', text: '#0e7490' },
    changelog: [
      { version: '0.1', date: '2026-06-22', items: ['Nexus Multi-Agent 工作流 Demo 上线'] },
    ],
  },
  {
    slug: 'learn',
    title: 'Nexus 交互式学习站',
    desc: 'LLM/Agent/RAG 的交互式课程与测验。',
    tech: ['React', 'Vite', 'TypeScript'],
    path: '/learn',
    icon: { letter: 'L', bg: '#f0fdf4', text: '#15803d' },
    changelog: [
      { version: '0.2', date: '2026-06-24', items: ['学习站接入门户统一侧边栏'] },
      { version: '0.1', date: '2026-06-22', items: ['Nexus 交互式学习站上线'] },
    ],
  },
  {
    slug: 'doctomd',
    title: 'DocHub Markdown 文档站',
    desc: '把 Markdown 文集一键转成可浏览的 HTML 文档站。',
    tech: ['FastAPI', 'Markdown', 'Jinja2'],
    path: '/doctomd',
    icon: { letter: 'D', bg: '#fff7ed', text: '#c2410c' },
    changelog: [
      { version: '0.1', date: '2026-06-23', items: ['DocHub Markdown 文档站上线'] },
    ],
  },
]
```

- [ ] **Step 2: 创建 `data/changelogs.ts`**

```ts
export interface ChangelogEntry {
  version: string
  date: string
  items: string[]
}

export const PAGE_CHANGELOGS: Record<string, ChangelogEntry[]> = {
  home: [
    {
      version: '0.2',
      date: '2026-06-24',
      items: ['新增 Hero 区与统一侧边栏', '增加页面级更新公告', '新增主题切换器', 'iframe 加载骨架屏'],
    },
    { version: '0.1', date: '2026-06-22', items: ['作品网格首页上线'] },
  ],
  rag: [{ version: '0.1', date: '2026-06-22', items: ['RAG 文档问答 Demo 上线'] }],
  fc: [{ version: '0.1', date: '2026-06-22', items: ['Function Calling Agent Demo 上线'] }],
  nexus: [{ version: '0.1', date: '2026-06-22', items: ['Nexus Multi-Agent 工作流 Demo 上线'] }],
  learn: [
    { version: '0.2', date: '2026-06-24', items: ['学习站接入门户统一侧边栏'] },
    { version: '0.1', date: '2026-06-22', items: ['Nexus 交互式学习站上线'] },
  ],
  doctomd: [{ version: '0.1', date: '2026-06-23', items: ['DocHub Markdown 文档站上线'] }],
  me: [{ version: '0.2', date: '2026-06-24', items: ['个人页上线'] }],
}
```

- [ ] **Step 3: 创建 `data/learnNav.ts`**

从 `frontends/nexus-learning-web/src/data/course.ts` 复制模块/课时标题(不移动学习站源码)。

```ts
export interface LearnNavModule {
  id: string
  title: string
  lessons: { id: string; title: string }[]
}

export const LEARN_NAV: LearnNavModule[] = [
  {
    id: 'fundamentals',
    title: '模块一：LLM 与 Agent 基础',
    lessons: [
      { id: 'llm-basics', title: 'LLM 的能力边界与工程约束' },
      { id: 'agent-intro', title: 'Agent 架构与 ReAct 范式' },
    ],
  },
  {
    id: 'rag-tools',
    title: '模块二：RAG 与工具',
    lessons: [
      { id: 'rag-overview', title: 'RAG 流程与向量数据库' },
      { id: 'tools', title: 'Function Calling 与工具设计' },
    ],
  },
  {
    id: 'nexus-arch',
    title: '模块三：Nexus 架构实现',
    lessons: [
      { id: 'multi-agent', title: 'Multi-Agent 协作模式' },
      { id: 'sse-ui', title: 'SSE 实时流与前端展示' },
    ],
  },
  {
    id: 'engineering',
    title: '模块四：工程化与求职',
    lessons: [
      { id: 'deployment', title: 'Docker 与云部署' },
      { id: 'career', title: '项目包装与面试准备' },
    ],
  },
]
```

- [ ] **Step 4: 运行 TypeScript 检查**

Run: `npx tsc --noEmit`
Expected: 无错误

- [ ] **Step 5: 提交**

```bash
git add frontends/portfolio/src/data/works.ts frontends/portfolio/src/data/changelogs.ts frontends/portfolio/src/data/learnNav.ts
git commit -m "feat(portfolio): add icon/changelog to works and create changelogs/learnNav data"
```

---

## Task 4: 导航栏与页面级更新公告

**Files:**
- Modify: `frontends/portfolio/src/components/NavBar.tsx`
- Create: `frontends/portfolio/src/components/PageChangelog.tsx`

**Interfaces:**
- `NavBar` 使用 `useLocation` 高亮当前页,右侧放 `ThemeToggle`,移动端有菜单按钮。
- `PageChangelog({ pageKey })` 读取 `PAGE_CHANGELOGS[pageKey]`,展示最新一条并可展开历史。

- [ ] **Step 1: 修改 `components/NavBar.tsx`**

```tsx
import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import ThemeToggle from './ThemeToggle'

const ITEMS = [
  { to: '/', label: '首页' },
  { to: '/rag', label: 'AI 作品' },
  { to: '/learn', label: '学习' },
  { to: '/me', label: '个人' },
]

export default function NavBar() {
  const { pathname } = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)

  const isActive = (to: string) => {
    if (to === '/') return pathname === '/'
    return pathname.startsWith(to)
  }

  return (
    <nav className="sticky top-0 z-50 bg-surface border-b border-border">
      <div className="max-w-content mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-md bg-accent text-accent-text flex items-center justify-center text-xs font-bold">
              AI
            </div>
            <span className="font-bold text-primary">个人集成学习网站</span>
          </Link>

          <div className="hidden md:flex items-center gap-6">
            {ITEMS.map((it) => (
              <Link
                key={it.to}
                to={it.to}
                className={`text-sm font-medium transition-colors ${
                  isActive(it.to) ? 'text-primary' : 'text-tertiary hover:text-primary'
                }`}
              >
                {it.label}
              </Link>
            ))}
            <ThemeToggle />
          </div>

          <div className="flex md:hidden items-center gap-3">
            <ThemeToggle />
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="p-2 rounded-md text-tertiary hover:bg-surface-hover"
              aria-label="切换菜单"
            >
              {mobileOpen ? '✕' : '☰'}
            </button>
          </div>
        </div>
      </div>

      {mobileOpen && (
        <div className="md:hidden border-t border-border bg-surface px-4 py-3 space-y-2">
          {ITEMS.map((it) => (
            <Link
              key={it.to}
              to={it.to}
              onClick={() => setMobileOpen(false)}
              className={`block text-sm font-medium ${
                isActive(it.to) ? 'text-primary' : 'text-tertiary'
              }`}
            >
              {it.label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  )
}
```

- [ ] **Step 2: 创建 `components/PageChangelog.tsx`**

```tsx
import { useState } from 'react'
import { PAGE_CHANGELOGS, type ChangelogEntry } from '../data/changelogs'

export default function PageChangelog({ pageKey }: { pageKey: string }) {
  const [expanded, setExpanded] = useState(false)
  const entries = PAGE_CHANGELOGS[pageKey]
  if (!entries || entries.length === 0) return null

  const latest = entries[0]

  return (
    <div className="bg-accent-secondary-bg border-b border-border-subtle">
      <div className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-2.5">
        <div className="flex items-start sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3 text-sm">
            <span className="shrink-0 px-2 py-0.5 rounded-full bg-accent text-accent-text text-xs font-semibold">
              v{latest.version}
            </span>
            <span className="text-accent-secondary-text">
              {latest.items.join(' · ')}
            </span>
          </div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-tertiary hover:text-primary whitespace-nowrap"
          >
            {expanded ? '收起历史' : '查看历史'}
          </button>
        </div>

        {expanded && (
          <div className="mt-3 pl-12 space-y-2 border-t border-border-subtle pt-3">
            {entries.map((e: ChangelogEntry) => (
              <div key={e.version} className="text-sm">
                <span className="font-semibold text-primary">v{e.version}</span>
                <span className="text-muted text-xs ml-2">{e.date}</span>
                <ul className="mt-1 ml-4 list-disc text-secondary">
                  {e.items.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
```

- [ ] **Step 3: 运行 TypeScript 检查**

Run: `npx tsc --noEmit`
Expected: 无错误

- [ ] **Step 4: 提交**

```bash
git add frontends/portfolio/src/components/NavBar.tsx frontends/portfolio/src/components/PageChangelog.tsx
git commit -m "feat(portfolio): redesign NavBar with ThemeToggle and add PageChangelog"
```

---

## Task 5: 侧边栏布局组件

**Files:**
- Create: `frontends/portfolio/src/components/SidebarNav.tsx`
- Create: `frontends/portfolio/src/components/SidebarLayout.tsx`

**Interfaces:**
- `SidebarNav({ items, activeKey })` renders a vertical list with icons and labels.
- `SidebarLayout({ sidebar, children })` renders the two-column layout.

- [ ] **Step 1: 创建 `components/SidebarNav.tsx`**

```tsx
import { Link } from 'react-router-dom'

export interface SidebarNavItem {
  key: string
  to: string
  label: string
  icon?: { letter: string; bg: string; text: string }
}

export default function SidebarNav({ items, activeKey }: { items: SidebarNavItem[]; activeKey: string }) {
  return (
    <nav className="space-y-1">
      {items.map((it) => {
        const active = activeKey === it.key
        return (
          <Link
            key={it.key}
            to={it.to}
            className={[
              'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
              active
                ? 'bg-soft text-primary'
                : 'text-tertiary hover:bg-soft hover:text-primary',
            ].join(' ')}
          >
            {it.icon && (
              <span
                className="w-6 h-6 rounded-md flex items-center justify-center text-[11px] font-bold shrink-0"
                style={{ backgroundColor: it.icon.bg, color: it.icon.text }}
              >
                {it.icon.letter}
              </span>
            )}
            {it.label}
          </Link>
        )
      })}
    </nav>
  )
}
```

- [ ] **Step 2: 创建 `components/SidebarLayout.tsx`**

```tsx
import { type ReactNode } from 'react'

export default function SidebarLayout({ sidebar, children }: { sidebar: ReactNode; children: ReactNode }) {
  return (
    <div className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div className="flex flex-col lg:flex-row gap-6">
        <aside className="lg:w-60 shrink-0">
          <div className="lg:sticky lg:top-20 bg-surface border border-border rounded-xl p-3 shadow-sm">
            {sidebar}
          </div>
        </aside>
        <main className="flex-1 min-w-0">{children}</main>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: 运行 TypeScript 检查**

Run: `npx tsc --noEmit`
Expected: 无错误

- [ ] **Step 4: 提交**

```bash
git add frontends/portfolio/src/components/SidebarNav.tsx frontends/portfolio/src/components/SidebarLayout.tsx
git commit -m "feat(portfolio): add SidebarNav and SidebarLayout components"
```

---

## Task 6: iframe 骨架屏与 Demo 信息卡

**Files:**
- Create: `frontends/portfolio/src/components/DemoInfoCard.tsx`
- Rewrite: `frontends/portfolio/src/components/DemoFrame.tsx`

**Interfaces:**
- `DemoInfoCard({ work })` shows title, desc, tech tags, source link.
- `DemoFrame({ src })` shows skeleton while iframe loads, then fades in.

- [ ] **Step 1: 创建 `components/DemoInfoCard.tsx`**

```tsx
import { Work } from '../data/works'
import Tag from './Tag'

const TAG_COLORS = ['blue', 'green', 'purple', 'cyan', 'orange', 'red', 'slate']

export default function DemoInfoCard({ work }: { work: Work }) {
  return (
    <div className="bg-surface border border-border rounded-xl p-5 shadow-sm">
      <h1 className="text-xl font-bold text-primary">{work.title}</h1>
      <p className="mt-2 text-sm text-secondary leading-relaxed">{work.desc}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {work.tech.map((t, idx) => (
          <Tag key={t} color={TAG_COLORS[idx % TAG_COLORS.length]}>
            {t}
          </Tag>
        ))}
      </div>
      {work.github && (
        <a
          href={work.github}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-4 inline-flex text-sm font-medium text-link hover:underline"
        >
          查看源码 →
        </a>
      )}
    </div>
  )
}
```

- [ ] **Step 2: 重写 `components/DemoFrame.tsx`**

```tsx
import { useState, useRef } from 'react'

export default function DemoFrame({ src, title }: { src: string; title: string }) {
  const [status, setStatus] = useState<'loading' | 'loaded' | 'error'>('loading')
  const timerRef = useRef<number | null>(null)

  const handleLoad = () => {
    if (timerRef.current) window.clearTimeout(timerRef.current)
    setStatus('loaded')
  }

  const handleError = () => {
    if (timerRef.current) window.clearTimeout(timerRef.current)
    setStatus('error')
  }

  const startLoad = () => {
    setStatus('loading')
    if (timerRef.current) window.clearTimeout(timerRef.current)
    timerRef.current = window.setTimeout(() => {
      if (status !== 'loaded') setStatus('error')
    }, 8000)
  }

  const reload = () => {
    startLoad()
    setStatus('loading')
  }

  return (
    <div className="relative flex-1 min-h-[60vh] lg:min-h-[70vh] bg-surface border border-border rounded-xl shadow-sm overflow-hidden">
      {status === 'loading' && (
        <div className="absolute inset-0 p-5 space-y-4">
          <div className="flex gap-3">
            <div className="h-8 w-32 bg-soft rounded-md shimmer" />
            <div className="h-8 w-24 bg-soft rounded-md shimmer" />
          </div>
          <div className="h-40 bg-soft rounded-lg shimmer" />
          <div className="space-y-2">
            <div className="h-4 bg-soft rounded w-3/4 shimmer" />
            <div className="h-4 bg-soft rounded w-1/2 shimmer" />
          </div>
        </div>
      )}

      {status === 'error' && (
        <div className="absolute inset-0 flex flex-col items-center justify-center p-6 text-center">
          <p className="text-primary font-medium">Demo 加载失败或超时</p>
          <p className="text-secondary text-sm mt-1">请检查网络或刷新重试</p>
          <div className="mt-4 flex gap-3">
            <button
              onClick={reload}
              className="px-4 py-2 rounded-full bg-accent text-accent-text text-sm font-medium hover:opacity-90"
            >
              重试
            </button>
            <a
              href="/"
              className="px-4 py-2 rounded-full border border-border text-primary text-sm font-medium hover:bg-surface-hover"
            >
              返回首页
            </a>
          </div>
        </div>
      )}

      <iframe
        key={status === 'error' ? 'error' : 'frame'}
        title={title}
        src={src}
        onLoad={handleLoad}
        onError={handleError}
        className="w-full h-full border-0 transition-opacity duration-300"
        style={{ opacity: status === 'loaded' ? 1 : 0 }}
      />

      <style>{`
        .shimmer {
          background: linear-gradient(90deg, var(--surface-hover) 25%, var(--surface-default) 50%, var(--surface-hover) 75%);
          background-size: 200% 100%;
          animation: shimmer 1.5s infinite;
        }
        @keyframes shimmer {
          0% { background-position: 200% 0; }
          100% { background-position: -200% 0; }
        }
      `}</style>
    </div>
  )
}
```

- [ ] **Step 3: 运行 TypeScript 检查**

Run: `npx tsc --noEmit`
Expected: 无错误

- [ ] **Step 4: 提交**

```bash
git add frontends/portfolio/src/components/DemoInfoCard.tsx frontends/portfolio/src/components/DemoFrame.tsx
git commit -m "feat(portfolio): add DemoInfoCard and skeleton-loading DemoFrame"
```

---

## Task 7: 首页升级(Home + WorkCard + 搜索)

**Files:**
- Create: `frontends/portfolio/src/components/WorkCard.tsx`
- Rewrite: `frontends/portfolio/src/pages/Home.tsx`

**Interfaces:**
- `WorkCard({ work })` renders the clickable project card with icon, title, desc, tags.
- `Home` renders Hero + search + filtered WorkCard grid.

- [ ] **Step 1: 创建 `components/WorkCard.tsx`**

```tsx
import { Link } from 'react-router-dom'
import { Work } from '../data/works'
import IconBox from './IconBox'
import Tag from './Tag'

const TAG_COLORS = ['blue', 'green', 'purple', 'cyan', 'orange', 'red', 'slate']

export default function WorkCard({ work }: { work: Work }) {
  return (
    <Link
      to={work.path}
      className="group block bg-surface border border-border rounded-xl p-5 shadow-sm transition-all hover:shadow-md hover:border-border"
    >
      <div className="flex items-start gap-4">
        <IconBox letter={work.icon.letter} bg={work.icon.bg} text={work.icon.text} />
        <div className="min-w-0">
          <h3 className="font-bold text-primary group-hover:text-link transition-colors">
            {work.title}
          </h3>
          <p className="mt-1 text-sm text-secondary line-clamp-2">{work.desc}</p>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {work.tech.map((t, idx) => (
          <Tag key={t} color={TAG_COLORS[idx % TAG_COLORS.length]}>
            {t}
          </Tag>
        ))}
      </div>
    </Link>
  )
}
```

- [ ] **Step 2: 重写 `pages/Home.tsx`**

```tsx
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import Button from '../components/Button'
import WorkCard from '../components/WorkCard'
import { WORKS } from '../data/works'
import { PAGE_CHANGELOGS } from '../data/changelogs'

export default function Home() {
  const [query, setQuery] = useState('')

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return WORKS
    return WORKS.filter(
      (w) =>
        w.title.toLowerCase().includes(q) ||
        w.desc.toLowerCase().includes(q) ||
        w.tech.some((t) => t.toLowerCase().includes(q)),
    )
  }, [query])

  const latestHome = PAGE_CHANGELOGS.home[0]

  return (
    <div>
      <section className="bg-hero border-b border-border-subtle">
        <div className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-20 text-center">
          {latestHome && (
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-secondary-bg text-accent-secondary-text text-xs font-semibold mb-6">
              <span>v{latestHome.version}</span>
              <span>·</span>
              <span>{latestHome.items[0]}</span>
            </div>
          )}
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-extrabold text-primary tracking-tight">
            探索 AI 与 Agent 的工程实践
          </h1>
          <p className="mt-5 text-base md:text-lg text-secondary max-w-2xl mx-auto leading-relaxed">
            从 RAG、Function Calling 到 Multi-Agent 工作流，把分散的实验整合成一个可运行的作品集门户。
          </p>
          <div className="mt-8 flex items-center justify-center gap-3">
            <Link to="/rag">
              <Button>浏览作品</Button>
            </Link>
            <Link to="/learn">
              <Button variant="secondary">开始学习</Button>
            </Link>
          </div>
        </div>
      </section>

      <section className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <h2 className="text-xl font-bold text-primary">精选作品</h2>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="搜索作品..."
            className="w-full sm:w-64 px-3 py-2 text-sm rounded-lg border border-border bg-surface text-primary placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-link/30"
          />
        </div>

        {filtered.length === 0 ? (
          <div className="text-center py-12 text-secondary text-sm">
            没有找到匹配“{query}”的作品
          </div>
        ) : (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((w) => (
              <WorkCard key={w.slug} work={w} />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
```

- [ ] **Step 3: 运行 TypeScript 检查**

Run: `npx tsc --noEmit`
Expected: 无错误

- [ ] **Step 4: 提交**

```bash
git add frontends/portfolio/src/components/WorkCard.tsx frontends/portfolio/src/pages/Home.tsx
git commit -m "feat(portfolio): redesign Home with Hero, search, and WorkCard grid"
```

---

## Task 8: Demo 页升级

**Files:**
- Modify: `frontends/portfolio/src/pages/Demo.tsx`

**Interfaces:**
- `Demo({ slug, src })` uses `SidebarLayout`, `SidebarNav`, `DemoInfoCard`, `DemoFrame`.

- [ ] **Step 1: 重写 `pages/Demo.tsx`**

```tsx
import { WORKS } from '../data/works'
import DemoFrame from '../components/DemoFrame'
import DemoInfoCard from '../components/DemoInfoCard'
import SidebarLayout from '../components/SidebarLayout'
import SidebarNav from '../components/SidebarNav'
import type { SidebarNavItem } from '../components/SidebarNav'
import PageChangelog from '../components/PageChangelog'
import PageTransition from '../components/PageTransition'

export default function Demo({ slug, src }: { slug: string; src: string }) {
  const work = WORKS.find((w) => w.slug === slug)!
  const navItems: SidebarNavItem[] = WORKS.filter((w) => w.slug !== 'learn').map((w) => ({
    key: w.slug,
    to: w.path,
    label: w.title,
    icon: w.icon,
  }))

  return (
    <PageTransition>
      <PageChangelog pageKey={slug} />
      <SidebarLayout
        sidebar={
          <div>
            <div className="text-xs font-semibold text-muted uppercase tracking-wider mb-3 px-3">
              作品导航
            </div>
            <SidebarNav items={navItems} activeKey={slug} />
          </div>
        }
      >
        <div className="space-y-4">
          <DemoInfoCard work={work} />
          <DemoFrame src={src} title={work.title} />
        </div>
      </SidebarLayout>
    </PageTransition>
  )
}
```

- [ ] **Step 2: 运行 TypeScript 检查**

Run: `npx tsc --noEmit`
Expected: 无错误

- [ ] **Step 3: 提交**

```bash
git add frontends/portfolio/src/pages/Demo.tsx
git commit -m "feat(portfolio): redesign Demo page with SidebarLayout and DemoFrame"
```

---

## Task 9: 学习入口页升级

**Files:**
- Modify: `frontends/portfolio/src/pages/Learn.tsx`

**Interfaces:**
- `Learn` wraps `/learn/` in iframe with course directory sidebar.

- [ ] **Step 1: 重写 `pages/Learn.tsx`**

```tsx
import DemoFrame from '../components/DemoFrame'
import SidebarLayout from '../components/SidebarLayout'
import SidebarNav from '../components/SidebarNav'
import PageChangelog from '../components/PageChangelog'
import PageTransition from '../components/PageTransition'
import { LEARN_NAV } from '../data/learnNav'

export default function Learn() {
  const navItems = LEARN_NAV.flatMap((m) => [
    { key: m.id, to: `/learn/#${m.id}`, label: m.title },
    ...m.lessons.map((l) => ({
      key: l.id,
      to: `/learn/#${l.id}`,
      label: l.title,
    })),
  ])

  return (
    <PageTransition>
      <PageChangelog pageKey="learn" />
      <SidebarLayout
        sidebar={
          <div>
            <div className="text-xs font-semibold text-muted uppercase tracking-wider mb-3 px-3">
              课程目录
            </div>
            <SidebarNav items={navItems} activeKey="learn" />
          </div>
        }
      >
        <DemoFrame src="/learn/" title="Nexus 交互式学习站" />
      </SidebarLayout>
    </PageTransition>
  )
}
```

- [ ] **Step 2: 运行 TypeScript 检查**

Run: `npx tsc --noEmit`
Expected: 无错误

- [ ] **Step 3: 提交**

```bash
git add frontends/portfolio/src/pages/Learn.tsx
git commit -m "feat(portfolio): wrap Learn in iframe with course directory sidebar"
```

---

## Task 10: 个人页升级

**Files:**
- Create: `frontends/portfolio/src/hooks/useDocumentTitle.ts`
- Modify: `frontends/portfolio/src/pages/Me.tsx`

**Interfaces:**
- `useDocumentTitle(title, hiddenTitle?)` sets page title and blur/focus behavior.

- [ ] **Step 1: 创建 `hooks/useDocumentTitle.ts`**

```ts
import { useEffect } from 'react'

export function useDocumentTitle(title: string, hiddenTitle = '快回来继续探索 AI 作品!') {
  useEffect(() => {
    const original = document.title
    document.title = title

    const onVisibilityChange = () => {
      document.title = document.hidden ? hiddenTitle : title
    }

    document.addEventListener('visibilitychange', onVisibilityChange)
    return () => {
      document.removeEventListener('visibilitychange', onVisibilityChange)
      document.title = original
    }
  }, [title, hiddenTitle])
}
```

- [ ] **Step 2: 重写 `pages/Me.tsx`**

```tsx
import SidebarLayout from '../components/SidebarLayout'
import SidebarNav from '../components/SidebarNav'
import Tag from '../components/Tag'
import PageChangelog from '../components/PageChangelog'
import PageTransition from '../components/PageTransition'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { PAGE_CHANGELOGS } from '../data/changelogs'

const SKILLS = [
  'Python', 'FastAPI', 'RAG', 'LangChain', 'React', 'Docker', 'AI/Agent 工程',
]

const SECTIONS = [
  { key: 'skills', label: '技能栈' },
  { key: 'resume', label: '简历' },
  { key: 'projects', label: '项目' },
  { key: 'history', label: '版本历史' },
]

export default function Me() {
  useDocumentTitle('个人 · 个人集成学习网站')

  const allHistory = Object.entries(PAGE_CHANGELOGS).flatMap(([page, entries]) =>
    entries.map((e) => ({ page, ...e })),
  )

  return (
    <PageTransition>
      <PageChangelog pageKey="me" />
      <SidebarLayout
        sidebar={
          <div>
            <div className="text-xs font-semibold text-muted uppercase tracking-wider mb-3 px-3">
              关于我
            </div>
            <SidebarNav items={SECTIONS.map((s) => ({ key: s.key, to: `#${s.key}`, label: s.label }))} activeKey="skills" />
          </div>
        }
      >
        <div className="space-y-6">
          <section id="skills" className="bg-surface border border-border rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-primary mb-4">技能栈</h2>
            <div className="flex flex-wrap gap-2">
              {SKILLS.map((s) => (
                <Tag key={s} color="slate">{s}</Tag>
              ))}
            </div>
          </section>

          <section id="resume" className="bg-surface border border-border rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-primary mb-4">简历</h2>
            <a
              href="/resume.pdf"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-4 py-2 rounded-lg bg-accent text-accent-text text-sm font-medium hover:opacity-90"
            >
              下载简历(PDF)
            </a>
          </section>

          <section id="projects" className="bg-surface border border-border rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-primary mb-4">项目</h2>
            <ul className="list-disc pl-5 text-secondary text-sm space-y-1">
              <li>
                <a href="/quiz/" target="_blank" rel="noopener noreferrer" className="text-link hover:underline">
                  cs-quiz-app 面试题库(待集成)
                </a>
              </li>
            </ul>
          </section>

          <section id="history" className="bg-surface border border-border rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-primary mb-4">版本历史</h2>
            <div className="space-y-4">
              {allHistory
                .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
                .slice(0, 10)
                .map((e, idx) => (
                  <div key={idx} className="text-sm">
                    <span className="font-semibold text-primary">v{e.version}</span>
                    <span className="text-muted text-xs ml-2">{e.date}</span>
                    <span className="text-tertiary text-xs ml-2 uppercase">[{e.page}]</span>
                    <ul className="mt-1 ml-4 list-disc text-secondary">
                      {e.items.map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ))}
            </div>
          </section>
        </div>
      </SidebarLayout>
    </PageTransition>
  )
}
```

- [ ] **Step 3: 运行 TypeScript 检查**

Run: `npx tsc --noEmit`
Expected: 无错误

- [ ] **Step 4: 提交**

```bash
git add frontends/portfolio/src/hooks/useDocumentTitle.ts frontends/portfolio/src/pages/Me.tsx
git commit -m "feat(portfolio): redesign Me page and add document title hook"
```

---

## Task 11: App.tsx 整合与最终构建验证

**Files:**
- Modify: `frontends/portfolio/src/App.tsx`

**Interfaces:**
- `App` wraps each route with `PageTransition` and passes correct props to `Demo`.

- [ ] **Step 1: 重写 `App.tsx`**

```tsx
import { Routes, Route, useLocation } from 'react-router-dom'
import NavBar from './components/NavBar'
import Home from './pages/Home'
import Demo from './pages/Demo'
import Learn from './pages/Learn'
import Me from './pages/Me'
import PageTransition from './components/PageTransition'

function DemoRoute({ slug, src }: { slug: string; src: string }) {
  return <Demo slug={slug} src={src} />
}

export default function App() {
  const { pathname } = useLocation()

  return (
    <div className="min-h-screen bg-base">
      <NavBar />
      <PageTransition key={pathname}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/rag" element={<DemoRoute slug="rag" src="/rag/" />} />
          <Route path="/fc" element={<DemoRoute slug="fc" src="/fc/" />} />
          <Route path="/nexus" element={<DemoRoute slug="nexus" src="/nexus/" />} />
          <Route path="/learn" element={<Learn />} />
          <Route path="/doctomd" element={<DemoRoute slug="doctomd" src="/doctomd/" />} />
          <Route path="/me" element={<Me />} />
        </Routes>
      </PageTransition>
    </div>
  )
}
```

- [ ] **Step 2: 运行 TypeScript 检查**

Run: `npx tsc --noEmit`
Expected: 无错误

- [ ] **Step 3: 运行生产构建**

Run: `npm run build`
Expected: 构建成功,`dist/` 目录生成且无错误。

- [ ] **Step 4: 提交**

```bash
git add frontends/portfolio/src/App.tsx
git commit -m "feat(portfolio): wire new pages and components in App.tsx"
```

---

## Task 12: Docker 本地集成验证

**Files:**
- 不修改代码,只运行验证命令。

- [ ] **Step 1: 构建前端脚本**

Run (in repo root): `bash deploy/build-frontends.sh`
Expected: portfolio 构建成功,输出到 `deploy/dist/portfolio/`。

- [ ] **Step 2: 启动 docker-compose**

Run (in repo root): `docker compose -f deploy/docker-compose.yml up -d --build`
Expected: 所有容器启动成功,无 `upstream not found` 错误。

- [ ] **Step 3: 访问验证**

Open: http://127.0.0.1:8080/
Check:
- 首页显示 Hero 区、搜索框、作品卡片。
- 点击 RAG/FC/Nexus/DocHub 进入 Demo 页,左侧有作品导航,iframe 有骨架屏。
- 点击“学习”进入 Learn 页,左侧有课程目录。
- 点击“个人”进入 Me 页,有技能栈/简历/项目/版本历史卡片。
- 导航栏主题切换器可切换浅色/深蓝/赛博,刷新后保持。
- 切换浏览器标签页,标题会变化。

- [ ] **Step 4: 移动端宽度验证**

Use browser devtools, set width to 375px.
Expected: 导航折叠为汉堡菜单,页面无横向滚动条。

- [ ] **Step 5: 提交验证结果(可选)**

若仅验证无代码变更,无需提交。若发现构建/配置问题需要修复,则单独 commit。

---

## Task 13: 线上部署验证

**Files:**
- 不修改代码,只运行验证命令。

- [ ] **Step 1: 推送到 GitHub**

Run: `git push origin master`
Expected: 推送成功。

- [ ] **Step 2: SSH 到服务器并拉取更新**

Run (需要代理): `ssh -o ProxyCommand="nc -X 5 -x 127.0.0.1:7890 %h %p" root@8.213.145.110`
On server:
```bash
cd /opt/ai-demos
git pull origin master
bash deploy/build-frontends.sh
docker compose -f deploy/docker-compose.yml up -d --build
```

- [ ] **Step 3: 线上验证**

Open: https://www.shiyuan-wreg.cloud/
Run through the same checks as Task 12 Step 3.

---

## Self-Review Checklist

- [ ] **Spec coverage**: 每个 spec 章节都有对应任务实现(主题系统→Task 1;基础组件→Task 2;数据→Task 3;导航/公告→Task 4;侧边栏→Task 5;iframe 骨架→Task 6;首页→Task 7;Demo→Task 8;Learn→Task 9;Me→Task 10;过渡/标题→Task 10/11;Docker→Task 12;线上→Task 13)。
- [ ] **Placeholder scan**: 计划中没有 TBD/TODO/"实现 later"/"适当处理"等模糊表述。
- [ ] **Type consistency**: `Work.changelog` 在 Task 3 定义为数组,Task 7 `WorkCard` 未使用它(符合设计);`SidebarNavItem` 类型在 Task 5 定义,Task 8/9/10 使用同一结构;`Theme` 类型在 Task 1 定义,全计划使用同一字面量联合。
- [ ] **文件边界**: 每个组件一个文件,布局/数据/钩子分离。

---

## Notes

- 如果在 Task 1 中 `npx tsc --noEmit` 报 Tailwind 自定义颜色不识别,检查 `tailwind.config.js` 是否正确导出。
- 如果 `DemoFrame` 的 iframe 在本地加载极慢,可临时把超时时间从 8000ms 调大,但提交前调回。
- 主题切换在开发服务器(`npm run dev`)下可能因 Vite 的 CSS HMR 有闪烁,属于正常;生产构建后应稳定。
- 所有 emoji 已避免,标签页标题使用纯文本。
