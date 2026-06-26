# The Machine HUD 皮肤(A1)实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 给 ai-demos 门户的 `/nexus` demo 页套上《疑犯追踪》监控终端(HUD)皮肤,含纯 CSS 装饰层与可选的 3D 悬浮视差(全局开关,默认关)。

**Architecture:** 用作用域受限的 class `.machine-skin` 包裹 `/nexus` 内容区。皮肤在该作用域内**覆盖站点标准 CSS 变量**,使子组件(SidebarNav / DemoInfoCard / DemoFrame)自动变成监控配色,无需改任何子组件。装饰层为 `absolute` 叠加,`pointer-events:none`。3D 视差由 `mousemove` 监听 + CSS transform 实现,受全局偏好开关控制,并尊重 `prefers-reduced-motion`。

**Tech Stack:** React 18 + TypeScript + Vite + Tailwind(类名→CSS 变量映射,见 `tailwind.config.js`)。无新增依赖。

## Global Constraints

- 不新增 npm 依赖;不引入外部字体 CDN,皮肤字体复用已自托管的 JetBrains Mono(`--font-mono`)。
- 不修改 `data-theme` / `useTheme.ts` / `ALL_THEMES`;不影响其它 5 个 demo 与现有 4 个主题。
- 所有皮肤样式必须写成 `.machine-skin` 后代选择器,严禁产生全局副作用。
- 视差开关 localStorage 键 = `ai-demos-parallax`,默认 `false`(关)。
- 系统 `prefers-reduced-motion: reduce` 时,视差实际生效值强制为 `false`,装饰动画关闭。
- 装饰叠加层一律 `pointer-events: none`,不得遮挡 iframe 交互。
- 本仓库前端无测试运行器;每个任务的自动关卡 = `npm run build`(在 `frontends/portfolio` 下,执行 `tsc && vite build`)通过且无类型错误,再加任务内列出的手动验收项。
- React 18 使用自动 JSX 运行时,组件文件无需 `import React`;需要类型时用 `import type { ReactNode } from 'react'`。

---

### Task 1: 视差偏好 hook `useMotionPreference`

**Files:**
- Create: `frontends/portfolio/src/hooks/useMotionPreference.ts`

**Interfaces:**
- Consumes: 无(基础模块)。
- Produces:
  ```ts
  export function useMotionPreference(): {
    parallaxEnabled: boolean        // 用户开关选择(UI 显示用)
    setParallaxEnabled: (v: boolean) => void
    prefersReducedMotion: boolean   // 系统“减少动态”设置
    effectiveParallax: boolean      // = parallaxEnabled && !prefersReducedMotion
  }
  ```
  - localStorage 键 `ai-demos-parallax`(字符串 `'true'`/`'false'`)。
  - 跨组件同步:`setParallaxEnabled` 写入后派发 `window` 事件 `'ai-demos-parallax-change'`;hook 监听该事件与 `storage` 事件实时同步(NavBar 的开关与 Demo 内的 MachineSkin 是两个 hook 实例,必须靠事件同步)。

- [ ] **Step 1: 创建 hook 文件**

创建 `frontends/portfolio/src/hooks/useMotionPreference.ts`:

```ts
import { useEffect, useState } from 'react'

const STORAGE_KEY = 'ai-demos-parallax'
const SYNC_EVENT = 'ai-demos-parallax-change'

function readEnabled(): boolean {
  if (typeof window === 'undefined') return false
  return window.localStorage.getItem(STORAGE_KEY) === 'true'
}

function readReducedMotion(): boolean {
  if (typeof window === 'undefined') return false
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

export function useMotionPreference() {
  const [parallaxEnabled, setEnabled] = useState<boolean>(readEnabled)
  const [prefersReducedMotion, setReduced] = useState<boolean>(readReducedMotion)

  useEffect(() => {
    if (typeof window === 'undefined') return

    const sync = () => setEnabled(readEnabled())
    window.addEventListener(SYNC_EVENT, sync)
    window.addEventListener('storage', sync)

    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    const onMq = () => setReduced(mq.matches)
    mq.addEventListener('change', onMq)

    return () => {
      window.removeEventListener(SYNC_EVENT, sync)
      window.removeEventListener('storage', sync)
      mq.removeEventListener('change', onMq)
    }
  }, [])

  const setParallaxEnabled = (v: boolean) => {
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(STORAGE_KEY, String(v))
      window.dispatchEvent(new Event(SYNC_EVENT))
    }
    setEnabled(v)
  }

  return {
    parallaxEnabled,
    setParallaxEnabled,
    prefersReducedMotion,
    effectiveParallax: parallaxEnabled && !prefersReducedMotion,
  }
}
```

