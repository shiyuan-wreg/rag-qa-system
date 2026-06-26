# The Machine HUD 皮肤(A1)设计文档

- **日期**:2026-06-26
- **阶段**:A1 —— 单页试装(只对 `/nexus` demo 页生效)
- **状态**:设计已确认,待写实现计划
- **来源参考**:`C:\Users\hzs17\Downloads\The-Machine-main`(他人用 Gemini 制作的《疑犯追踪》监控终端风格网页)

---

## 1. 背景与目标

ai-demos 门户现有 4 个可切换主题(`mono-light` / `light` / `deepblue` / `cyber`),通过 `<html data-theme="...">` + CSS 变量实现。用户希望引入 The Machine 的监控终端视觉风格(HUD)作为新皮肤。

整体路线分三步,本文档**只覆盖第一步 A1**:

1. **A1(本文档)**:用作用域受限的 CSS,只给 `/nexus` 这一个 demo 页的**外壳**套皮。低风险、可快速预览局部效果、易回退。
2. **B(后续)**:给 nexus demo 内部(`nexus_app` 后端 iframe 内容)套皮。
3. **A2(最终)**:提升为全局主题 `data-theme="machine"`,注册进 `ALL_THEMES`。

### 目标

- 在 `/nexus` 页面呈现监控终端视觉:监控网格、扫描线、暗角、CRT 闪烁、边角括号框、黄黑配色、等宽字体。
- 提供可选的 3D 悬浮视差效果(随鼠标偏移),由全局开关控制。
- 完全不影响其它 5 个 demo、不影响现有主题系统。

### 非目标(YAGNI)

- ❌ 打字机渐入效果(与 Nexus 自身流式输出冲突,暂不做)。
- ❌ 修改 iframe 内部(`nexus_app`)的样式(那是 B 阶段)。
- ❌ 注册成全局 `data-theme` 主题(那是 A2 阶段)。
- ❌ The Machine 原项目的音频播报、Gemini 调用等功能(纯视觉借鉴)。

---

## 2. 核心机制:作用域 class,不碰全局主题

A1 **不**新增 `data-theme`、**不**改 `useTheme`、**不**碰其它 demo。

做法:`/nexus` 页面内容外包一层 `<div class="machine-skin">`,所有皮肤样式写成后代选择器(`.machine-skin ...`),天然只在该容器内生效,样式不会外泄到导航栏或其它页面。

```
Demo.tsx (slug === 'nexus')
  └─ <MachineSkin>            ← 新增组件,class="machine-skin"
       ├─ 装饰叠加层 (grid/scanline/vignette/noise)  absolute, pointer-events:none
       └─ {children}          ← 原 SidebarLayout(导航栏 + DemoFrame)
```

其它 demo(`slug !== 'nexus'`)走原逻辑,渲染路径零改动。

**A2 升级的无损路径**:A1 把所有视觉变量定义在 `.machine-skin { --machine-*: ... }` 作用域下。将来 A2 时,把这批变量从 `.machine-skin` 选择器移到 `[data-theme="machine"]`,并把皮肤的 CSS 变量改为复用站点标准变量名(`--bg-base` / `--accent-primary` 等),即可让皮肤变成全站主题。A1 的组件与 CSS 结构为此预留。

---

## 3. 覆盖范围

**方案 A(已确认)**:皮肤覆盖**整个 demo 内容区**——左侧作品导航栏 + 右侧 demo 面板都套监控皮,沉浸感最强。

- 皮肤容器为 `Demo.tsx` 中 `h-[calc(100vh-3.5rem)]` 的内容区。
- 顶部全局导航栏(NavBar,3.5rem 高)**不**套皮,保持站点正常主题——保证用户始终能用正常的导航与主题切换器。
- 装饰叠加层用 `absolute inset-0`(限定在内容区内部),**不用** `fixed`(避免盖住导航栏)。

---

## 4. 组件与模块设计

### 4.1 `src/styles/machine-skin.css`(新增)

