# React 零基础入门

> 目标：理解 React 是什么，能写简单的函数组件，并看懂 Kairos 门户的页面和组件结构。

## 1. 一句话定义

React 是 **用于构建用户界面的 JavaScript 库**，通过组件和声明式渲染把 UI 拆成可复用的模块。

## 2. 为什么存在

在 Kairos 中选择 React 的原因：

1. **组件化**：把页面拆成独立、可复用的小块，降低复杂度。
2. **声明式 UI**：只需描述"界面应该长什么样"，React 负责高效更新 DOM。
3. **生态成熟**：React Router、状态管理、UI 库、测试工具一应俱全。
4. **就业市场需求大**：AI/Agent 前端开发几乎都离不开 React。

Kairos 门户 `frontends/portfolio` 使用 React 18 + TypeScript 构建。

## 3. 安装与验证

使用 Vite 创建 React + TypeScript 项目：

```bash
npm create vite@latest my-app -- --template react-ts
cd my-app
npm install
npm run dev
```

访问 http://localhost:5173，Expected: 看到 Vite + React 默认页面。

## 4. 最小动手示例

### 4.1 JSX 基础

JSX 是 React 的语法扩展，允许在 JavaScript 中写类似 HTML 的结构：

```tsx
function App() {
  return <h1>Hello, React!</h1>
}

export default App
```

JSX 编译后变成 `React.createElement`，所以本质上还是 JavaScript。

### 4.2 组件与 props

组件就是函数，props 是父组件传给子组件的数据：

```tsx
function Welcome({ name }: { name: string }) {
  return <p>Welcome, {name}</p>
}

function App() {
  return <Welcome name="Kairos" />
}
```

props 是**只读**的，不能在子组件中修改。

### 4.3 state 与事件

state 是组件内部可变的状态，变化会触发重新渲染：

```tsx
import { useState } from 'react'

function Counter() {
  const [count, setCount] = useState(0)

  return (
    <button onClick={() => setCount(count + 1)}>
      Clicked {count} times
    </button>
  )
}
```

### 4.4 useEffect

`useEffect` 用于处理副作用，例如数据获取、订阅、手动修改 DOM：

```tsx
import { useEffect } from 'react'

function Title() {
  useEffect(() => {
    document.title = 'Kairos'
  }, [])

  return <div>页面标题已修改</div>
}
```

第二个参数是依赖数组，`[]` 表示只在组件挂载时执行一次。

### 4.5 条件渲染与列表渲染

```tsx
function UserList({ users }: { users: { id: number; name: string }[] }) {
  if (users.length === 0) return <p>暂无用户</p>

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  )
}
```

**列表渲染必须提供稳定且唯一的 `key`**，不要用数组索引。

## 5. 核心概念

### 5.1 组件化思想

把页面拆成独立组件：

```
App
├── NavBar
├── PageTransition
│   └── Routes
│       ├── Home
│       ├── Demo
│       ├── Learn
│       └── Me
└── GlobalHud
```

每个组件只负责一块 UI，便于复用和测试。

### 5.2 props 与 state 的区别

| | props | state |
|---|---|---|
| 来源 | 父组件传入 | 组件内部管理 |
| 是否可变 | 只读 | 可通过 setter 修改 |
| 作用 | 组件间通信 | 组件内部响应式数据 |

### 5.3 虚拟 DOM 与 diff

React 维护一棵虚拟 DOM 树。当 state 变化时，React 会生成新的虚拟 DOM，与旧的对比（diff），只更新真正变化的部分，减少真实 DOM 操作。

### 5.4 Hooks 规则

1. **只在顶层调用 hook**：不要在循环、条件或嵌套函数中调用。
2. **只在 React 函数组件或自定义 hook 中调用**。

### 5.5 受控组件

表单元素的值由 state 控制：

```tsx
function Input() {
  const [value, setValue] = useState('')

  return (
    <input
      value={value}
      onChange={(e) => setValue(e.target.value)}
    />
  )
}
```

## 6. 在 Kairos 中的应用

### 6.1 应用入口

看 `frontends/portfolio/src/main.tsx`：

```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

`createRoot` 是 React 18 的新 API，支持并发特性。

### 6.2 路由配置

看 `frontends/portfolio/src/App.tsx`：

```tsx
import { Routes, Route, useLocation } from 'react-router-dom'
import NavBar from './components/NavBar'
import Home from './pages/Home'
import Demo from './pages/Demo'
// ...

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
          {/* ... */}
        </Routes>
      </PageTransition>
      <GlobalHud />
    </div>
  )
}
```

这里用 `react-router-dom` 管理多页面路由，`useLocation` 获取当前路径。

### 6.3 NavBar 组件

看 `frontends/portfolio/src/components/NavBar.tsx`：

```tsx
import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

const ITEMS = [
  { to: '/', label: '首页' },
  { to: '/rag', label: 'AI 作品' },
  { to: '/learn', label: '学习' },
  // ...
]

export default function NavBar() {
  const { pathname } = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)

  const isActive = (to: string) => {
    if (to === '/') return pathname === '/'
    return pathname.startsWith(to)
  }

  return (
    <nav>
      {ITEMS.map((it) => (
        <Link key={it.to} to={it.to} className={...}>
          {it.label}
        </Link>
      ))}
    </nav>
  )
}
```

- `useState(false)` 管理移动端菜单开关。
- `useLocation()` 获取当前路径，用于高亮当前导航项。
- `ITEMS.map` 渲染导航列表，`key={it.to}` 使用稳定唯一的路径作为 key。

### 6.4 页面切换动画

`App.tsx` 中 `PageTransition key={pathname}`：

```tsx
<PageTransition key={pathname}>
  <Routes>{/* ... */}</Routes>
</PageTransition>
```

通过把 `pathname` 作为 `key`，路由切换时 `PageTransition` 会重新挂载，从而触发动画。

## 7. 常见错误与排查

| 错误信息 | 可能原因 | 解决方法 |
|---|---|---|
| `Each child in a list should have a unique "key" prop` | 列表渲染缺少 key | 使用稳定唯一值作为 key |
| `Too many re-renders` | setState 在渲染时直接调用 | 把 setState 放到事件处理函数中 |
| `Hooks can only be called inside the body of a function component` | hook 放在条件分支或普通函数里 | 把 hook 提到组件顶层 |
| `useEffect` 无限循环 | 依赖数组遗漏 state | 补全依赖或改用合适依赖 |
| `ReactDOM.createRoot` 报错 | 重复调用 createRoot | 确保只调用一次 |

## 8. 常见面试问法

- "useEffect 什么时候执行？依赖数组的作用是什么？"
- "React 渲染优化有哪些手段？"
- "props 和 state 的区别是什么？"
- "React 18 的并发特性你了解吗？"
- "虚拟 DOM 是什么？diff 算法做了什么？"
- "为什么列表渲染需要 key？"

## 9. 下一步

React 基础已经掌握。你可以：

- 回到 [Kairos 技术概念地图](kairos-concept-map.md)，把 React 标记为已掌握
- 继续学习 [Vite 零基础入门](vite-basics.md)，理解项目如何构建
- 继续学习 [TailwindCSS 零基础入门](tailwindcss-basics.md)，理解样式系统