- [ ] **Step 2: 类型检查 + 构建**

在 `frontends/portfolio` 下运行:`npm run build`
Expected: 构建成功,输出 `✓ built in ...`,无 TS 错误。

- [ ] **Step 3: 提交**

```bash
git add frontends/portfolio/src/hooks/useMotionPreference.ts
git commit -m "feat(portfolio): add useMotionPreference hook for parallax toggle"
```

---

### Task 2: 视差开关组件 `ParallaxToggle` 并接入 NavBar

**Files:**
- Create: `frontends/portfolio/src/components/ParallaxToggle.tsx`
- Modify: `frontends/portfolio/src/components/NavBar.tsx`(import + 桌面区 line 70 前、移动区 line 74 前各加一个)

**Interfaces:**
- Consumes: `useMotionPreference()`(Task 1)。
- Produces: 默认导出 React 组件 `ParallaxToggle`(无 props)。

- [ ] **Step 1: 创建 ParallaxToggle 组件**

创建 `frontends/portfolio/src/components/ParallaxToggle.tsx`:

```tsx
import { useMotionPreference } from '../hooks/useMotionPreference'

export default function ParallaxToggle() {
  const { parallaxEnabled, setParallaxEnabled, prefersReducedMotion } = useMotionPreference()
  const disabled = prefersReducedMotion

  return (
    <button
      onClick={() => setParallaxEnabled(!parallaxEnabled)}
      disabled={disabled}
      aria-pressed={parallaxEnabled && !disabled}
      title={disabled ? '系统已开启“减少动态效果”,3D 视差已禁用' : '切换 3D 悬浮视差'}
      className={[
        'inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-md border transition-all',
        disabled
          ? 'border-border text-muted opacity-50 cursor-not-allowed'
          : parallaxEnabled
            ? 'border-accent bg-accent text-accent-text shadow-sm'
            : 'border-border text-tertiary hover:text-primary hover:bg-surface-hover',
      ].join(' ')}
    >
      3D
    </button>
  )
}
```

- [ ] **Step 2: NavBar 引入组件**

在 `frontends/portfolio/src/components/NavBar.tsx` 顶部 import 区(第 3 行 `import ThemeToggle from './ThemeToggle'` 下一行)加入:

```tsx
import ParallaxToggle from './ParallaxToggle'
```

- [ ] **Step 3: 桌面导航区加入开关**

在 NavBar 桌面区,把原来的:

```tsx
            <ThemeToggle />
          </div>

          <div className="flex md:hidden items-center gap-3">
```

改为(在桌面 `<ThemeToggle />` 前插入 `<ParallaxToggle />`):

```tsx
            <ParallaxToggle />
            <ThemeToggle />
          </div>

          <div className="flex md:hidden items-center gap-3">
```

- [ ] **Step 4: 移动导航区加入开关**

把移动区原来的:

```tsx
          <div className="flex md:hidden items-center gap-3">
            <ThemeToggle />
            <button
```

改为(在移动 `<ThemeToggle />` 前插入 `<ParallaxToggle />`):

```tsx
          <div className="flex md:hidden items-center gap-3">
            <ParallaxToggle />
            <ThemeToggle />
            <button
```

- [ ] **Step 5: 类型检查 + 构建**

在 `frontends/portfolio` 下运行:`npm run build`
Expected: 构建成功,无 TS 错误。