集中存放全部皮肤样式,在 `main.tsx` 引入一次。结构:

```css
.machine-skin {
  /* 皮肤调色板,集中定义,便于 A2 迁移 */
  --machine-bg: #0a0a0c;
  --machine-yellow: #FFD700;
  --machine-red: #FF4500;
  --machine-cyan: #00FFFF;
  --machine-grid: rgba(255,255,255,0.05);

  position: relative;
  background: var(--machine-bg);
  color: #e0e0e0;
  font-family: 'Share Tech Mono', ui-monospace, monospace;
}

/* 装饰层:网格 / 扫描线 / 暗角 / 噪点 —— 均 pointer-events:none */
.machine-skin__grid      { /* 40px 棋盘格 linear-gradient */ }
.machine-skin__scanline  { /* 4px 横向条纹 */ }
.machine-skin__vignette  { /* 径向渐变四周压暗 */ }
.machine-skin__noise     { /* 噪点纹理 + 低透明度 */ }

/* CRT 闪烁 */
@keyframes machine-flicker { 0%{opacity:.98} 50%{opacity:1} 100%{opacity:.99} }
.machine-skin--crt { animation: machine-flicker 0.15s infinite; }

/* 边角括号框 */
.machine-skin__bracket { /* 四角 L 形描边,黄色 */ }

/* prefers-reduced-motion:关闭所有动画 */
@media (prefers-reduced-motion: reduce) {
  .machine-skin--crt,
  .machine-skin__scanline { animation: none; }
}
```

字体 `Share Tech Mono` 通过 `index.html` 的 Google Fonts `<link>` 引入(与 The Machine 原项目一致),并提供本地等宽字体回退。

### 4.2 `src/components/MachineSkin.tsx`(新增)

皮肤包装组件,职责单一:渲染装饰层 + 处理视差变换 + 透传 children。

接口:

```ts
interface MachineSkinProps {
  children: React.ReactNode
}
```

行为:
- 渲染 `.machine-skin` 容器,内含 4 个装饰叠加层 + `{children}`。
- 调用 `useMotionPreference()` 取得 `effectiveParallax`。
- 当 `effectiveParallax === true` 时,挂载 `mousemove` 监听器,根据指针在容器内的相对位置计算 `transform`;为 `false` 时不挂监听器(零运行开销)。

视差计算(幅度做小,避免眩晕):

```
归一化:nx = (mouseX / width)  - 0.5   ∈ [-0.5, 0.5]
        ny = (mouseY / height) - 0.5
旋转:  rotateY = nx * 12deg   (左右,上限 ±6°)
        rotateX = -ny * 12deg  (上下,上限 ±6°)
位移:  translate = nx*8px, ny*8px(z 轴感由 perspective 产生)
应用:  外层 perspective(1000px);内容层 transform: rotateX() rotateY() translate()
        transition 用于松手回正时平滑过渡
```

- 视差 `transform` 作用在**装饰外壳层**;包含 iframe 的内容容器保持可交互(`transform` 不破坏 iframe 事件)。
- 装饰叠加层全部 `pointer-events: none`,不拦截点击。

### 4.3 `src/hooks/useMotionPreference.ts`(新增)

管理"是否启用 3D 视差"这一全局偏好。

```ts
const STORAGE_KEY = 'ai-demos-parallax'   // 默认 false

export function useMotionPreference(): {
  parallaxEnabled: boolean      // 用户本人的开关选择(UI 显示用)
  setParallaxEnabled: (v: boolean) => void
  prefersReducedMotion: boolean // 系统"减少动态"设置
  effectiveParallax: boolean    // = parallaxEnabled && !prefersReducedMotion(实际生效值)
}
```

- 初始值:`localStorage[ai-demos-parallax]`,缺省 `false`(默认关)。
- 监听 `window.matchMedia('(prefers-reduced-motion: reduce)')`,系统开启减少动态时 `effectiveParallax` 强制为 `false`(但 `parallaxEnabled` 仍保留用户选择)。
- 与现有 `useTheme` 的 localStorage 持久化模式保持一致。

