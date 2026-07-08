# Kairos 门户背景音乐与开场载入动画实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 Kairos 门户（`frontends/portfolio`）实现背景音乐循环播放（音符开关）和全黑开场缓入动画。

**Architecture:** 使用原生 `HTMLAudioElement` 管理音频，`useRef` 持有实例，`useState` 管理播放/静音状态；新增 `MusicToggle` 组件嵌入 `NavBar`，新增 `SplashOverlay` 组件挂载于 `App.tsx` 最外层；通过 `setTimeout` 控制黑屏与淡出阶段。

**Tech Stack:** React 18 + TypeScript + Vite + TailwindCSS + lucide-react（已有依赖）。

## Global Constraints

- 不新增 npm 依赖。
- 音乐文件必须放在 `frontends/portfolio/public/music/`，不参与打包。
- 不修改后端、部署配置、其他 demo。
- 自动播放被浏览器阻止时，必须等待用户首次交互后恢复。
- 时长参数必须抽成常量，便于体验后微调。
- 所有改动需通过 `npm run build` 类型检查。
- 每次任务完成后独立 commit，最终 push `origin/master`。

---

## File Structure

| 文件 | 动作 | 职责 |
|---|---|---|
| `frontends/portfolio/public/music/shattered-dream.mp3` | 新增 | 背景音乐资源 |
| `frontends/portfolio/src/components/MusicToggle.tsx` | 新增 | 音符图标播放/静音开关 |
| `frontends/portfolio/src/components/SplashOverlay.tsx` | 新增 | 全黑开场遮罩 + 缓入动画 |
| `frontends/portfolio/src/App.tsx` | 修改 | 集成音频管理、SplashOverlay、MusicToggle |
| `frontends/portfolio/src/components/NavBar.tsx` | 修改 | 渲染 MusicToggle |
| `docs/superpowers/plans/2026-07-08-portfolio-bg-music-splash.md` | 新增 | 本计划文件 |

---

### Task 1: Copy music file into project

**Files:**
- Create: `frontends/portfolio/public/music/shattered-dream.mp3`

**Interfaces:**
- Consumes: Source file at `C:\Users\hzs17\Downloads\Shattered Dream.mp3`
- Produces: Static asset reachable at `/music/shattered-dream.mp3`

- [ ] **Step 1: Create target directory**

  ```bash
  mkdir -p /c/Users/hzs17/Desktop/kairos/frontends/portfolio/public/music
  ```

- [ ] **Step 2: Copy the music file**

  ```bash
  cp "/c/Users/hzs17/Downloads/Shattered Dream.mp3" \
     /c/Users/hzs17/Desktop/kairos/frontends/portfolio/public/music/shattered-dream.mp3
  ```

- [ ] **Step 3: Verify file size**

  ```bash
  ls -lh /c/Users/hzs17/Desktop/kairos/frontends/portfolio/public/music/shattered-dream.mp3
  ```

  Expected: 输出类似 `4.3M` 的文件大小。

- [ ] **Step 4: Commit**

  ```bash
  git add frontends/portfolio/public/music/shattered-dream.mp3
  git commit -m "assets(portfolio): add background music file

  Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
  ```

---

### Task 2: Create MusicToggle component

**Files:**
- Create: `frontends/portfolio/src/components/MusicToggle.tsx`
- Modify: `frontends/portfolio/src/components/NavBar.tsx`（下一任务才修改，本任务只创建组件）

**Interfaces:**
- Consumes: `isPlaying: boolean`, `onToggle: () => void`
- Produces: React component `MusicToggle`

- [ ] **Step 1: Write the component**

  创建 `frontends/portfolio/src/components/MusicToggle.tsx`：

  ```tsx
  import { Music, MusicOff } from 'lucide-react'

  interface MusicToggleProps {
    isPlaying: boolean
    onToggle: () => void
  }

  export default function MusicToggle({ isPlaying, onToggle }: MusicToggleProps) {
    return (
      <button
        type="button"
        onClick={onToggle}
        aria-label={isPlaying ? '关闭背景音乐' : '播放背景音乐'}
        title={isPlaying ? '关闭背景音乐' : '播放背景音乐'}
        className="p-2 rounded-md text-tertiary hover:text-primary hover:bg-surface-hover transition-colors active:scale-95"
      >
        {isPlaying ? (
          <Music className="w-5 h-5" />
        ) : (
          <MusicOff className="w-5 h-5" />
        )}
      </button>
    )
  }
  ```