- [ ] **Step 6: 手动验收**

`npm run dev`,打开任意页面:
- 导航栏主题切换器左侧出现 `3D` 按钮,默认未激活(关)。
- 点击 → 变激活态;刷新页面后状态保持(localStorage 持久化)。
- 系统开启“减少动态效果”时,按钮显示禁用态。

- [ ] **Step 7: 提交**

```bash
git add frontends/portfolio/src/components/ParallaxToggle.tsx frontends/portfolio/src/components/NavBar.tsx
git commit -m "feat(portfolio): add 3D parallax toggle to navbar"
```

---

### Task 3: 皮肤样式表 `machine-skin.css` 并全局引入

**Files:**
- Create: `frontends/portfolio/src/styles/machine-skin.css`
- Modify: `frontends/portfolio/src/main.tsx`(第 12 行 `import './styles.css'` 后加一行)

**Interfaces:**
- Consumes: 站点标准 CSS 变量名(来自 `tailwind.config.js` 映射)。
- Produces: class `.machine-skin` 及其后代类 `.machine-skin__grid` `.machine-skin__scanline` `.machine-skin__vignette` `.machine-skin__noise` `.machine-skin__frame` `.machine-skin__viewport` `.machine-skin__content`。

- [ ] **Step 1: 创建样式表**

创建 `frontends/portfolio/src/styles/machine-skin.css`:

```css
/* ============================================================
   The Machine HUD 皮肤(A1)—— 作用域限定在 .machine-skin 内
   仅 /nexus demo 页使用;靠后代选择器隔离,无全局副作用。
   ============================================================ */

.machine-skin {
  /* 皮肤私有色板 */
  --machine-bg: #0a0a0c;
  --machine-yellow: #ffd700;
  --machine-grid: rgba(255, 255, 255, 0.05);

  /* 覆盖站点标准变量(tailwind 类名据此取色)→ 子组件自动变监控配色 */
  --bg-base: #0a0a0c;
  --bg-soft: #111114;
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

  --shadow-sm: 0 0 8px rgba(255, 215, 0, 0.08);
  --shadow-md: 0 0 16px rgba(255, 215, 0, 0.10);
  --shadow-lg: 0 0 24px rgba(255, 215, 0, 0.14);
  --shadow-glow: 0 0 0 1px rgba(255, 215, 0, 0.25), 0 0 20px rgba(255, 215, 0, 0.15);

  /* 复用自托管 JetBrains Mono;CJK 回退保证中文不缺字 */
  --font-sans: "JetBrains Mono", "MiSans", "HarmonyOS Sans SC", "PingFang SC",
               "Microsoft YaHei", ui-monospace, monospace;

  position: relative;
  background: var(--machine-bg);
  overflow: hidden;
}

/* ---------- 装饰叠加层(均不挡鼠标) ---------- */
.machine-skin__grid,
.machine-skin__scanline,
.machine-skin__vignette,
.machine-skin__noise,
.machine-skin__frame {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 1;
}

.machine-skin__grid {
  background-size: 40px 40px;
  background-image:
    linear-gradient(to right, var(--machine-grid) 1px, transparent 1px),
    linear-gradient(to bottom, var(--machine-grid) 1px, transparent 1px);
}

.machine-skin__scanline {
  background: linear-gradient(to bottom, transparent 50%, rgba(255, 255, 255, 0.03) 50%);
  background-size: 100% 4px;
  animation: machine-flicker 0.15s infinite;
}

.machine-skin__vignette {
  background: radial-gradient(circle, transparent 40%, rgba(0, 0, 0, 0.85) 100%);
}

.machine-skin__noise {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  opacity: 0.05;
}

/* 四角括号框 */
.machine-skin__frame span {
  position: absolute;
  width: 22px;
  height: 22px;
  border: 2px solid var(--machine-yellow);
}
.machine-skin__frame span:nth-child(1) { top: 6px; left: 6px; border-right: 0; border-bottom: 0; }
.machine-skin__frame span:nth-child(2) { top: 6px; right: 6px; border-left: 0; border-bottom: 0; }
.machine-skin__frame span:nth-child(3) { bottom: 6px; left: 6px; border-right: 0; border-top: 0; }
.machine-skin__frame span:nth-child(4) { bottom: 6px; right: 6px; border-left: 0; border-top: 0; }

/* ---------- 内容层(视差作用对象) ---------- */
.machine-skin__viewport {
  position: relative;
  z-index: 2;
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  perspective: 1000px;
}
.machine-skin__content {
  flex: 1 1 auto;
  min-height: 0;
  display: flex;
  flex-direction: column;
  transform-style: preserve-3d;
  transition: transform 0.2s ease-out;
  will-change: transform;
}

@keyframes machine-flicker {
  0% { opacity: 0.97; }
  50% { opacity: 1; }
  100% { opacity: 0.98; }
}

/* 无障碍:系统要求减少动态 → 关闭装饰动画与过渡 */
@media (prefers-reduced-motion: reduce) {
  .machine-skin__scanline { animation: none; }
  .machine-skin__content { transition: none; }
}
```