### 4.4 `src/components/ParallaxToggle.tsx`(新增)

3D 视差开关 UI,放在 NavBar 中 `ThemeToggle` 旁边,风格与之统一。

- 调用 `useMotionPreference()`,点击切换 `setParallaxEnabled`。
- `aria-pressed` 反映当前状态;`prefersReducedMotion` 为真时显示禁用态并附说明(系统已开启减少动态)。

### 4.5 改动文件

| 文件 | 动作 | 说明 |
|---|---|---|
| `src/pages/Demo.tsx` | 改 | `slug === 'nexus'` 时用 `<MachineSkin>` 包裹内容区;否则原样 |
| `src/components/NavBar.tsx` | 改 | 在 `ThemeToggle` 旁加入 `<ParallaxToggle />` |
| `src/main.tsx` | 改 | 引入 `styles/machine-skin.css` |
| `index.html` | 改 | 加 `Share Tech Mono` 字体 `<link>` |

---

## 5. 数据流

1. 用户访问 `/nexus` → `Demo` 组件渲染,`slug === 'nexus'` 判定为真。
2. 内容区被 `<MachineSkin>` 包裹;CSS 类作用域生效,装饰层渲染,黄黑配色应用。
3. `MachineSkin` 调用 `useMotionPreference()` 读取 `effectiveParallax`。
4. 用户在 NavBar 点击 `ParallaxToggle` → 写入 `localStorage` → `effectiveParallax` 更新 → `MachineSkin` 挂载/卸载 `mousemove` 监听。
5. 监听激活时,鼠标移动 → 计算 transform → 外壳层产生 3D 悬浮偏移。
6. 访问其它 demo 或切换主题 → 完全不受影响。

---

## 6. 错误处理与边界

- **SSR / 无 window**:hook 初始化判断 `typeof window`,缺省返回默认值(沿用 `useTheme` 写法)。
- **触屏 / 无鼠标**:默认关,即便开启,无 `mousemove` 也只是静态皮肤,不报错。
- **iframe 加载失败**:`DemoFrame` 自带 loading/error 态,皮肤层在其外部,不干扰其逻辑。
- **性能**:`mousemove` 回调用 `requestAnimationFrame` 节流,避免高频重排;关闭时不挂监听零开销。
- **无障碍**:`prefers-reduced-motion: reduce` 同时由 CSS(关动画)和 JS(`effectiveParallax=false`)双重尊重。

---

## 7. 验证方式

- **手动**:
  1. `/nexus` 显示监控皮(网格/扫描线/暗角/CRT/边角框/黄黑配色)。
  2. 其它 5 个 demo(`/rag` `/fc` `/doctomd` `/iconforge` 及 `/learn`)外观无变化。
  3. 顶部导航栏不被装饰层遮挡,主题切换器仍可用。
  4. `ParallaxToggle` 默认关;开启后鼠标移动产生 3D 偏移;iframe 内仍可点击交互。
  5. 系统开启"减少动态效果"时,开关显示禁用态,无动画与视差。
  6. 刷新后开关状态从 localStorage 恢复。
- **构建**:`npm run build` 通过,无类型错误。

---

## 8. 回退方案

A1 不删除任何现有代码。回退只需:移除 `Demo.tsx` 中 nexus 的 `<MachineSkin>` 条件包裹(或整体删除 4 个新增文件 + 2 处引入)。对其它功能零影响。

---

## 9. 后续阶段衔接

- **B 阶段**:在 `nexus_app` 后端的前端资源中套同款皮(iframe 内部,因文档隔离需在后端侧改)。
- **A2 阶段**:将 `.machine-skin` 调色板迁移到 `[data-theme="machine"]`,皮肤 CSS 变量改为复用站点标准变量名,在 `useTheme.ts` 的 `ALL_THEMES` 注册 `'machine'`,在 `ThemeToggle` 增加"监控"选项。`MachineSkin` 的装饰层与 `ParallaxToggle` 可直接复用为全局组件。
