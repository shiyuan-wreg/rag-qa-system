# Kairos 前端层零基础伴读教程实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 补齐 Kairos 前端门户层四篇零基础伴读教程（TypeScript、React、Vite、TailwindCSS），更新概念地图链接与项目状态文档，最终提交并推送到 master。

**Architecture:** 沿用后端层/基础设施层教程的统一结构（一句话定义→为什么存在→安装→最小示例→核心概念→项目实例→常见错误→面试问法→下一步），每篇结合 `frontends/portfolio` 真实代码，让零基础读者能看懂 Kairos 前端实现。

**Tech Stack:** Markdown 文档、React + TypeScript + Vite + TailwindCSS（仅作示例引用，不修改前端源码）。

## Global Constraints

- 教程文件统一放在 `docs/learning/` 目录，文件名沿用 `<topic>-basics.md` 约定。
- 每篇教程必须包含：目标、一句话定义、为什么存在、安装与验证、最小动手示例、核心概念、Kairos 项目实例、常见错误与排查、常见面试问法、下一步。
- 项目实例必须引用 `frontends/portfolio` 真实代码，不可编造路径或函数名。
- 概念地图更新只修改"推荐学习资源"中的零基础教程链接，不改动已有 7 字段模板内容。
- 所有改动最终需要一次 git commit + push。
- 不改动任何前端源代码、不改动构建产物、不引入新依赖。

---

## File Structure

| 文件 | 用途 |
|---|---|
| `docs/learning/typescript-basics.md` | TypeScript 零基础教程（新建） |
| `docs/learning/react-basics.md` | React 零基础教程（新建） |
| `docs/learning/vite-basics.md` | Vite 零基础教程（新建） |
| `docs/learning/tailwindcss-basics.md` | TailwindCSS 零基础教程（新建） |
| `docs/learning/kairos-concept-map.md` | 更新前端 4 个节点的零基础教程链接 |
| `docs/PROJECT-STATE.md` | 标记前端层教程完成，更新下一步 |
| `docs/session-log.md` | 记录本次会话完成内容与未做事项 |
| `docs/superpowers/plans/2026-07-08-frontend-basics-tutorials.md` | 本计划文件（已存在） |

---

### Task 1: Write TypeScript basics tutorial

**Files:**
- Create: `docs/learning/typescript-basics.md`

**Interfaces:**
- Consumes: Existing tutorial style from `docs/learning/fastapi-basics.md`
- Produces: A standalone markdown file covering TypeScript fundamentals with Kairos examples

- [ ] **Step 1: Create file with header and goal**

  写入标题 `# TypeScript 零基础入门` 和目标段落：
  > 目标：理解 TypeScript 是什么，能写带类型的简单代码，并看懂 Kairos 门户的类型声明和 `tsconfig.json` 配置。

- [ ] **Step 2: Write sections 1-3 (definition, why exists, install)**

  - 一句话定义：TypeScript 是 JavaScript 的超集，增加静态类型，让变量、函数、组件在运行前就能被类型系统检查。
  - 为什么存在：大项目里动态类型容易隐藏错误；TypeScript 把很多运行时 bug 提前到编译期发现，同时提升 IDE 补全、重构和可维护性。
  - 安装与验证：
    ```bash
    npm install -g typescript
    tsc --version
    ```
    Expected: `Version 5.x.x`

- [ ] **Step 3: Write section 4 (minimal hands-on examples)**

  包含：
  - 基础类型：`let count: number = 0; let name: string = 'Kairos'; let ok: boolean = true;`
  - 函数类型：`function add(a: number, b: number): number { return a + b }`
  - 接口：
    ```typescript
    interface User {
      name: string
      age: number
      email?: string
    }
    ```
  - 数组与联合类型：`let ids: number[] = [1, 2, 3]; let value: string | number = 'x'`
  - 泛型：
    ```typescript
    function identity<T>(arg: T): T { return arg }
    identity<number>(42)
    ```