- [ ] **Step 2: main.tsx 引入样式表**

在 `frontends/portfolio/src/main.tsx` 第 12 行 `import './styles.css'` 之后加一行:

```tsx
import './styles.css'
import './styles/machine-skin.css'
```

- [ ] **Step 3: 类型检查 + 构建**

在 `frontends/portfolio` 下运行:`npm run build`
Expected: 构建成功,CSS 被打包,无错误。

- [ ] **Step 4: 提交**

```bash
git add frontends/portfolio/src/styles/machine-skin.css frontends/portfolio/src/main.tsx
git commit -m "feat(portfolio): add machine-skin stylesheet (scoped HUD theme)"
```

---

### Task 4: `MachineSkin` 包装组件(静态装饰)并接入 Demo 页

**Files:**
- Create: `frontends/portfolio/src/components/MachineSkin.tsx`
- Modify: `frontends/portfolio/src/pages/Demo.tsx`

**Interfaces:**
- Consumes: 样式类(Task 3)。
- Produces: 默认导出组件 `MachineSkin`,签名 `({ children }: { children: ReactNode }) => JSX.Element`。本任务**只渲染静态装饰结构,不含视差逻辑**(视差在 Task 5 加入)。

- [ ] **Step 1: 创建 MachineSkin 组件(静态版)**

创建 `frontends/portfolio/src/components/MachineSkin.tsx`:

```tsx
import type { ReactNode } from 'react'

export default function MachineSkin({ children }: { children: ReactNode }) {
  return (
    <div className="machine-skin flex-1 min-h-0 flex flex-col">
      <div className="machine-skin__grid" aria-hidden="true" />
      <div className="machine-skin__noise" aria-hidden="true" />
      <div className="machine-skin__vignette" aria-hidden="true" />
      <div className="machine-skin__scanline" aria-hidden="true" />
      <div className="machine-skin__frame" aria-hidden="true">
        <span /><span /><span /><span />
      </div>
      <div className="machine-skin__viewport">
        <div className="machine-skin__content">{children}</div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Demo.tsx 接入(仅 nexus 套皮)**

把 `frontends/portfolio/src/pages/Demo.tsx` 整个文件替换为:

```tsx
import { WORKS } from '../data/works'
import DemoFrame from '../components/DemoFrame'
import DemoInfoCard from '../components/DemoInfoCard'
import SidebarLayout from '../components/SidebarLayout'
import SidebarNav from '../components/SidebarNav'
import type { SidebarNavItem } from '../components/SidebarNav'
import PageTransition from '../components/PageTransition'
import MachineSkin from '../components/MachineSkin'

