# TailwindCSS 零基础入门

> 目标：理解 TailwindCSS 是什么，能用工具类写样式，并看懂 Kairos 门户的主题系统。

## 1. 一句话定义

TailwindCSS 是 **实用类优先（utility-first）的 CSS 框架**，通过组合大量细粒度类名来构建界面样式。

## 2. 为什么存在

在 Kairos 中选择 TailwindCSS 的原因：

1. **开发快**：不需要手写 CSS 文件，直接在 JSX 中组合类名。
2. **设计一致**：通过配置文件统一颜色、间距、字体等设计 token。
3. **响应式简单**：用 `sm:`、`md:`、`lg:` 前缀快速实现多端适配。
4. **产物小**：JIT 模式只生成实际使用的类，不会把所有 CSS 都打进去。

Kairos 门户 `frontends/portfolio` 几乎所有样式都用 TailwindCSS 实现。

## 3. 安装与验证

在 Vite + React 项目中安装：

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

初始化后会生成 `tailwind.config.js` 和 `postcss.config.js`。

在 `src/index.css`（或对应入口 CSS）中写入：

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

配置 `tailwind.config.js` 扫描范围：

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

启动开发服务器，Expected: Tailwind 类名生效。

## 4. 最小动手示例

### 4.1 基础布局

```html
<div class="flex items-center justify-center h-screen bg-gray-900 text-white">
  <h1 class="text-3xl font-bold">Hello Tailwind</h1>
</div>
```

这些类名的含义：

- `flex`：开启 flex 布局。
- `items-center`：垂直居中。
- `justify-center`：水平居中。
- `h-screen`：高度等于视口高度。
- `bg-gray-900`：深灰背景。
- `text-white`：白色文字。
- `text-3xl`：大字号。
- `font-bold`：加粗。

### 4.2 响应式设计

```html
<p class="text-sm md:text-base lg:text-lg">
  这段文字在小屏是 sm，中屏是 base，大屏是 lg。
</p>
```

Tailwind 是**移动端优先**：不写前缀的样式默认作用于最小屏幕，前缀表示在更大屏幕生效。

### 4.3 状态变体

```html
<button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
  点击我
</button>
```

`hover:bg-blue-700` 表示鼠标悬停时背景色变深。

### 4.4 自定义颜色

在 `tailwind.config.js` 中扩展主题：

```javascript
export default {
  theme: {
    extend: {
      colors: {
        kairos: '#1a1a1a',
      },
    },
  },
}
```

然后使用：

```html
<div class="bg-kairos"></div>
```

## 5. 核心概念

### 5.1 utility-first 思想

传统 CSS：

```css
.card {
  padding: 1rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
```

Tailwind：

```html
<div class="p-4 bg-white rounded-lg shadow-md"></div>
```

不需要起类名，直接在 HTML/JSX 中描述样式。

### 5.2 JIT 模式

Tailwind v3 默认使用 JIT（Just-In-Time），只生成你在代码里实际用到的类。这意味着你可以写任意值，例如 `w-[123px]`、`text-[#1da1f2]`，Tailwind 会动态生成对应 CSS。

### 5.3 自定义主题扩展

通过 `theme.extend` 添加自己的设计 token：

```javascript
export default {
  theme: {
    extend: {
      colors: { primary: '#3b82f6' },
      spacing: { 18: '4.5rem' },
      fontFamily: { mono: ['JetBrains Mono', 'monospace'] },
    },
  },
}
```

### 5.4 响应式前缀

默认断点（移动端优先）：

| 前缀 | 最小宽度 | CSS |
|---|---|---|
| `sm:` | 640px | `@media (min-width: 640px)` |
| `md:` | 768px | `@media (min-width: 768px)` |
| `lg:` | 1024px | `@media (min-width: 1024px)` |
| `xl:` | 1280px | `@media (min-width: 1280px)` |

### 5.5 深色模式与 CSS 变量

Kairos 的主题系统使用 CSS 变量 + `data-theme` 属性：

```css
:root {
  --bg-base: #ffffff;
  --text-primary: #111111;
}

[data-theme="machine"] {
  --bg-base: #0a0a0a;
  --text-primary: #e3b341;
}
```