- [ ] **Step 4: Write section 5 (core concepts)**

  - 类型推断与显式注解
  - `interface` vs `type`
  - `any` vs `unknown` vs `never`
  - 泛型的使用场景
  - `strict: true` 的意义

- [ ] **Step 5: Write section 6 (Kairos examples)**

  引用：
  - `frontends/portfolio/tsconfig.json` 中的 `strict: true`、`moduleResolution: bundler`、`noEmit: true`、`allowImportingTsExtensions: true`
  - `frontends/portfolio/src/hooks/useTheme.ts` 中的 `export type Theme = 'mono-light' | ...` 联合类型、`useState<Theme>(...)` 泛型
  - `frontends/portfolio/src/App.tsx` 中的 `{ slug: string; src: string }` props 类型

- [ ] **Step 6: Write sections 7-9 (errors, interview, next steps)**

  常见错误表格：
  | 错误信息 | 可能原因 | 解决方法 |
  |---|---|---|
  | `Type 'X' is not assignable to type 'Y'` | 类型不匹配 | 检查变量/函数返回值类型 |
  | `Parameter 'x' implicitly has an 'any' type` | strict 模式下未声明参数类型 | 显式声明参数类型 |
  | `Cannot find module 'react'` | 缺少 @types 包 | `npm install -D @types/react` |
  | `TS5097: An import path can only be preceded by ...` | `allowImportingTsExtensions` 未配 `noEmit: true` | 同步 tsconfig |

  面试问法至少 5 题，下一步指向 React 教程或概念地图。

---

### Task 2: Write React basics tutorial

**Files:**
- Create: `docs/learning/react-basics.md`

**Interfaces:**
- Consumes: Tutorial style and TypeScript context from Task 1
- Produces: A standalone markdown file covering React fundamentals with Kairos examples

- [ ] **Step 1: Create file with header and goal**

  标题 `# React 零基础入门`，目标：
  > 目标：理解 React 是什么，能写简单的函数组件，并看懂 Kairos 门户的页面和组件结构。

- [ ] **Step 2: Write sections 1-3 (definition, why exists, install)**

  - 一句话定义：用于构建用户界面的 JavaScript 库，通过组件和声明式渲染把 UI 拆成可复用的模块。
  - 为什么存在：传统命令式 DOM 操作难以维护复杂页面；React 用组件化、状态驱动 UI 和虚拟 DOM，让界面开发更可预测、可复用。
  - 安装与验证：
    ```bash
    npx create-vite@latest my-app --template react-ts
    cd my-app
    npm install
    npm run dev
    ```

- [ ] **Step 3: Write section 4 (minimal hands-on examples)**

  包含：
  - JSX 基础：
    ```tsx
    function App() {
      return <h1>Hello, React!</h1>
    }
    ```
  - 组件与 props：
    ```tsx
    function Welcome({ name }: { name: string }) {
      return <p>Welcome, {name}</p>
    }
    ```
  - state 与事件：
    ```tsx
    import { useState } from 'react'
    function Counter() {
      const [count, setCount] = useState(0)
      return <button onClick={() => setCount(count + 1)}>{count}</button>
    }
    ```
  - useEffect 基础：
    ```tsx
    import { useEffect } from 'react'
    useEffect(() => {
      document.title = 'Kairos'
    }, [])
    ```

- [ ] **Step 4: Write section 5 (core concepts)**

  - JSX 是语法糖，编译后变成 `React.createElement`
  - 组件是函数，props 只读，state 可变且触发重新渲染
  - 虚拟 DOM 与 diff
  - hooks 规则：只在顶层调用、只在 React 函数中调用
  - 列表渲染与 `key` 的重要性

