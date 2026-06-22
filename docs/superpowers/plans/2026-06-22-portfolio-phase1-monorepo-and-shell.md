# 个人集成学习网站 Phase 1 实现计划（清理 + monorepo 重组 + 门户外壳 + 本地 docker-compose）

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把 ai-demos 清理重组为 monorepo，做出统一的 React 门户外壳，用 iframe 集成 RAG 与 Function Calling 两个 demo，整套用 docker-compose 在本地一键跑通。

**Architecture:** 方案 C（统一外壳 + iframe）。Nginx 作唯一入口：静态托管门户外壳与学习站，反向代理到本机回环上的 RAG/FC FastAPI 后端。所有服务由一份 docker-compose.yml 编排，本地与未来线上同一份。

**Tech Stack:** Python 3.12 + FastAPI + dashscope（通义千问）；React 18 + Vite 5 + TS + Tailwind + React Router；Nginx；Docker + docker-compose。

## Global Constraints

- Python 后端统一用 **通义千问（dashscope）**，环境变量 `DASHSCOPE_API_KEY`，绝不写进代码或镜像。
- 所有后端只监听容器内端口，**不对宿主机直接暴露**，统一经 Nginx。
- `.env` 不进 git（仓库 `.gitignore` 已含）。
- 前端外壳技术栈与 `frontends/nexus-learning-web` 保持一致（React+Vite+TS+Tailwind）。
- 每个 Python 服务单 worker、懒加载重依赖。
- 工作标题「个人集成学习网站」，不含任何个人姓名/学校信息。
- 本计划**不含** Nexus Web（Phase 2）与服务器部署（Phase 3）。

---

## 文件结构（Phase 1 结束后）

```
ai-demos/
├── core/ rag/ eval/                 共享 Python 包（不动）
├── backends/
│   ├── rag_app/
│   │   ├── main.py                  ← 由 app.py 迁入
│   │   └── Dockerfile
│   └── fc_app/
│       ├── main.py                  ← 由 legacy/agent_app.py 迁入
│       └── Dockerfile
├── frontends/
│   ├── portfolio/                   ← 新建 React 门户外壳
│   │   ├── package.json vite.config.ts tsconfig*.json
│   │   ├── tailwind.config.js postcss.config.js index.html
│   │   └── src/{main.tsx,App.tsx,styles.css,
│   │            pages/{Home,Demo,Learn,Me}.tsx,
│   │            components/{NavBar,DemoFrame}.tsx,
│   │            data/works.ts}
│   └── nexus-learning-web/          ← 由根迁入
├── deploy/
│   ├── docker-compose.yml
│   └── nginx/nginx.conf
├── main.py                          Nexus CLI（不动）
├── requirements.txt CHANGELOG.md README.md
└── docs/
```

约定：`agent-console-ai/` 与 `legacy/` 在本计划中被移除；`cs-quiz-app` 的完整集成（含 Fastify+SQLite 容器）与 Nexus Web 放到后续阶段，Phase 1 的「个人」页对刷题先留入口占位。

---

### Task 1: 把 agent-console-ai 抽离出 ai-demos

**Files:**
- Move: `agent-console-ai/` → `../agent-console-ai/`（移出仓库到桌面）
- Modify: 仓库索引（git rm）

**Interfaces:**
- Consumes: 无
- Produces: 干净仓库，无 agent-console-ai

- [ ] **Step 1: 把目录移出仓库到桌面同级位置**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
mv agent-console-ai /c/Users/hzs17/Desktop/agent-console-ai
```

- [ ] **Step 2: 让被移走的目录独立成自己的 git 仓库**

```bash
cd /c/Users/hzs17/Desktop/agent-console-ai
git init
git add -A
git commit -m "chore: extract agent-console-ai into standalone repo (课程设计·鸿蒙前端)"
```

- [ ] **Step 3: 从 ai-demos 删除该目录的跟踪**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git rm -r --cached agent-console-ai 2>/dev/null; git add -A
git status -s
```
Expected: 显示 `agent-console-ai/...` 一批 `D`（deleted）

- [ ] **Step 4: 提交**