- [ ] **Step 2: Verify lucide-react exports**

  检查 `frontends/portfolio/package.json` 已包含 `lucide-react`（已知存在）。

  运行：

  ```bash
  grep -E '"lucide-react"' /c/Users/hzs17/Desktop/kairos/frontends/portfolio/package.json
  ```

  Expected: 输出包含 `lucide-react` 的行。

- [ ] **Step 3: Type check**

  ```bash
  cd /c/Users/hzs17/Desktop/kairos/frontends/portfolio
  npx tsc --noEmit
  ```

  Expected: 无错误（可能有现有错误，但不应新增）。

- [ ] **Step 4: Commit**

  ```bash
  git add frontends/portfolio/src/components/MusicToggle.tsx
  git commit -m "feat(portfolio): add MusicToggle component with note icons

  Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
  ```

---

### Task 3: Create SplashOverlay component

**Files:**
- Create: `frontends/portfolio/src/components/SplashOverlay.tsx`

**Interfaces:**
- Consumes: None
- Produces: React component `SplashOverlay`

- [ ] **Step 1: Write the component**

  创建 `frontends/portfolio/src/components/SplashOverlay.tsx`：

  ```tsx
  import { useEffect, useState } from 'react'

  export const BLACK_HOLD_MS = 500
  export const FADE_DURATION_MS = 1800
  export const TOTAL_SPLASH_MS = BLACK_HOLD_MS + FADE_DURATION_MS

  type SplashPhase = 'black' | 'fading' | 'done'

  export default function SplashOverlay() {
    const [phase, setPhase] = useState<SplashPhase>('black')

    useEffect(() => {
      const fadeTimer = window.setTimeout(() => setPhase('fading'), BLACK_HOLD_MS)
      const doneTimer = window.setTimeout(() => setPhase('done'), TOTAL_SPLASH_MS)

      return () => {
        window.clearTimeout(fadeTimer)
        window.clearTimeout(doneTimer)
      }
    }, [])

    if (phase === 'done') return null

    return (
      <div
        aria-hidden="true"
        className={`fixed inset-0 z-[100] bg-black pointer-events-none transition-opacity ease-out ${
          phase === 'fading' ? 'opacity-0' : 'opacity-100'
        }`}
        style={{ transitionDuration: `${FADE_DURATION_MS}ms` }}
      />
    )
  }
  ```

- [ ] **Step 2: Type check**

  ```bash
  cd /c/Users/hzs17/Desktop/kairos/frontends/portfolio
  npx tsc --noEmit
  ```

  Expected: 无新增错误。

- [ ] **Step 3: Commit**

  ```bash
  git add frontends/portfolio/src/components/SplashOverlay.tsx
  git commit -m "feat(portfolio): add SplashOverlay with black hold and fade-in

  Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
  ```

---

### Task 4: Wire up audio and overlay in App.tsx

**Files:**
- Modify: `frontends/portfolio/src/App.tsx`
- Modify: `frontends/portfolio/src/components/NavBar.tsx`（下一任务）

**Interfaces:**
- Consumes: `MusicToggle`, `SplashOverlay`
- Produces: `audioRef`, `isPlaying`, `isMuted`, `handleMusicToggle` passed down to NavBar

- [ ] **Step 1: Read current App.tsx**

  已读取。当前内容：

  ```tsx
  import { Routes, Route, useLocation } from 'react-router-dom'
  import NavBar from './components/NavBar'
  import Home from './pages/Home'
  import Demo from './pages/Demo'
  import Learn from './pages/Learn'
  import Me from './pages/Me'
  import Changelog from './pages/Changelog'
  import PageTransition from './components/PageTransition'
  import GlobalHud from './components/GlobalHud'
  import ParallaxViewport from './components/ParallaxViewport'

  function DemoRoute({ slug, src }: { slug: string; src: string }) {
    return <Demo slug={slug} src={src} />
  }

  export default function App() {
    const { pathname } = useLocation()

    return (
      <div className="min-h-screen bg-base">
        <NavBar />
        <ParallaxViewport>
          <PageTransition key={pathname}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/rag" element={<DemoRoute slug="rag" src="/rag/" />} />
              <Route path="/fc" element={<DemoRoute slug="fc" src="/fc/" />} />
              <Route path="/nexus" element={<DemoRoute slug="nexus" src="/nexus/" />} />
              <Route path="/learn" element={<Learn />} />
              <Route path="/doctomd" element={<DemoRoute slug="doctomd" src="/doctomd/" />} />
              <Route path="/iconforge" element={<DemoRoute slug="iconforge" src="/iconforge/" />} />
              <Route path="/changelog" element={<Changelog />} />
              <Route path="/me" element={<Me />} />
            </Routes>
          </PageTransition>
        </ParallaxViewport>
        <GlobalHud />
      </div>
    )
  }
  ```