Tailwind 配置引用这些变量：

```javascript
colors: {
  base: 'var(--bg-base)',
  primary: 'var(--text-primary)',
}
```

切换主题时只需修改 `data-theme`，所有使用 `bg-base`、`text-primary` 的组件自动变色。

### 5.6 与自定义 CSS 的职责分离

Tailwind 处理常见样式，复杂动画、纹理、全局背景等可放在自定义 CSS 文件中（如 `machine-skin.css`、`texture.css`），两者互补。

## 6. 在 Kairos 中的应用

### 6.1 tailwind.config.js

看 `frontends/portfolio/tailwind.config.js`：

```javascript
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
        primary: 'var(--text-primary)',
        secondary: 'var(--text-secondary)',
        accent: {
          DEFAULT: 'var(--accent-primary)',
          text: 'var(--accent-primary-text)',
        },
      },
      fontFamily: {
        sans: 'var(--font-sans)',
        mono: 'var(--font-mono)',
      },
      maxWidth: {
        content: 'var(--max-content)',
        wide: 'var(--max-wide)',
      },
    },
  },
}
```

Kairos 没有直接使用 Tailwind 的默认色板，而是通过 CSS 变量定义了一套自己的设计系统。

### 6.2 NavBar 组件

看 `frontends/portfolio/src/components/NavBar.tsx`：

```tsx
<nav className="sticky top-0 z-50 bg-surface/90 backdrop-blur border-b transition-all duration-300">
  <div className="max-w-wide mx-auto px-4 sm:px-6 lg:px-8">
    <div className="flex items-center justify-between h-14">
      {/* ... */}
    </div>
  </div>
</nav>
```

- `sticky top-0`： sticky 定位，粘在顶部。
- `bg-surface/90`：使用自定义 surface 颜色，90% 不透明度。
- `backdrop-blur`：背景模糊效果。
- `max-w-wide mx-auto`：最大宽度限制，水平居中。
- `px-4 sm:px-6 lg:px-8`：响应式水平内边距。

### 6.3 响应式导航

```tsx
<div className="hidden md:flex items-center gap-6">
  {/* 桌面端导航 */}
</div>

<div className="flex md:hidden items-center gap-3">
  {/* 移动端导航 */}
</div>
```

- `hidden md:flex`：小屏隐藏，中屏及以上显示。
- `flex md:hidden`：小屏显示，中屏及以上隐藏。

## 7. 常见错误与排查

| 错误信息/现象 | 可能原因 | 解决方法 |
|---|---|---|
| Tailwind 类不生效 | `content` 配置未覆盖文件路径 | 检查 `tailwind.config.js` 的 content |
| 自定义颜色无效 | CSS 变量名与 Tailwind 配置不一致 | 统一变量命名 |
| 响应式样式不生效 | 断点理解错误 | 记住移动端优先 |
| 类名太长可读性差 | JSX 中堆砌大量类 | 抽成常量、用 clsx/tailwind-merge |
| JIT 不生成动态值 | 语法错误 | 使用 `w-[123px]` 形式 |
| 浅色/深色主题没切换 | data-theme 没生效或变量未定义 | 检查 theme.css 和 HTML 属性 |

## 8. 常见面试问法

- "Tailwind 和传统 CSS 框架（如 Bootstrap）的区别是什么？"
- "Tailwind 如何实现主题切换？"
- "如何避免 Tailwind 类名过长导致 JSX 可读性下降？"
- "Tailwind 的 JIT 模式是什么？"
- "Tailwind 是移动端优先还是桌面端优先？"
- "Tailwind 中如何自定义设计 token？"

## 9. 下一步

前端层基础教程已完成。你可以：

- 回到 [Kairos 技术概念地图](kairos-concept-map.md)，把 TailwindCSS 标记为已掌握
- 尝试修改 `frontends/portfolio/src/components/NavBar.tsx` 的 Tailwind 类名，观察界面变化
- 继续学习 AI 层：[LLM / Function Calling / RAG 相关教程]