```bash
git commit -m "chore: remove agent-console-ai (extracted to standalone course project)"
```

---

### Task 2: 建立 monorepo 骨架目录

**Files:**
- Create: `backends/.gitkeep`, `frontends/.gitkeep`, `deploy/nginx/.gitkeep`

**Interfaces:**
- Consumes: 无
- Produces: 空目录结构 `backends/` `frontends/` `deploy/nginx/`

- [ ] **Step 1: 创建目录**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
mkdir -p backends frontends deploy/nginx
touch backends/.gitkeep frontends/.gitkeep deploy/nginx/.gitkeep
```

- [ ] **Step 2: 提交**

```bash
git add backends/.gitkeep frontends/.gitkeep deploy/nginx/.gitkeep
git commit -m "chore: scaffold monorepo dirs (backends/ frontends/ deploy/)"
```

---

### Task 3: 迁移 RAG 网页 → backends/rag_app

**Files:**
- Move: `app.py` → `backends/rag_app/main.py`
- Create: `backends/rag_app/__init__.py`

**Interfaces:**
- Consumes: `core.agent.Agent`, `core.rag_tool.{init_rag_tool,search_docs}`, `core.tools.TOOL_MAP`, `eval.evaluator.run_test_cases`（均位于 repo 根，导入路径不变）
- Produces: `backends.rag_app.main:app`（FastAPI 实例，路由 `/ /chat /clear /eval`）

- [ ] **Step 1: 移动文件**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git mv app.py backends/rag_app/main.py
touch backends/rag_app/__init__.py
```

- [ ] **Step 2: 确认导入无需改动（core./eval. 仍从 repo 根解析）**

Run: `grep -nE "^from (core|eval)" backends/rag_app/main.py`
Expected: 显示 `from core.agent import Agent` 等 4 行，无需修改。

- [ ] **Step 3: 本地验证能从 repo 根启动**

```bash
./venv/Scripts/python.exe -m uvicorn backends.rag_app.main:app --port 8001 &
sleep 4 && curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/ ; kill %1
```
Expected: `200`

- [ ] **Step 4: 提交**

```bash
git add -A
git commit -m "refactor: move RAG web app to backends/rag_app"
```

---

### Task 4: 迁移 Function Calling 网页 → backends/fc_app

**Files:**
- Move: `legacy/agent_app.py` → `backends/fc_app/main.py`
- Create: `backends/fc_app/__init__.py`

**Interfaces:**
- Consumes: 无内部依赖（自包含：内联工具 + 内联 HTML，用 dashscope）
- Produces: `backends.fc_app.main:app`（FastAPI 实例，路由 `/ /chat /clear`）

- [ ] **Step 1: 移动文件**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git mv legacy/agent_app.py backends/fc_app/main.py
touch backends/fc_app/__init__.py
```

- [ ] **Step 2: 本地验证启动**

```bash
./venv/Scripts/python.exe -m uvicorn backends.fc_app.main:app --port 8002 &
sleep 4 && curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8002/ ; kill %1
```
Expected: `200`

- [ ] **Step 3: 提交**

```bash
git add -A
git commit -m "refactor: promote FC agent web to backends/fc_app"
```

---

### Task 5: 删除剩余 legacy/

**Files:**
- Delete: `legacy/`（agent.py, app.py, rag.py, step1-4*.py, test_api.py）

**Interfaces:**
- Consumes: 无（已确认无代码引用 legacy）
- Produces: 仓库无 legacy 目录

- [ ] **Step 1: 再次确认无人引用 legacy**

Run: `grep -rnE "from legacy|import legacy" --include="*.py" . | grep -v "/venv/"`
Expected: 无输出

- [ ] **Step 2: 删除并提交**

```bash
git rm -r legacy
git commit -m "chore: remove legacy demos (preserved in git history)"
```

---

### Task 6: 迁移学习站点 → frontends/nexus-learning-web

**Files:**
- Move: `nexus-learning-web/` → `frontends/nexus-learning-web/`

**Interfaces:**
- Consumes: 无
- Produces: 学习站点位于 `frontends/nexus-learning-web`，构建产物供 Nginx 托管于 `/learn`

- [ ] **Step 1: 移动目录（node_modules 已被其 .gitignore 忽略）**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git mv nexus-learning-web frontends/nexus-learning-web
```