- [ ] **Step 2: Replace App.tsx with integrated version**

  完整替换为：

  ```tsx
  import { useEffect, useRef, useState } from 'react'
  import { Routes, Route, useLocation } from 'react-router-dom'
  import NavBar from './components/NavBar'
  import Home from './pages/Home'
  import Demo from './pages/Demo'
  import Learn from './pages/Learn'
  import Me from './pages/Me'
  import Changelog from './pages/Changelog'
  import PageTransition from './components/PageTransition'
  import GlobalHud from './components/GlobalHud'
  import ParallaxViewport from './components/ParallaxViewport'
  import SplashOverlay, { TOTAL_SPLASH_MS } from './components/SplashOverlay'

  const MUSIC_SRC = '/music/shattered-dream.mp3'
  const MUSIC_VOLUME = 0.5

  function DemoRoute({ slug, src }: { slug: string; src: string }) {
    return <Demo slug={slug} src={src} />
  }

  export default function App() {
    const { pathname } = useLocation()
    const audioRef = useRef<HTMLAudioElement | null>(null)
    const [isPlaying, setIsPlaying] = useState(false)
    const [isMuted, setIsMuted] = useState(false)
    const [splashDone, setSplashDone] = useState(false)

    // Initialize audio and attempt autoplay
    useEffect(() => {
      const audio = new Audio(MUSIC_SRC)
      audio.loop = true
      audio.volume = MUSIC_VOLUME
      audioRef.current = audio

      audio
        .play()
        .then(() => setIsPlaying(true))
        .catch(() => {
          // Browser blocked autoplay; wait for first user interaction
          setIsPlaying(false)
        })

      return () => {
        audio.pause()
        audio.src = ''
        audioRef.current = null
      }
    }, [])

    // Resume audio on first user interaction if autoplay was blocked
    useEffect(() => {
      if (isMuted) return

      const tryResume = () => {
        const audio = audioRef.current
        if (audio && audio.paused) {
          audio.play().then(() => setIsPlaying(true)).catch(() => {})
        }
      }

      window.addEventListener('click', tryResume, { once: true })
      window.addEventListener('keydown', tryResume, { once: true })

      return () => {
        window.removeEventListener('click', tryResume)
        window.removeEventListener('keydown', tryResume)
      }
    }, [isMuted])

    // Splash overlay lifecycle
    useEffect(() => {
      const timer = window.setTimeout(() => setSplashDone(true), TOTAL_SPLASH_MS)
      return () => window.clearTimeout(timer)
    }, [])

    const handleMusicToggle = () => {
      const audio = audioRef.current
      if (!audio) return

      if (isPlaying) {
        audio.pause()
        setIsPlaying(false)
        setIsMuted(true)
      } else {
        audio
          .play()
          .then(() => {
            setIsPlaying(true)
            setIsMuted(false)
          })
          .catch(() => {})
      }
    }

    return (
      <>
        <SplashOverlay />
        <div
          className={`min-h-screen bg-base transition-opacity ease-out ${
            splashDone ? 'opacity-100' : 'opacity-0'
          }`}
          style={{ transitionDuration: `${TOTAL_SPLASH_MS}ms` }}
        >
          <NavBar isPlaying={isPlaying} onMusicToggle={handleMusicToggle} />
          <ParallaxViewport>
            <PageTransition key={pathname}>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/rag" element={<DemoRoute slug="rag" src="/rag/" />} />
                <Route path="/fc" element={<DemoRoute slug="fc" src="/fc/" />} />
                <Route path="/nexus" element={<DemoRoute slug="nexus" src="/nexus/" />} />
                <Route path="/learn" element={<Learn />} />
                <Route path="/doctomd" element={<DemoRoute slug="doctomd" src="/doctomd/" />} />
                <Route path="/iconforge" element={<DemoRoute slug="iconforge" src="/iconforge/" />} />
                <Route path="/changelog" element={<Changelog />} />
                <Route path="/me" element={<Me />} />
              </Routes>
            </PageTransition>
          </ParallaxViewport>
          <GlobalHud />
        </div>
      </>
    )
  }
  ```

- [ ] **Step 3: Type check**

  ```bash
  cd /c/Users/hzs17/Desktop/kairos/frontends/portfolio
  npx tsc --noEmit
  ```

  Expected: 无新增错误。

- [ ] **Step 4: Commit**

  ```bash
  git add frontends/portfolio/src/App.tsx
  git commit -m "feat(portfolio): wire up background music and splash overlay in App

  - Initialize HTMLAudioElement on mount and attempt autoplay
  - Resume on first user interaction if blocked by browser
  - Add splash-driven page fade-in synced with SplashOverlay
  - Pass music state and toggle handler to NavBar

  Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
  ```