- [ ] **Step 5: Write section 6 (Kairos examples)**

  引用：
  - `frontends/portfolio/src/main.tsx` 中的 `ReactDOM.createRoot`
  - `frontends/portfolio/src/App.tsx` 中的 `Routes`、`Route`、`useLocation`、`DemoRoute` 组件
  - `frontends/portfolio/src/components/NavBar.tsx` 中的 `useState`、`useLocation`、`ITEMS.map` 列表渲染、`key={it.to}`
  - 说明 `key={pathname}` 在 `PageTransition` 上触发切换动画

- [ ] **Step 6: Write sections 7-9 (errors, interview, next steps)**

  常见错误表格：
  | 错误信息 | 可能原因 | 解决方法 |
  |---|---|---|
  | `Each child in a list should have a unique "key" prop` | 列表渲染缺少 key | 使用稳定唯一值作为 key |
  | `Too many re-renders` | setState 在渲染时直接调用 | 把 setState 放到事件处理函数中 |
  | `Hooks can only be called inside the body of a function component` | hook 放在条件分支或普通函数里 | 把 hook 提到组件顶层 |
  | `useEffect` 无限循环 | 依赖数组遗漏 state | 补全依赖或改用合适依赖 |

  面试问法至少 5 题，下一步指向 Vite 或 TailwindCSS 教程。

---

### Task 3: Write Vite basics tutorial

**Files:**
- Create: `docs/learning/vite-basics.md`

**Interfaces:**
- Consumes: React context from Task 2
- Produces: A standalone markdown file covering Vite fundamentals with Kairos examples

- [ ] **Step 1: Create file with header and goal**

  标题 `# Vite 零基础入门`，目标：
  > 目标：理解 Vite 是什么，能启动开发服务器和打包项目，并看懂 Kairos 门户的构建配置。

- [ ] **Step 2: Write sections 1-3 (definition, why exists, install)**

  - 一句话定义：现代前端构建工具，基于原生 ES 模块和 esbuild/Rollup，提供极快的开发服务器和生产打包能力。
  - 为什么存在：传统 Webpack 项目配置复杂、冷启动慢、热更新慢；Vite 利用浏览器原生 ESM 实现秒级启动，并借助 esbuild 和 Rollup 兼顾开发与生产构建性能。
  - 安装与验证：使用 `npm create vite@latest my-app -- --template react-ts`

- [ ] **Step 3: Write section 4 (minimal hands-on examples)**

  包含：
  - 创建项目、启动开发服务器、访问 `http://localhost:5173`
  - 修改 `src/App.tsx` 观察 HMR
  - 生产构建：`npm run build` 生成 `dist/`
  - 预览生产包：`npm run preview`

- [ ] **Step 4: Write section 5 (core concepts)**

  - 开发服务器：基于原生 ESM，按需编译
  - esbuild：开发阶段预构建依赖、转译 TypeScript/JSX
  - Rollup：生产阶段打包、tree-shaking、代码分割
  - HMR（热模块替换）
  - `vite.config.ts` 与插件生态
  - 环境变量：`.env` 中以 `VITE_` 开头的变量可在客户端使用

- [ ] **Step 5: Write section 6 (Kairos examples)**

  引用：
  - `frontends/portfolio/vite.config.ts` 中的 `defineConfig`、`@vitejs/plugin-react`、`base: '/'`、`server.port: 5180`、demo 代理规则
  - `frontends/portfolio/package.json` 中的 `dev`、`build`、`preview` 脚本
  - 说明 `build: "tsc && vite build"` 先类型检查再打包

- [ ] **Step 6: Write sections 7-9 (errors, interview, next steps)**

  常见错误表格：
  | 错误信息 | 可能原因 | 解决方法 |
  |---|---|---|
  | `Cannot GET /rag` | 开发代理未命中或 SPA 路由冲突 | 检查代理路径是否带尾斜杠 |
  | `tsc` 报错但 Vite dev 正常 | 类型错误会阻止生产构建 | 先修复类型错误再 build |
  | HMR 不生效 | 某些导出方式导致 | 使用命名导出或默认导出规范 |
  | 静态资源 404 | 路径写法在 dev/prod 不一致 | 使用相对路径或配置 alias |

  面试问法至少 5 题，下一步指向 TailwindCSS 教程。