- [ ] **Step 2: 设置子路径 base，使其能挂在 /learn 下**

Modify `frontends/nexus-learning-web/vite.config.ts`，在 `defineConfig({...})` 内加入 `base: '/learn/'`：

```ts
export default defineConfig({
  base: '/learn/',
  plugins: [react()],
  // ...existing config...
})
```

- [ ] **Step 3: 验证构建通过**

```bash
cd frontends/nexus-learning-web && npm install && npm run build
ls dist/index.html
```
Expected: `dist/index.html` 存在

- [ ] **Step 4: 提交**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add -A
git commit -m "refactor: move nexus-learning-web into frontends/ with /learn base"
```

---

### Task 7: 新建门户外壳 React 工程骨架

**Files:**
- Create: `frontends/portfolio/package.json`, `vite.config.ts`, `tsconfig.json`, `tsconfig.node.json`, `tailwind.config.js`, `postcss.config.js`, `index.html`, `src/main.tsx`, `src/styles.css`

**Interfaces:**
- Consumes: 无
- Produces: 可 `npm run build` 的空壳 Vite+React+TS+Tailwind 工程，输出到 `dist/`

- [ ] **Step 1: 写 package.json**

```json
{
  "name": "portfolio",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.4",
    "typescript": "^5.4.5",
    "vite": "^5.3.1"
  }
}
```

- [ ] **Step 2: 写 vite.config.ts（门户挂在根路径 /）**

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: '/',
  plugins: [react()],
  server: { port: 5180 },
})
```

- [ ] **Step 3: 写 tsconfig.json 与 tsconfig.node.json**

`tsconfig.json`:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```
`tsconfig.node.json`:
```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true
  },
  "include": ["vite.config.ts"]
}
```

- [ ] **Step 4: 写 tailwind.config.js 与 postcss.config.js**

`tailwind.config.js`:
```js
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: { extend: {} },
  plugins: [],
}
```
`postcss.config.js`:
```js
export default { plugins: { tailwindcss: {}, autoprefixer: {} } }
```

- [ ] **Step 5: 写 index.html、src/main.tsx、src/styles.css**

`index.html`:
```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>个人集成学习网站</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```
`src/styles.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```
`src/main.tsx`:
```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './styles.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>,
)
```

- [ ] **Step 6: 安装依赖并验证构建（此时 App 尚未建，先放占位）**

临时 `src/App.tsx`:
```tsx
export default function App() {
  return <div>portfolio shell</div>
}
```
Run:
```bash
cd frontends/portfolio && npm install && npm run build && ls dist/index.html
```
Expected: `dist/index.html` 存在

- [ ] **Step 7: 提交**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add frontends/portfolio
git commit -m "feat: scaffold portfolio shell (React+Vite+TS+Tailwind)"
```

---

### Task 8: 门户数据与页面组件

**Files:**
- Create: `src/data/works.ts`, `src/components/NavBar.tsx`, `src/components/DemoFrame.tsx`, `src/pages/Home.tsx`, `src/pages/Demo.tsx`, `src/pages/Learn.tsx`, `src/pages/Me.tsx`
- Modify: `src/App.tsx`（替换占位为路由）

**Interfaces:**
- Consumes: react-router-dom
- Produces: 路由 `/ /rag /fc /learn /me`；`works.ts` 导出 `WORKS: Work[]`，`Work = { slug:string; title:string; desc:string; tech:string[]; github?:string; path:string }`

- [ ] **Step 1: 写 src/data/works.ts**

```ts
export type Work = {
  slug: string
  title: string
  desc: string
  tech: string[]
  github?: string
  path: string        // 站内路由
}

export const WORKS: Work[] = [
  { slug: 'rag', title: 'RAG 文档问答', desc: '基于检索增强生成的私有知识库问答。',
    tech: ['RAG', 'Chroma', '通义千问', 'FastAPI'], path: '/rag' },
  { slug: 'fc', title: 'Function Calling Agent', desc: '大模型自动决策并调用工具完成任务。',
    tech: ['Function Calling', '通义千问', 'FastAPI'], path: '/fc' },
  { slug: 'learn', title: 'Nexus 交互式学习站', desc: 'LLM/Agent/RAG 的交互式课程与测验。',
    tech: ['React', 'Vite', 'TypeScript'], path: '/learn' },
]
```