---

### Task 5: Render MusicToggle in NavBar

**Files:**
- Modify: `frontends/portfolio/src/components/NavBar.tsx`

**Interfaces:**
- Consumes: `isPlaying: boolean`, `onMusicToggle: () => void`
- Produces: Updated `NavBar` rendering `MusicToggle`

- [ ] **Step 1: Read current NavBar.tsx**

  当前 `NavBar` 为默认导出，无 props。顶部区域包含 `Logo` + 站点名 + 桌面端导航 + 主题/视差开关。

- [ ] **Step 2: Add props and import MusicToggle**

  修改后的关键部分：

  ```tsx
  import MusicToggle from './MusicToggle'

  interface NavBarProps {
    isPlaying?: boolean
    onMusicToggle?: () => void
  }

  export default function NavBar({ isPlaying = false, onMusicToggle }: NavBarProps) {
    // ... existing body
  }
  ```

- [ ] **Step 3: Insert MusicToggle into top-right controls**

  在桌面端和移动端的控制区（`ThemeToggle`/`ParallaxToggle` 旁边）插入 `MusicToggle`：

  ```tsx
  <div className="hidden md:flex items-center gap-6">
    {ITEMS.map((it) => (
      // ... existing links
    ))}
    <MusicToggle isPlaying={isPlaying} onToggle={onMusicToggle ?? (() => {})} />
    <ParallaxToggle />
    <ThemeToggle />
  </div>

  <div className="flex md:hidden items-center gap-3">
    <MusicToggle isPlaying={isPlaying} onToggle={onMusicToggle ?? (() => {})} />
    <ParallaxToggle />
    <ThemeToggle />
    <button>{/* mobile menu button */}</button>
  </div>
  ```

  完整 `NavBar.tsx` 修改后版本（保持所有现有逻辑）：

  ```tsx
  import { useState } from 'react'
  import { Link, useLocation } from 'react-router-dom'
  import ThemeToggle from './ThemeToggle'
  import ParallaxToggle from './ParallaxToggle'
  import Logo from './Logo'
  import MusicToggle from './MusicToggle'
  import { useScrolled } from '../hooks/useScrolled'

  const ITEMS = [
    { to: '/', label: '首页' },
    { to: '/rag', label: 'AI 作品' },
    { to: '/learn', label: '学习' },
    { to: '/changelog', label: '更新' },
    { to: '/me', label: '个人' },
  ]

  function MenuIcon({ open }: { open: boolean }) {
    return (
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        {open ? (
          <>
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </>
        ) : (
          <>
            <line x1="4" y1="6" x2="20" y2="6" />
            <line x1="4" y1="12" x2="20" y2="12" />
            <line x1="4" y1="18" x2="20" y2="18" />
          </>
        )}
      </svg>
    )
  }

  interface NavBarProps {
    isPlaying?: boolean
    onMusicToggle?: () => void
  }

  export default function NavBar({ isPlaying = false, onMusicToggle }: NavBarProps) {
    const { pathname } = useLocation()
    const [mobileOpen, setMobileOpen] = useState(false)
    const scrolled = useScrolled()

    const isActive = (to: string) => {
      if (to === '/') return pathname === '/'
      return pathname.startsWith(to)
    }

    return (
      <nav className={`sticky top-0 z-50 bg-surface/90 backdrop-blur border-b transition-all duration-300 ${
        scrolled ? 'border-strong shadow-md' : 'border-border'
      }`}>
        <div className="max-w-wide mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-14">
            <Link to="/" className="flex items-center gap-2.5">
              <Logo className="w-8 h-8 text-primary" />
              <span className="font-bold text-primary">Kairos</span>
            </Link>

            <div className="hidden md:flex items-center gap-6">
              {ITEMS.map((it) => (
                <Link
                  key={it.to}
                  to={it.to}
                  className={`group relative font-mono text-sm tracking-widest uppercase transition-colors ${
                    isActive(it.to) ? 'text-primary' : 'text-secondary hover:text-primary'
                  }`}
                >
                  {it.label}
                  <span className={`absolute -bottom-[17px] left-0 h-0.5 bg-accent transition-all duration-300 ${
                    isActive(it.to) ? 'w-full' : 'w-0 group-hover:w-full'
                  }`} />
                </Link>
              ))}
              <MusicToggle isPlaying={isPlaying} onToggle={onMusicToggle ?? (() => {})} />
              <ParallaxToggle />
              <ThemeToggle />
            </div>

            <div className="flex md:hidden items-center gap-3">
              <MusicToggle isPlaying={isPlaying} onToggle={onMusicToggle ?? (() => {})} />
              <ParallaxToggle />
              <ThemeToggle />
              <button
                onClick={() => setMobileOpen(!mobileOpen)}
                className="p-2 rounded-md text-tertiary hover:bg-surface-hover"
                aria-label="切换菜单"
              >
                <MenuIcon open={mobileOpen} />
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
                className={`block text-base font-medium ${
                  isActive(it.to) ? 'text-primary' : 'text-secondary'
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

- [ ] **Step 4: Type check**

  ```bash
  cd /c/Users/hzs17/Desktop/kairos/frontends/portfolio
  npx tsc --noEmit
  ```

  Expected: 无新增错误。

- [ ] **Step 5: Commit**

  ```bash
  git add frontends/portfolio/src/components/NavBar.tsx
  git commit -m "feat(portfolio): render MusicToggle in NavBar controls

  Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
  ```

---

### Task 6: Verify build and dev behavior

**Files:**
- All modified/created files above

**Interfaces:**
- Consumes: Completed Tasks 1-5
- Produces: Verified frontend build

- [ ] **Step 1: Run TypeScript check**

  ```bash
  cd /c/Users/hzs17/Desktop/kairos/frontends/portfolio
  npx tsc --noEmit
  ```

  Expected: 无错误输出。

- [ ] **Step 2: Run production build**

  ```bash
  npm run build
  ```

  Expected: 输出 `dist/` 目录，无 Rollup/TypeScript 报错。

- [ ] **Step 3: Verify dist contains music**

  ```bash
  ls -lh /c/Users/hzs17/Desktop/kairos/frontends/portfolio/dist/music/shattered-dream.mp3
  ```

  Expected: 文件存在，大小约 4.3M。

- [ ] **Step 4: Start dev server for manual check (optional)**

  ```bash
  npm run dev
  ```

  在浏览器访问 http://localhost:5180：

  - 页面应先黑屏约 0.5s，随后缓入显示。
  - 左上角应出现音符按钮。
  - 点击音符按钮可切换音乐。

  注意：需要同时启动本地 Docker 后端（:8080）才能看到各 demo 页面，但门户首页本身不需要后端。

- [ ] **Step 5: Commit any fixes**

  如果验证中发现并修复了问题，单独 commit。

---

### Task 7: Push to origin/master

**Files:**
- All commits created in Tasks 1-6

**Interfaces:**
- Consumes: Verified local commits
- Produces: `origin/master` updated

- [ ] **Step 1: Review git log**

  ```bash
  git log --oneline origin/master..HEAD
  ```

  Expected: 显示 5-6 个相关 commit。

- [ ] **Step 2: Push**

  ```bash
  git push origin master
  ```

  Expected: 输出 `master -> master`。

- [ ] **Step 3: Verify remote**

  ```bash
  git log --oneline -5
  ```

  Expected: `origin/master` 标签指向最新 commit。

---

## Self-Review

**1. Spec coverage:**

| Spec 要求 | 覆盖任务 |
|---|---|
| 背景音乐循环播放 | Task 4 |
| 音符图标开关在 NavBar 左上角 | Task 2, Task 5 |
| 自动播放被阻止后首次交互恢复 | Task 4 |
| 全黑开场 0.5s | Task 3 |
| 缓入 1.5–2s | Task 3, Task 4 |
| 时长参数可微调 | Task 3 (`BLACK_HOLD_MS`, `FADE_DURATION_MS`) |
| 音乐文件放 public/ | Task 1 |
| 不新增依赖 | 全计划 |
| 通过 build | Task 6 |

**2. Placeholder scan:**

- 无 "TBD"/"TODO"/"implement later"。
- 无模糊描述。
- 所有代码块完整。
- 所有文件路径精确。

**3. Type consistency:**

- `MusicToggle` 接收 `isPlaying: boolean`, `onToggle: () => void`。
- `NavBar` 接收 `isPlaying?: boolean`, `onMusicToggle?: () => void`。
- `App` 传递 `isPlaying={isPlaying}` 和 `onMusicToggle={handleMusicToggle}`。
- `SplashOverlay` 导出 `BLACK_HOLD_MS`, `FADE_DURATION_MS`, `TOTAL_SPLASH_MS`。
- `App` 导入 `TOTAL_SPLASH_MS` 用于页面淡入同步。

无类型不一致。

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-07-08-portfolio-bg-music-splash.md`.**

**Two execution options:**

1. **Subagent-Driven (recommended)** - Dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints.

**Which approach?**
