# Kairos 门户背景音乐与开场载入动画设计

> 设计日期：2026-07-08  
> 关联计划：待补充 `docs/superpowers/plans/2026-07-08-portfolio-bg-music-splash.md`

## 目标

为 Kairos 门户（`frontends/portfolio`）增加两个体验型功能：

1. **背景音乐**：进入网站后自动循环播放指定音乐，用户可通过 `NavBar` 左上角的音符图标按钮切换播放/静音。
2. **开场载入动画**：页面初次加载时先显示全黑遮罩约 0.5s，随后以 1.5–2s 的缓动动画渐进显示网页内容。

## 范围

- 只修改 `frontends/portfolio` 前端项目。
- 不修改任何后端服务、API 或部署配置。
- 不引入新的 npm 依赖（使用原生 `HTMLAudioElement`）。
- 音乐文件由用户本地提供，复制到项目 `public/music/` 目录下参与构建。

## 方案

采用 **最小依赖方案（方案 A）**：

- 原生 `HTMLAudioElement` 管理音频。
- 新组件 `MusicToggle` 放在 `NavBar` 左上角。
- 新组件 `SplashOverlay` 作为全屏开场遮罩，挂载于 `App.tsx` 最外层。
- 自动播放被浏览器阻止时，等待用户首次交互后恢复播放。

## 详细设计

### 1. 音乐文件

- **源文件**：`C:\Users\hzs17\Downloads\Shattered Dream.mp3`
- **目标路径**：`frontends/portfolio/public/music/shattered-dream.mp3`
- **引用方式**：`/music/shattered-dream.mp3`（Vite 会把 `public/` 下内容原样复制到 `dist/` 根目录）

### 2. 背景音乐管理

#### 2.1 状态与引用

在 `App.tsx` 顶层用 `useRef` 持有 `HTMLAudioElement` 实例，用 `useState` 管理两个状态：

- `isPlaying: boolean` — 当前是否正在播放。
- `isMuted: boolean` — 用户是否手动关闭。

```typescript
const audioRef = useRef<HTMLAudioElement | null>(null)
const [isPlaying, setIsPlaying] = useState(false)
const [isMuted, setIsMuted] = useState(false)
```

#### 2.2 初始化行为

在 `useEffect` 中：

1. 创建 `audio` 元素。
2. 设置 `loop = true`。
3. 设置初始音量（建议 `0.5`）。
4. 调用 `audio.play()` 尝试自动播放。
5. 若 `play()` 返回的 Promise 被 reject（浏览器自动播放策略），将 `isPlaying` 设为 `false`，等待用户首次点击页面后再尝试播放。

#### 2.3 首次交互恢复

监听 `window` 的 `click` / `keydown` / `touchstart` 事件，仅触发一次：

```typescript
useEffect(() => {
  const tryResume = () => {
    if (audioRef.current && !isMuted && audioRef.current.paused) {
      audioRef.current.play().catch(() => {})
    }
  }
  window.addEventListener('click', tryResume, { once: true })
  window.addEventListener('keydown', tryResume, { once: true })
  return () => {
    window.removeEventListener('click', tryResume)
    window.removeEventListener('keydown', tryResume)
  }
}, [isMuted])
```

#### 2.4 切换逻辑

`MusicToggle` 组件接收 `isPlaying` 和 `onToggle`：

- 点击时调用 `onToggle`。
- `onToggle` 内部：
  - 若当前在播放：调用 `audio.pause()`，`setIsPlaying(false)`，`setIsMuted(true)`。
  - 若当前暂停/静音：调用 `audio.play()`，成功则 `setIsPlaying(true)`，`setIsMuted(false)`。

### 3. 音乐开关 UI

#### 3.1 位置

整合到 `NavBar` 左上角区域，位于 `ThemeToggle` / `ParallaxToggle` 之前或 Logo 右侧。最终位置在实现阶段根据视觉平衡微调。

#### 3.2 图标样式

使用 `lucide-react` 中的 `Music` 和 `MusicOff` 图标（若不存在则使用 `Volume2` / `VolumeX` 或内联 SVG 音符图标）。

- **播放状态**：实心/彩色音符图标（`text-primary`）。
- **静音/暂停状态**：音符带斜杠或空心图标（`text-tertiary`）。

```tsx
import { Music, MusicOff } from 'lucide-react'

<button aria-label={isPlaying ? '关闭音乐' : '播放音乐'}>
  {isPlaying ? <Music className="w-5 h-5" /> : <MusicOff className="w-5 h-5" />}
</button>
```

#### 3.3 交互反馈