- [ ] **Step 2: 写 src/components/NavBar.tsx**

```tsx
import { Link, useLocation } from 'react-router-dom'

const ITEMS = [
  { to: '/', label: '首页' },
  { to: '/rag', label: 'AI作品' },
  { to: '/learn', label: '学习' },
  { to: '/me', label: '个人' },
]

export default function NavBar() {
  const { pathname } = useLocation()
  return (
    <nav className="flex gap-6 px-6 py-4 border-b bg-white sticky top-0 z-10">
      <span className="font-bold">个人集成学习网站</span>
      <div className="flex gap-4 ml-auto">
        {ITEMS.map((it) => (
          <Link key={it.to} to={it.to}
            className={pathname === it.to ? 'font-semibold text-blue-600' : 'text-gray-600'}>
            {it.label}
          </Link>
        ))}
      </div>
    </nav>
  )
}
```

- [ ] **Step 3: 写 src/components/DemoFrame.tsx（iframe + 技术说明面板）**

```tsx
import { Work } from '../data/works'

export default function DemoFrame({ work, src }: { work: Work; src: string }) {
  return (
    <div className="flex flex-col lg:flex-row gap-4 p-6">
      <iframe title={work.title} src={src}
        className="flex-1 min-h-[70vh] border rounded-lg" />
      <aside className="lg:w-80 shrink-0 space-y-3">
        <h2 className="text-xl font-bold">{work.title}</h2>
        <p className="text-gray-600">{work.desc}</p>
        <div className="flex flex-wrap gap-2">
          {work.tech.map((t) => (
            <span key={t} className="px-2 py-1 text-xs bg-gray-100 rounded">{t}</span>
          ))}
        </div>
        {work.github && (
          <a href={work.github} className="text-blue-600 underline" target="_blank">查看源码</a>
        )}
      </aside>
    </div>
  )
}
```

- [ ] **Step 4: 写四个页面**

`src/pages/Home.tsx`:
```tsx
import { Link } from 'react-router-dom'
import { WORKS } from '../data/works'

export default function Home() {
  return (
    <div className="max-w-5xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2">个人集成学习网站</h1>
      <p className="text-gray-600 mb-8">AI 应用与 Agent 相关作品的集中展示。</p>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {WORKS.map((w) => (
          <Link key={w.slug} to={w.path}
            className="block p-5 border rounded-lg hover:shadow transition">
            <h3 className="font-semibold mb-1">{w.title}</h3>
            <p className="text-sm text-gray-600">{w.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
```
`src/pages/Demo.tsx`:
```tsx
import { WORKS } from '../data/works'
import DemoFrame from '../components/DemoFrame'

export default function Demo({ slug, src }: { slug: string; src: string }) {
  const work = WORKS.find((w) => w.slug === slug)!
  return <DemoFrame work={work} src={src} />
}
```
`src/pages/Learn.tsx`:
```tsx
export default function Learn() {
  // 学习站点由 Nginx 静态托管于 /learn，这里直接跳转
  if (typeof window !== 'undefined') window.location.href = '/learn/'
  return null
}
```
`src/pages/Me.tsx`:
```tsx
export default function Me() {
  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      <section>
        <h2 className="text-xl font-bold mb-2">技能栈</h2>
        <p className="text-gray-600">Python · FastAPI · RAG · LangChain · React · Docker · AI/Agent 工程</p>
      </section>
      <section>
        <h2 className="text-xl font-bold mb-2">简历</h2>
        <a href="/resume.pdf" className="text-blue-600 underline" target="_blank">下载简历（PDF）</a>
      </section>
      <section>
        <h2 className="text-xl font-bold mb-2">项目</h2>
        <ul className="list-disc pl-5 text-gray-600 space-y-1">
          <li><a href="/quiz/" className="text-blue-600 underline">cs-quiz-app 面试题库（待集成）</a></li>
        </ul>
      </section>
    </div>
  )
}
```