export default function Demo({ slug, src }: { slug: string; src: string }) {
  const work = WORKS.find((w) => w.slug === slug)!
  const navItems: SidebarNavItem[] = WORKS.filter((w) => w.slug !== 'learn').map((w) => ({
    key: w.slug,
    to: w.path,
    label: w.title,
    icon: w.icon,
  }))

  const content = (
    <div className="max-w-wide mx-auto w-full px-4 sm:px-6 lg:px-8 py-4 flex-1 min-h-0">
      <SidebarLayout
        sidebar={
          <div className="space-y-5">
            <div>
              <div className="text-xs font-semibold text-muted uppercase tracking-wider mb-3 px-3">
                作品导航
              </div>
              <SidebarNav items={navItems} activeKey={slug} />
            </div>
            <DemoInfoCard work={work} />
          </div>
        }
      >
        <DemoFrame src={src} title={work.title} index={work.index} />
      </SidebarLayout>
    </div>
  )

  return (
    <PageTransition>
      <div className="h-[calc(100vh-3.5rem)] flex flex-col">
        {slug === 'nexus' ? <MachineSkin>{content}</MachineSkin> : content}
      </div>
    </PageTransition>
  )
}
```

- [ ] **Step 3: 类型检查 + 构建**

在 `frontends/portfolio` 下运行:`npm run build`
Expected: 构建成功,无 TS 错误。

- [ ] **Step 4: 手动验收**

`npm run dev`:
- 访问 `/nexus`:整个内容区(左侧作品导航 + 右侧 demo 面板)呈深色监控皮,网格/扫描线/暗角/噪点/四角黄色括号可见,文字与边框为琥珀黄,字体为等宽。
- 顶部全局导航栏**不**受影响,未被装饰层遮挡,主题切换器与 `3D` 开关仍可用。
- 访问 `/rag`、`/fc`、`/doctomd`、`/iconforge`、`/learn`:外观与改动前完全一致(无皮肤)。
- 切换站点主题(极简/浅色/深蓝/赛博)时,`/nexus` 皮肤保持监控样式不被站点主题覆盖。
- iframe 内容可正常点击交互(装饰层不挡鼠标)。

- [ ] **Step 5: 提交**

```bash
git add frontends/portfolio/src/components/MachineSkin.tsx frontends/portfolio/src/pages/Demo.tsx
git commit -m "feat(portfolio): apply machine HUD skin to /nexus demo page (static layers)"
```

---

### Task 5: 在 `MachineSkin` 中加入 3D 视差逻辑

**Files:**
- Modify: `frontends/portfolio/src/components/MachineSkin.tsx`

**Interfaces:**
- Consumes: `useMotionPreference()`(Task 1)的 `effectiveParallax`;Task 4 的 DOM 结构(`.machine-skin__viewport` / `.machine-skin__content`)。
- Produces: 同一 `MachineSkin` 组件,新增 `mousemove` 驱动的 transform。

- [ ] **Step 1: 用带视差的版本替换 MachineSkin**

把 `frontends/portfolio/src/components/MachineSkin.tsx` 整个替换为:

```tsx
import { useEffect, useRef } from 'react'
import type { ReactNode } from 'react'
import { useMotionPreference } from '../hooks/useMotionPreference'