- 鼠标悬停显示 Tooltip 或 title 提示。
- 点击时有轻微缩放反馈（`active:scale-95`）。

### 4. 开场载入动画

#### 4.1 组件

新增 `SplashOverlay.tsx`：

```tsx
export default function SplashOverlay() {
  const [phase, setPhase] = useState<'black' | 'fading' | 'done'>('black')

  useEffect(() => {
    const fadeTimer = setTimeout(() => setPhase('fading'), 500)
    const doneTimer = setTimeout(() => setPhase('done'), 2200)
    return () => {
      clearTimeout(fadeTimer)
      clearTimeout(doneTimer)
    }
  }, [])

  if (phase === 'done') return null

  return (
    <div
      className={`fixed inset-0 z-[100] bg-black transition-opacity duration-[1500ms] ease-out pointer-events-none ${
        phase === 'fading' ? 'opacity-0' : 'opacity-100'
      }`}
    />
  )
}
```

#### 4.2 参数

| 阶段 | 时长 | 说明 |
|---|---|---|
| 全黑 | 0.5s | 遮挡未渲染完全的页面 |
| 缓入淡出 | 1.5–2s | 黑屏 `opacity-100` → `opacity-0` |
| 总时长 | 2.0–2.5s | 之后遮罩从 DOM 移除 |

实现时把时长抽成常量，方便用户体验后微调：

```typescript
const BLACK_HOLD_MS = 500
const FADE_DURATION_MS = 1800
```

#### 4.3 与页面内容的配合

`App.tsx` 中页面主体容器同时添加淡入类：

```tsx
<div className={`min-h-screen bg-base transition-opacity duration-[1500ms] ease-out ${splashDone ? 'opacity-100' : 'opacity-0'}`}>
  {/* ... */}
</div>
```

这样黑屏淡出与网页内容淡入同步进行。

### 5. 自动播放策略说明

现代浏览器（Chrome、Safari、Edge、Firefox）普遍限制带声音频的自动播放。可行策略：

1. 页面加载后立即尝试播放。
2. 若被拒绝，保持音频元素存在但暂停。
3. 监听用户首次交互（点击/按键），再次尝试播放。
4. 用户可通过音符按钮随时静音。

这是浏览器安全策略决定的行为，无法绕过；最佳用户体验是让用户感知到音乐可控，并提供明显的音符开关。

### 6. 需要修改/新增的文件

| 文件 | 动作 | 说明 |
|---|---|---|
| `frontends/portfolio/public/music/shattered-dream.mp3` | 新增 | 复制用户提供的音乐文件 |
| `frontends/portfolio/src/components/MusicToggle.tsx` | 新增 | 音符开关按钮 |
| `frontends/portfolio/src/components/SplashOverlay.tsx` | 新增 | 全黑开场遮罩 |
| `frontends/portfolio/src/App.tsx` | 修改 | 集成音频管理、MusicToggle、SplashOverlay |
| `frontends/portfolio/src/components/NavBar.tsx` | 修改 | 接收并渲染 MusicToggle |

### 7. 已知风险与规避

| 风险 | 规避方法 |
|---|---|
| 浏览器阻止自动播放 | 先尝试播放，失败则等待首次交互；用户可手动开关 |
| 音乐文件过大影响构建/加载 | 4.3MB 可接受；public/ 文件不参与打包，直接复制到 dist |
| 黑屏时间过长 | 时长抽成常量，便于体验后微调 |
| 主题切换与黑屏冲突 | SplashOverlay 用纯黑 `bg-black`，不依赖主题变量 |
| 切换路由时音乐中断 | 音频实例放在 App 顶层，切换路由不销毁 |

### 8. 成功标准

1. 访问首页时，0.5s 内看到全黑遮罩，随后网页在 1.5–2s 内缓入显示。
2. 音乐在支持自动播放的环境下自动循环播放。
3. 浏览器阻止自动播放时，用户首次点击页面后音乐开始播放。
4. `NavBar` 左上角音符按钮可正常切换播放/静音，图标状态同步。
5. 本地 `npm run build` 成功，无新增 TS/ESLint 错误。

---

## 决策记录

- **不用 Howler.js**：需求简单，原生 `HTMLAudioElement` 足够，避免新增依赖。
- **音乐放 public/ 而非 src/assets/**：Vite 对 public/ 文件原样复制，引用路径稳定，且大文件不参与 bundle 打包。
- **开关放 NavBar 左上角**：符合用户指定位置，与现有主题/视差开关视觉统一。
- **SplashOverlay 与页面内容同步淡入**：避免黑屏移除后页面突然闪现。