- [ ] **Step 5: 改写 src/App.tsx 接入路由**

```tsx
import { Routes, Route } from 'react-router-dom'
import NavBar from './components/NavBar'
import Home from './pages/Home'
import Demo from './pages/Demo'
import Learn from './pages/Learn'
import Me from './pages/Me'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/rag" element={<Demo slug="rag" src="/rag/" />} />
        <Route path="/fc" element={<Demo slug="fc" src="/fc/" />} />
        <Route path="/learn" element={<Learn />} />
        <Route path="/me" element={<Me />} />
      </Routes>
    </div>
  )
}
```

- [ ] **Step 6: 构建验证**

```bash
cd frontends/portfolio && npm run build && ls dist/index.html
```
Expected: 构建无 TS 错误，`dist/index.html` 存在

- [ ] **Step 7: 提交**

```bash
cd /c/Users/hzs17/Desktop/ai-demos
git add frontends/portfolio
git commit -m "feat: portfolio pages, nav, and iframe demo frame"
```

---

### Task 9: 为 rag_app 与 fc_app 写 Dockerfile

**Files:**
- Create: `backends/rag_app/Dockerfile`, `backends/fc_app/Dockerfile`, `.dockerignore`

**Interfaces:**
- Consumes: repo 根的 `requirements.txt`、`core/`、`rag/`、`eval/`
- Produces: 两个镜像，分别在容器内 8001/8002 提供 uvicorn 服务

- [ ] **Step 1: 写 .dockerignore（repo 根）**

```
venv/
**/node_modules/
**/dist/
__pycache__/
*.pyc
.env
chroma_db/
.git/
```

