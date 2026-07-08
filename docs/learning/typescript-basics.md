# TypeScript 零基础入门

> 目标：理解 TypeScript 是什么，能写带类型的简单代码，并看懂 Kairos 门户的类型声明和 `tsconfig.json` 配置。

## 1. 一句话定义

TypeScript 是 **JavaScript 的超集**，增加静态类型系统，让变量、函数、组件在运行前就能被类型检查。

## 2. 为什么存在

在 Kairos 中选择 TypeScript 的原因：

1. **提前发现错误**：把很多运行时 bug 提前到编译期发现，例如拼写错误、类型不匹配、空值访问。
2. **提升开发体验**：IDE 能提供更好的自动补全、跳转定义、重构支持。
3. **便于维护**：大型项目里代码关系复杂，类型就是最好的文档。
4. **与现代工具链配合**：Vite、React、TailwindCSS 都对 TypeScript 有良好支持。

Kairos 门户 `frontends/portfolio` 全部使用 TypeScript 编写。

## 3. 安装与验证

确保你已安装 Node.js（建议 v18+），然后：

```bash
npm install -g typescript
```

验证：

```bash
tsc --version
```

Expected: 输出类似 `Version 5.4.5`

## 4. 最小动手示例

### 4.1 基础类型

创建 `hello.ts`：

```typescript
let count: number = 0
let name: string = 'Kairos'
let isReady: boolean = true

count = 10      // OK
count = 'ten'   // 报错：Type 'string' is not assignable to type 'number'
```

编译运行：

```bash
tsc hello.ts
node hello.js
```

### 4.2 函数类型

```typescript
function add(a: number, b: number): number {
  return a + b
}

add(2, 3)      // OK
add('2', '3')  // 报错：参数类型不匹配
```

### 4.3 接口（interface）

```typescript
interface User {
  name: string
  age: number
  email?: string  // 可选字段
}

const u: User = { name: 'Alice', age: 23 }
```

### 4.4 数组与联合类型

```typescript
let ids: number[] = [1, 2, 3]
let value: string | number = 'hello'
value = 42  // OK
```

### 4.5 泛型

泛型让函数或组件在保持类型安全的同时复用逻辑：

```typescript
function identity<T>(arg: T): T {
  return arg
}

identity<number>(42)
identity<string>('Kairos')
```

## 5. 核心概念

### 5.1 类型推断与显式注解

TypeScript 能自动推断简单类型，但复杂场景建议显式声明：

```typescript
let x = 10          // 推断为 number
let y: number = 10  // 显式注解
```

### 5.2 interface 与 type

两者都能定义类型，使用场景略有不同：

```typescript
// interface 适合对象形状和继承
interface Animal {
  name: string
}
interface Dog extends Animal {
  breed: string
}

// type 适合联合类型、元组
type Theme = 'light' | 'dark'
type Point = [number, number]
```

### 5.3 any、unknown 与 never

| 类型 | 含义 | 使用建议 |
|---|---|---|
| `any` | 关闭类型检查 | 尽量少用 |
| `unknown` | 未知类型，使用前需断言或收窄 | 比 `any` 安全 |
| `never` | 不可能存在的值 | 用于 exhaustive check |

### 5.4 泛型的使用场景

组件、hook、工具函数经常用到泛型：

```typescript
function useState<T>(initial: T): [T, (v: T) => void] {
  // React 的 useState 就是泛型
}
```

### 5.5 strict: true 的意义

开启严格模式后，TypeScript 会检查更多潜在问题：隐式 `any`、空值、未使用变量等。初学者初期会被报错困扰，但这是培养类型思维的必经之路。

## 6. 在 Kairos 中的应用

### 6.1 tsconfig.json 配置

看 `frontends/portfolio/tsconfig.json`：

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true
  },
  "include": ["src"]
}
```

关键项解释：

- `strict: true`：开启所有严格类型检查。
- `moduleResolution: bundler`：配合 Vite 等现代打包器。
- `allowImportingTsExtensions: true`：允许导入 `.ts`/`.tsx` 文件，必须配合 `noEmit: true` 使用。
- `noEmit: true`：只做类型检查，不输出 JS，由 Vite 负责打包。
- `jsx: react-jsx`：使用 React 17+ 的新 JSX 转换。

### 6.2 自定义 hook 的类型

看 `frontends/portfolio/src/hooks/useTheme.ts`：

```typescript
export type Theme = 'mono-light' | 'mono' | 'light' | 'deepblue' | 'cyber' | 'machine'

export function useTheme() {
  const [theme, setThemeState] = useState<Theme>(getInitialTheme)
  // ...
  const setTheme = (t: Theme) => { /* ... */ }
  return { theme, setTheme }
}
```

这里用联合类型 `Theme` 限制了可选主题，避免非法值被写入 localStorage。

### 6.3 组件 props 类型

看 `frontends/portfolio/src/App.tsx`：

```typescript
function DemoRoute({ slug, src }: { slug: string; src: string }) {
  return <Demo slug={slug} src={src} />
}
```

直接在参数里解构并声明类型，简洁明确。

## 7. 常见错误与排查

| 错误信息 | 可能原因 | 解决方法 |
|---|---|---|
| `Type 'X' is not assignable to type 'Y'` | 类型不匹配 | 检查变量/函数返回值类型 |
| `Parameter 'x' implicitly has an 'any' type` | strict 模式下未声明参数类型 | 显式声明参数类型 |
| `Cannot find module 'react'` | 缺少 @types 包 | `npm install -D @types/react` |
| `An import path can only be preceded by...` | `allowImportingTsExtensions` 未配 `noEmit: true` | 同步 tsconfig 配置 |
| `'x' is possibly 'undefined'` | 空值未处理 | 加判断或 `!` 断言（慎用） |

## 8. 常见面试问法

- "TypeScript 和 JavaScript 的区别是什么？"
- "interface 和 type 的区别是什么？"
- "泛型在什么时候使用？"
- "`any` 和 `unknown` 有什么区别？"
- "`strict: true` 会开启哪些检查？"
- "TypeScript 编译后生成什么？"

## 9. 下一步

前端层基础教程刚刚开始。你可以：

- 回到 [Kairos 技术概念地图](kairos-concept-map.md)，把 TypeScript 标记为已掌握
- 继续学习 [React 零基础入门](react-basics.md)
- 继续学习 [Vite 零基础入门](vite-basics.md)
- 继续学习 [TailwindCSS 零基础入门](tailwindcss-basics.md)