export default function MachineSkin({ children }: { children: ReactNode }) {
  const { effectiveParallax } = useMotionPreference()
  const viewportRef = useRef<HTMLDivElement>(null)
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!effectiveParallax) return
    const viewport = viewportRef.current
    const content = contentRef.current
    if (!viewport || !content) return

    let frame = 0
    const onMove = (e: MouseEvent) => {
      if (frame) return
      frame = window.requestAnimationFrame(() => {
        frame = 0
        const rect = viewport.getBoundingClientRect()
        const nx = (e.clientX - rect.left) / rect.width - 0.5   // [-0.5, 0.5]
        const ny = (e.clientY - rect.top) / rect.height - 0.5
        const rotateY = nx * 12   // 上限 ±6°
        const rotateX = -ny * 12
        const tx = nx * 8
        const ty = ny * 8
        content.style.transform =
          `rotateX(${rotateX}deg) rotateY(${rotateY}deg) translate3d(${tx}px, ${ty}px, 0)`
      })
    }
    const reset = () => {
      if (frame) {
        window.cancelAnimationFrame(frame)
        frame = 0
      }
      content.style.transform = ''
    }

    viewport.addEventListener('mousemove', onMove)
    viewport.addEventListener('mouseleave', reset)
    return () => {
      viewport.removeEventListener('mousemove', onMove)
      viewport.removeEventListener('mouseleave', reset)
      reset()
    }
  }, [effectiveParallax])

  return (
    <div className="machine-skin flex-1 min-h-0 flex flex-col">
      <div className="machine-skin__grid" aria-hidden="true" />
      <div className="machine-skin__noise" aria-hidden="true" />
      <div className="machine-skin__vignette" aria-hidden="true" />
      <div className="machine-skin__scanline" aria-hidden="true" />
      <div className="machine-skin__frame" aria-hidden="true">
        <span /><span /><span /><span />
      </div>
      <div ref={viewportRef} className="machine-skin__viewport">
        <div ref={contentRef} className="machine-skin__content">{children}</div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: 类型检查 + 构建**

在 `frontends/portfolio` 下运行:`npm run build`
Expected: 构建成功,无 TS 错误。

- [ ] **Step 3: 手动验收**

`npm run dev`,访问 `/nexus`:
- `3D` 开关**关**(默认):鼠标移动时内容区**不**偏移(无视差)。
- 点 `3D` 开关**开**:鼠标在内容区移动时,内容产生随鼠标的 3D 悬浮偏移(旋转 ±6° 内 + 轻微位移);鼠标移出后平滑回正。
- 视差开启时 iframe 内仍可点击交互。
- 关闭开关后视差立即停止(事件同步,无需刷新)。
- 系统开启“减少动态效果”时,即使开关为开也无视差(`effectiveParallax` 为 false)。

- [ ] **Step 4: 提交**

```bash
git add frontends/portfolio/src/components/MachineSkin.tsx
git commit -m "feat(portfolio): add mouse-driven 3D parallax to machine skin"
```

---

## 自检(Self-Review)

**Spec 覆盖核对:**

| Spec 要求 | 对应任务 |
|---|---|
| §2 `.machine-skin` 作用域、不碰全局主题 | Task 3(CSS)+ Task 4(包裹) |
| §2 覆盖标准 CSS 变量 → 子组件自动变色 | Task 3 |
| §3 方案 A:整个内容区套皮,导航栏不套 | Task 4 |
| §4.1 装饰层(网格/扫描线/暗角/噪点/CRT/边角框) | Task 3 |
| §4.2 MachineSkin 组件 + 视差计算公式 | Task 4 + Task 5 |
| §4.3 视差受开关控制、iframe 可交互、幅度小 | Task 5 |
| §4.3 关闭时零监听开销 | Task 5(`if (!effectiveParallax) return`) |
| §4.4 useMotionPreference,默认关,localStorage,reduced-motion | Task 1 |
| §4.4 ParallaxToggle 放 ThemeToggle 旁 | Task 2 |
| §6 SSR/触屏/性能(rAF 节流)/无障碍双重尊重 | Task 1(SSR/reduced)+ Task 3(CSS @media)+ Task 5(rAF) |
| §7 验证清单 | 各任务手动验收步骤 |
| §8 回退(不删现有代码) | 全程仅新增 + 条件包裹 |

**与 spec 的务实偏差(已在交付时说明):**
- 字体不引 Google Fonts CDN,改用自托管 JetBrains Mono(Global Constraints),省去 `index.html` 改动。
- 无前端测试运行器,自动关卡用 `npm run build` + 手动验收清单替代单元测试。

**类型一致性:** `useMotionPreference` 返回字段名 `parallaxEnabled` / `setParallaxEnabled` / `prefersReducedMotion` / `effectiveParallax` 在 Task 2、Task 5 引用处一致;CSS 类名 `.machine-skin__viewport` / `.machine-skin__content` 在 Task 3、4、5 一致。

**占位符扫描:** 无 TBD/TODO,每个改动步骤均含完整代码。