---

### Task 4: Write TailwindCSS basics tutorial

**Files:**
- Create: `docs/learning/tailwindcss-basics.md`

**Interfaces:**
- Consumes: Vite context from Task 3
- Produces: A standalone markdown file covering TailwindCSS fundamentals with Kairos examples

- [ ] **Step 1: Create file with header and goal**

  标题 `# TailwindCSS 零基础入门`，目标：
  > 目标：理解 TailwindCSS 是什么，能用工具类写样式，并看懂 Kairos 门户的主题系统。

- [ ] **Step 2: Write sections 1-3 (definition, why exists, install)**

  - 一句话定义：实用类优先（utility-first）的 CSS 框架，通过组合大量细粒度类名来构建界面样式。
  - 为什么存在：传统手写 CSS 容易出现命名冲突、样式冗余和文件分散；Tailwind 把常见样式封装成类名，让开发者直接在 HTML/JSX 中组合，提高开发效率和一致性。
  - 安装与验证：
    ```bash
    npm install -D tailwindcss postcss autoprefixer
    npx tailwindcss init -p
    ```

- [ ] **Step 3: Write section 4 (minimal hands-on examples)**

  包含：
  - `tailwind.config.js` 基础配置
  - `index.css` 中导入：
    ```css
    @tailwind base;
    @tailwind components;
    @tailwind utilities;
    ```
  - 在 JSX 中使用：
    ```html
    <div class="flex items-center justify-center h-screen bg-gray-900 text-white">
      <h1 class="text-3xl font-bold">Hello Tailwind</h1>
    </div>
    ```
  - 响应式：`className="text-sm md:text-base lg:text-lg"`
  - 状态变体：`hover:bg-blue-700 focus:outline-none`

- [ ] **Step 4: Write section 5 (core concepts)**

  - utility-first 思想
  - JIT（Just-In-Time）模式
  - 自定义主题扩展（colors、spacing、fontFamily 等）
  - 响应式前缀（移动端优先）
  - 深色模式与 CSS 变量结合
  - 与自定义 CSS 的职责分离

- [ ] **Step 5: Write section 6 (Kairos examples)**

  引用：
  - `frontends/portfolio/tailwind.config.js` 中的 `colors.base: 'var(--bg-base)'`、`colors.surface`、自定义 spacing/fontFamily
  - `frontends/portfolio/src/components/NavBar.tsx` 中的 `sticky top-0 z-50 bg-surface/90 backdrop-blur`、`max-w-wide mx-auto px-4 sm:px-6 lg:px-8`
  - 说明主题切换通过 `data-theme` 改变 CSS 变量，Tailwind 配置引用这些变量

- [ ] **Step 6: Write sections 7-9 (errors, interview, next steps)**

  常见错误表格：
  | 错误信息/现象 | 可能原因 | 解决方法 |
  |---|---|---|
  | Tailwind 类不生效 | `content` 配置未覆盖文件路径 | 检查 tailwind.config.js 的 content |
  | 自定义颜色无效 | CSS 变量名与 Tailwind 配置不一致 | 统一变量命名 |
  | 响应式样式不生效 | 断点理解错误 | 记住移动端优先 |
  | 类名太长可读性差 | JSX 中堆砌大量类 | 抽成常量、用 clsx/tailwind-merge |

  面试问法至少 5 题，下一步指向概念地图或 AI 层教程。

---

### Task 5: Update concept map with tutorial links

**Files:**
- Modify: `docs/learning/kairos-concept-map.md`

**Interfaces:**
- Consumes: Tutorial file paths from Tasks 1-4
- Produces: Updated concept map with links to all four new tutorials

- [ ] **Step 1: Update TypeScript node**

  在 TypeScript 节点的"推荐学习资源"段落后追加：
  - 零基础入门：`docs/learning/typescript-basics.md`

