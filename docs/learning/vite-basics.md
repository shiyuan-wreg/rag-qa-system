# Vite 零基础入门

> 目标：理解 Vite 是什么，能启动开发服务器和打包项目，并看懂 Kairos 门户的构建配置。

## 1. 一句话定义

Vite 是 **现代前端构建工具**，基于浏览器原生 ES 模块和 esbuild/Rollup，提供极快的开发服务器和生产打包能力。

## 2. 为什么存在

在 Kairos 中选择 Vite 的原因：

1. **启动快**：开发服务器利用浏览器原生 ESM，冷启动几乎是秒级。
2. **热更新快**：修改代码后页面局部更新，不刷新整个应用。
3. **配置简单**：开箱即用，React、TypeScript、Vue 等通过插件一键支持。
4. **生产构建优**：使用 Rollup 打包，支持 tree-shaking 和代码分割。

Kairos 门户 `frontends/portfolio` 使用 Vite 作为构建工具。

## 3. 安装与验证

使用官方脚手架创建项目：

```bash
npm create vite@latest my-app -- --template react-ts
cd my-app
npm install
npm run dev
```

访问 http://localhost:5173，Expected: 看到 Vite + React 默认页面。

## 4. 最小动手示例

### 4.1 开发服务器

```bash
npm run dev
```

Vite 启动后：
- 开发服务器监听 `localhost:5173`（默认）。
- 浏览器直接请求原生的 ES 模块，Vite 按需编译被请求的文件。
- 修改 `src/App.tsx`，页面会热更新。

### 4.2 生产构建

```bash
npm run build
```

Expected: 生成 `dist/` 目录，包含优化后的静态资源。

### 4.3 预览生产包

```bash
npm run preview
```

Expected: 在本地启动一个生产环境预览服务器，验证打包结果。

### 4.4 配置代理

开发时经常需要把 API 请求转发到另一个服务器：

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
})
```

这样前端请求 `/api/chat` 会被转发到 `http://localhost:8000/api/chat`。

## 5. 核心概念

### 5.1 原生 ESM 开发服务器

传统打包器（如 Webpack）在开发时会把所有模块打包成一个或多个 bundle，项目越大启动越慢。Vite 直接把浏览器当成打包器，按需加载 ES 模块，所以启动速度与项目规模基本无关。

### 5.2 esbuild 与 Rollup

| 阶段 | 工具 | 作用 |
|---|---|---|
| 开发 | esbuild | 预构建依赖、转译 TypeScript/JSX，速度极快 |
| 生产 | Rollup | 打包、tree-shaking、代码分割、生成优化产物 |

### 5.3 HMR（热模块替换）

修改一个组件文件时，Vite 只更新这个模块，保持组件状态不丢失。相比整页刷新，开发效率大幅提升。

### 5.4 环境变量

Vite 支持 `.env` 文件，只有以 `VITE_` 开头的变量才能在客户端代码中使用：

```bash
# .env
VITE_API_URL=http://localhost:8000
```

```typescript
const apiUrl = import.meta.env.VITE_API_URL
```

### 5.5 base 配置

`base: '/'` 表示项目部署在域名根路径。如果未来要部署到子路径（如 `https://example.com/kairos/`），需要改为 `base: '/kairos/'`，并同步调整 Nginx 配置。

## 6. 在 Kairos 中的应用

### 6.1 vite.config.ts

看 `frontends/portfolio/vite.config.ts`：

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const demoProxy = 'http://localhost:8080'

export default defineConfig({
  base: '/',
  plugins: [react()],
  server: {
    port: 5180,
    proxy: {
      '/rag/': demoProxy,
      '/fc/': demoProxy,
      '/nexus/': demoProxy,
      '/doctomd/': demoProxy,
      '/iconforge/': demoProxy,
      '/learn/': demoProxy,
    },
  },
})
```

关键配置解释：

- `base: '/'`：部署到域名根路径。
- `plugins: [react()]`：支持 React 和 JSX/TSX 转译。
- `port: 5180`：开发服务器端口。
- `proxy`：把各 demo 路径代理到本地 Docker Nginx（:8080），与生产环境行为一致。

**注意**：代理路径使用尾斜杠（如 `/rag/`），避免命中门户 SPA 路由（`/nexus` 无斜杠会被 React Router 拦截）。

### 6.2 package.json 脚本

看 `frontends/portfolio/package.json`：

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  }
}
```

- `dev`：启动开发服务器。
- `build`：先执行 `tsc` 类型检查，再通过 `vite build` 打包。
- `preview`：预览生产构建产物。

### 6.3 生产构建流程

Kairos 的 `deploy/build-frontends.sh` 会执行：

```bash
cd frontends/portfolio
npm install
npm run build
```

生成的 `dist/` 目录会被 Nginx 挂载为静态站点根目录。

## 7. 常见错误与排查

| 错误信息/现象 | 可能原因 | 解决方法 |
|---|---|---|
| `Cannot GET /rag` | 开发代理未命中或 SPA 路由冲突 | 检查代理路径是否带尾斜杠 |
| `tsc` 报错但 Vite dev 正常 | 类型错误会阻止生产构建 | 先修复类型错误再 build |
| HMR 不生效 | 某些导出方式导致 | 使用命名导出或默认导出规范 |
| 静态资源 404 | 路径写法在 dev/prod 不一致 | 使用相对路径或配置 alias |
| 端口被占用 | 5180 被其他程序占用 | 关闭占用程序或修改 port |

## 8. 常见面试问法

- "Vite 和 Webpack 的区别是什么？"
- "Vite 为什么启动快？"
- "esbuild 和 Rollup 在 Vite 中分别负责什么？"
- "Vite 如何处理环境变量？"
- "HMR 是什么？Vite 是怎么实现的？"
- "tree-shaking 是什么？"

## 9. 下一步

Vite 构建链路已经理解。你可以：

- 回到 [Kairos 技术概念地图](kairos-concept-map.md)，把 Vite 标记为已掌握
- 继续学习 [TailwindCSS 零基础入门](tailwindcss-basics.md)，理解样式系统
- 尝试修改 `frontends/portfolio/vite.config.ts` 的代理规则，观察本地开发行为变化