- [ ] **Step 2: 写 backends/rag_app/Dockerfile（build context = repo 根）**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY core/ ./core/
COPY rag/ ./rag/
COPY eval/ ./eval/
COPY docs/ ./docs/
COPY backends/rag_app/ ./backends/rag_app/
CMD ["uvicorn", "backends.rag_app.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
```

- [ ] **Step 3: 写 backends/fc_app/Dockerfile（build context = repo 根）**

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backends/fc_app/ ./backends/fc_app/
CMD ["uvicorn", "backends.fc_app.main:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "1"]
```

- [ ] **Step 4: 提交**

```bash
git add backends/rag_app/Dockerfile backends/fc_app/Dockerfile .dockerignore
git commit -m "build: add Dockerfiles for rag_app and fc_app"
```

---

### Task 10: 写 Nginx 配置

**Files:**
- Create: `deploy/nginx/nginx.conf`

**Interfaces:**
- Consumes: 容器服务名 `rag:8001`、`fc:8002`；静态目录 `/usr/share/nginx/html`（门户）、`/usr/share/nginx/learn`（学习站）
- Produces: 路由 `/` `/rag` `/fc` `/learn` 的对外服务

- [ ] **Step 1: 写 deploy/nginx/nginx.conf**

```nginx
server {
    listen 80;
    server_name _;

    # 门户外壳（SPA，history 路由回退到 index.html）
    root /usr/share/nginx/html;
    index index.html;
    location / { try_files $uri $uri/ /index.html; }

    # 学习站点（静态，base=/learn/）
    location /learn/ {
        alias /usr/share/nginx/learn/;
        try_files $uri $uri/ /learn/index.html;
    }

    # RAG 后端
    location /rag/ {
        proxy_pass http://rag:8001/;
        proxy_set_header Host $host;
    }
    # Function Calling 后端
    location /fc/ {
        proxy_pass http://fc:8002/;
        proxy_set_header Host $host;
    }
}
```

- [ ] **Step 2: 提交**

```bash
git add deploy/nginx/nginx.conf
git commit -m "build: add nginx reverse-proxy + static hosting config"
```

---

### Task 11: 写 docker-compose 编排

**Files:**
- Create: `deploy/docker-compose.yml`
- Create: `deploy/build-frontends.sh`（构建前端并把产物放到 nginx 挂载目录）

**Interfaces:**
- Consumes: 各 Dockerfile、`frontends/portfolio/dist`、`frontends/nexus-learning-web/dist`、repo 根 `.env`
- Produces: `docker compose up` 启动 nginx(对外 8080) + rag + fc

- [ ] **Step 1: 写 deploy/build-frontends.sh**

```bash
#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
( cd "$ROOT/frontends/portfolio" && npm install && npm run build )
( cd "$ROOT/frontends/nexus-learning-web" && npm install && npm run build )
echo "frontends built: portfolio/dist, nexus-learning-web/dist"
```

- [ ] **Step 2: 写 deploy/docker-compose.yml**

```yaml
services:
  rag:
    build:
      context: ..
      dockerfile: backends/rag_app/Dockerfile
    env_file: ../.env
    restart: always
    expose: ["8001"]

  fc:
    build:
      context: ..
      dockerfile: backends/fc_app/Dockerfile
    env_file: ../.env
    restart: always
    expose: ["8002"]

  nginx:
    image: nginx:1.27-alpine
    ports: ["8080:80"]
    restart: always
    depends_on: [rag, fc]
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - ../frontends/portfolio/dist:/usr/share/nginx/html:ro
      - ../frontends/nexus-learning-web/dist:/usr/share/nginx/learn:ro
```

- [ ] **Step 3: 提交**

```bash
git add deploy/docker-compose.yml deploy/build-frontends.sh
git commit -m "build: add docker-compose orchestration and frontend build script"
```

---

### Task 12: 本地端到端冒烟测试

**Files:**
- Create: `deploy/README.md`（本地运行步骤）

**Interfaces:**
- Consumes: 全部前序任务
- Produces: 本地 `http://127.0.0.1:8080` 可访问门户 + RAG/FC demo + 学习站

- [ ] **Step 1: 确保 repo 根有 .env（含 DASHSCOPE_API_KEY）**

Run: `grep -q DASHSCOPE_API_KEY .env && echo OK || echo "缺 .env"`
Expected: `OK`（若缺，从 `.env.example` 复制并填入 Key）

- [ ] **Step 2: 构建前端产物**

```bash
bash deploy/build-frontends.sh
```
Expected: 末行打印 `frontends built: ...`

- [ ] **Step 3: 起 compose**

```bash
docker compose -f deploy/docker-compose.yml up -d --build
docker compose -f deploy/docker-compose.yml ps
```
Expected: `nginx`、`rag`、`fc` 三个服务 `running`

- [ ] **Step 4: 逐路径冒烟**

```bash
for p in / /rag/ /fc/ /learn/; do
  printf "%s -> " "$p"; curl -s -o /dev/null -w "%{http_code}\n" "http://127.0.0.1:8080$p"
done
```
Expected: 四行均为 `200`

- [ ] **Step 5: 写 deploy/README.md（运行步骤）**

```markdown
# 本地运行

1. repo 根放好 `.env`（含 DASHSCOPE_API_KEY）
2. `bash deploy/build-frontends.sh` 构建前端
3. `docker compose -f deploy/docker-compose.yml up -d --build`
4. 浏览器访问 http://127.0.0.1:8080
5. 停止：`docker compose -f deploy/docker-compose.yml down`

> 改了前端代码后需重新执行第 2、3 步；改了后端代码只需第 3 步加 `--build`。
```

- [ ] **Step 6: 提交**

```bash
git add deploy/README.md
git commit -m "docs: add local run guide; Phase 1 portfolio runs via docker-compose"
```

---

## 后续阶段（不在本计划内）

- **Phase 2**：Nexus Web 后端（FastAPI + SSE 多智能体可视化）→ `backends/nexus_app`，门户加 `/nexus` 路由与卡片。
- **Phase 3**：cs-quiz-app 完整集成（Fastify+SQLite 容器 + `/quiz` 静态前端）。
- **Phase 4**：部署到首尔服务器（Ubuntu + swap + Docker + 域名 A 记录 + Let's Encrypt HTTPS）。
- **后续**：博客；把 demo 由 iframe 逐个重写为原生 React（演进到方案 A）。