- [ ] **Step 2: Update React node**

  在 React 节点的"推荐学习资源"段落后追加：
  - 零基础入门：`docs/learning/react-basics.md`

- [ ] **Step 3: Update Vite node**

  在 Vite 节点的"推荐学习资源"段落后追加：
  - 零基础入门：`docs/learning/vite-basics.md`

- [ ] **Step 4: Update TailwindCSS node**

  在 TailwindCSS 节点的"推荐学习资源"段落后追加：
  - 零基础入门：`docs/learning/tailwindcss-basics.md`

---

### Task 6: Update PROJECT-STATE and session log

**Files:**
- Modify: `docs/PROJECT-STATE.md`
- Modify: `docs/session-log.md`

**Interfaces:**
- Consumes: Completion status of Tasks 1-5
- Produces: Updated project state and session log

- [ ] **Step 1: Update PROJECT-STATE.md**

  在"2026-07-07 学习资产 ✅ 已完成"节后追加"2026-07-08 前端门户层零基础教程 ✅ 已完成"：
  - 列出新增 4 篇教程
  - 标记概念地图已更新
  - 下一步改为：继续补 AI 层（LLM / Function Calling / RAG）基础教程，或按用户指定方向继续

- [ ] **Step 2: Update session-log.md**

  追加 2026-07-08 新会话记录：
  - 会话目标：继续 Kairos 前端层基础教程
  - 完成内容：4 篇教程 + 概念地图 + PROJECT-STATE
  - 未做事项：AI 层基础教程、前端源码优化、生产部署
  - 最终状态：已提交 push

---

### Task 7: Commit and push changes

**Files:**
- All new/modified markdown files in `docs/`

**Interfaces:**
- Consumes: All completed tutorial files and state updates
- Produces: A single git commit on master pushed to origin

- [ ] **Step 1: Review changes**

  运行：
  ```bash
  git status --short
  git diff --stat
  ```

- [ ] **Step 2: Stage files**

  运行：
  ```bash
  git add docs/learning/typescript-basics.md \
          docs/learning/react-basics.md \
          docs/learning/vite-basics.md \
          docs/learning/tailwindcss-basics.md \
          docs/learning/kairos-concept-map.md \
          docs/PROJECT-STATE.md \
          docs/session-log.md
  ```

- [ ] **Step 3: Commit**

  运行：
  ```bash
  git commit -m "docs(learning): add frontend basics tutorials (ts/react/vite/tailwind)

  - Add docs/learning/typescript-basics.md
  - Add docs/learning/react-basics.md
  - Add docs/learning/vite-basics.md
  - Add docs/learning/tailwindcss-basics.md
  - Link four new tutorials in kairos-concept-map.md
  - Update PROJECT-STATE.md and session-log.md
  
  Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
  ```

- [ ] **Step 4: Push**

  运行：
  ```bash
  git push origin master
  ```

  Expected: 输出包含 `master -> master` 的推送成功信息。

---

## Self-Review

**1. Spec coverage:**
- 4 篇前端零基础教程：Task 1-4 覆盖。
- 概念地图链接更新：Task 5 覆盖。
- 项目状态与会话日志更新：Task 6 覆盖。
- git 提交与推送：Task 7 覆盖。
- 无占位符：所有步骤均给出具体文件路径、代码示例和命令。

**2. Placeholder scan:**
- 无 "TBD"/"TODO"/"implement later"。
- 无 "add appropriate error handling" 等模糊描述。
- 所有代码块和命令完整可执行。

**3. Type consistency:**
- 文件名统一使用 `<topic>-basics.md`。
- 概念地图链接使用相对路径 `docs/learning/<file>.md` 风格（与后端教程一致）。
- 不修改前端源码，因此不涉及前端类型一致性问题。

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-07-08-frontend-basics-tutorials.md`.**

**Two execution options:**

1. **Subagent-Driven (recommended)** - Dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints.

**Which approach?**
