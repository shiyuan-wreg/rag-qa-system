# ai-demos 门户外壳 UI 升级设计(第一轮)

> **范围**: 门户外壳(React/Vite/Tailwind)视觉升级 + 组件体系 + 加载反馈 + 页面级更新公告。
> **本轮不做**: 主题切换器、深蓝/赛博主题、iframe demo 内部换肤(均放第二轮)。
> **主题默认**: 浅色现代风。
> **日期**: 2026-06-24

---

## 1. 目标与成功标准

### 1.1 目标

- 解决当前外壳“组件匮乏、缺乏层次、缺少加载反馈”的问题。
- 让首页、Demo 页、学习入口、个人页在视觉上统一、专业,符合 AI/Agent 求职作品集定位。
- 建立可复用的 UI 组件与 CSS 设计令牌,为后续主题切换和多主题扩展打基础。

### 1.2 成功标准

- 首页具有清晰的 Hero/内容两层视觉结构,作品卡片带搜索/筛选入口。
- Demo / Learn / Me 页共用同一套侧边栏布局组件。
- 页面级更新公告栏在每个页面顶部展示当前页面最新版本信息。
- iframe 加载有骨架屏/spinner,路由切换有过渡动画,标签页失焦/聚焦有标题反馈。
- Docker 本地构建通过,所有路径 200,无回归。

---

## 2. 设计原则

1. **层次优先**: 用字号、字重、颜色深浅、留白、阴影把页面分成导航 → 公告 → Hero → 内容 → 侧边栏 + 主内容区。
2. **统一组件**: 同一类结构(带侧边栏的内页)使用同一组件,避免每个页面自己写布局。
3. **克制反馈**: 加载与过渡反馈要明显但不过度,先解决“有没有”,再解决“好不好看”。
4. **渐进主题**: 本轮只实现默认浅色主题,但所有颜色走 CSS 变量,第二轮加主题切换器和另外两套主题时改动面最小。

---

## 3. 设计令牌(CSS 变量)

所有颜色、间距、圆角、阴影统一用 `:root` CSS 变量定义,便于未来主题切换。

```css
:root {
  /* background */
  --bg-base: #ffffff;
  --bg-soft: #f8fafc;
  --bg-hero: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);

  /* surface */
  --surface-default: #ffffff;
  --surface-raised: #ffffff;
  --surface-hover: #f1f5f9;

  /* border */
  --border-default: #e2e8f0;
  --border-subtle: #f1f5f9;

  /* text */
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-tertiary: #64748b;
  --text-muted: #94a3b8;
  --text-link: #2563eb;

  /* accent */
  --accent-primary: #0f172a;
  --accent-primary-text: #ffffff;
  --accent-secondary-bg: #eff6ff;
  --accent-secondary-text: #1d4ed8;

  /* spacing scale */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-16: 64px;

  /* radius */
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 999px;

  /* shadow */
  --shadow-sm: 0 1px 2px rgba(15, 23, 42, 0.04);
  --shadow-md: 0 1px 3px rgba(15, 23, 42, 0.06), 0 1px 2px rgba(15, 23, 42, 0.04);

  /* typography */
  --font-sans: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;

  /* max widths */
  --max-content: 1100px;
}
```

Tailwind 通过 `tailwind.config.js` 的 `extend.colors` 把这些变量映射成 Tailwind 类名(如 `bg-surface` 等),避免手写大量内联样式。

---

## 4. 页面设计

### 4.1 全局导航 `NavBar`

- 白色背景、底部 1px 边框、吸顶 `sticky top-0`。
- 左侧:Logo 方块(背景 `--accent-primary`,文字白色)+ 站点标题。
- 右侧:首页 / AI 作品 / 学习 / 个人四个链接。
- 当前页链接高亮(字重 600,颜色 `--text-primary`),其余 `--text-tertiary`。
- 移动端:链接收进汉堡菜单(用 React state + 简单展开面板,不引入新依赖)。

### 4.2 全局页面级更新公告 `PageChangelog`

- 每个页面顶部渲染一条紧凑公告条,紧贴导航下方。
- 背景 `--accent-secondary-bg`,文字 `--accent-secondary-text`,左侧加版本号 pill。
- 数据来源:每个页面自己的 `changelog` 数组,取最新一条渲染。
- 右侧放一个“查看历史”展开/折叠按钮,展开后显示该页面全部版本条目(最多 5 条)。
- 公告条不占据页面主内容宽度,全站通栏,但内容是页面相关的。

### 4.3 首页 `Home`

#### Hero 区

- 背景 `--bg-hero`。
- 顶部放一个 pill 标签:最新全站版本号 + 一句话(如“v0.2 · 新增 Nexus 学习站与全站 UI 升级”)。
- 主标题:36-40px,字重 800,`--text-primary`。
- 副标题:18px,`--text-secondary`,最大宽度 640px,居中,行高 1.7。
- 两个 CTA 按钮:
  - 主按钮:深底白字,`--accent-primary` + `--accent-primary-text`,圆角 full。
  - 次按钮:白底 + 边框,hover 变浅灰。

#### 精选作品区

- 最大宽度 `--max-content`,水平内边距 `--space-8`。
- 标题行:左侧“精选作品”+ 右侧搜索框。
- 搜索框:实时过滤作品卡片(按标题/描述/tech 标签)。
- 网格:三列(`lg:grid-cols-3`),两列(`sm:grid-cols-2`),单列兜底。
- 作品卡片:
  - 白色背景、细边框、`--radius-xl`、轻微阴影。
  - 顶部左侧放一个**图标方块**:40×40,圆角 `--radius-md`,背景用该技术的主色 50/100 号色,文字是首字母。
  - 标题 16px 字重 700,描述 13px `--text-tertiary`。
  - 底部 tech tags:小 pill,每个 tag 用独立颜色。

### 4.4 Demo 页 `Demo`

- 使用统一布局 `SidebarLayout`:
  - 左侧边栏(240px):作品导航列表,当前项高亮。
  - 右侧主内容区:顶部当前 demo 信息卡(标题、描述、tech tags、源码链接) + iframe 容器。
- iframe 容器:
  - 圆角、阴影、1px 边框。
  - 初始状态显示骨架屏(标题行 + 内容区占位)。
  - 监听 `iframe.onload`,加载完成后淡出骨架屏,淡入 iframe 内容。
  - iframe 加载失败时显示错误提示 + 重试按钮。
- 右侧当前 demo 信息卡同时作为“面包屑/上下文”,让用户知道自己在哪里。

### 4.5 学习入口 `Learn`

- 当前行为是直接 `window.location.href = '/learn/'`,导致全页跳转,没有外壳感。
- 改为**iframe 嵌入** `/learn/`,复用 `Demo` 页结构:
  - 左侧边栏放学习站目录(从 `course.ts` 抽取模块/课时列表)。
  - 右侧 iframe 加载 `/learn/`。
- 这样学习站既能独立运行,也能被门户统一包装;后续若重写学习站为原生页面,直接替换 iframe 区域即可。

### 4.6 个人页 `Me`

- 使用统一布局 `SidebarLayout`,左侧放“关于我”的快捷导航(技能栈、简历、项目、版本历史),右侧放内容卡片。
- 内容分卡片:
  - 技能栈:标签云形式。
  - 简历:下载按钮 + 最近更新时间。
  - 项目:cs-quiz-app 链接(仍显示“待集成”,因为 Phase 3 还没做)。
  - 版本历史:折叠列表,展示整个 ai-demos 的版本迭代。

---

## 5. 组件清单

| 组件 | 路径 | 职责 |
|---|---|---|
| `NavBar` | `components/NavBar.tsx` | 全局导航 + Logo + 移动端菜单 |
| `PageChangelog` | `components/PageChangelog.tsx` | 页面级更新公告条 + 历史展开 |
| `SidebarLayout` | `components/SidebarLayout.tsx` | 左侧边栏 + 右侧主内容区通用布局 |
| `SidebarNav` | `components/SidebarNav.tsx` | 侧边栏导航列表(接收 items + activeKey) |
| `WorkCard` | `components/WorkCard.tsx` | 首页作品卡片 |
| `DemoFrame` | `components/DemoFrame.tsx` | iframe + 骨架屏 + 加载/错误状态 |
| `DemoInfoCard` | `components/DemoInfoCard.tsx` | 当前 demo 信息卡 |
| `IconBox` | `components/IconBox.tsx` | 40×40 图标方块(首字母 + 背景色) |
| `Tag` | `components/Tag.tsx` | 小 pill 标签,支持多种颜色 |
| `Button` | `components/Button.tsx` | 主/次按钮统一封装 |
| `PageTransition` | `components/PageTransition.tsx` | 路由切换淡入淡出包装器 |
| `useDocumentTitle` | `hooks/useDocumentTitle.ts` | 页面标题 + 失焦提醒 |
| `useChangelog` | `hooks/useChangelog.ts` | 读取页面 changelog 数据 |

---

## 6. 数据变更

### 6.1 `data/works.ts`

每个 `Work` 增加:

```ts
export interface Work {
  slug: string
  title: string
  desc: string
  tech: string[]
  github?: string
  path: string
  icon?: { letter: string; bg: string; text: string }  // 首页卡片图标
  changelog?: { version: string; date: string; items: string[] }[]
}
```

### 6.2 新增 `data/changelogs.ts`

集中存放各页面 changelog:

```ts
export const PAGE_CHANGELOGS: Record<string, ChangelogEntry[]> = {
  home: [
    { version: '0.2', date: '2026-06-24', items: ['新增 Hero 区与统一侧边栏', '增加页面级更新公告', 'iframe 加载骨架屏'] },
    { version: '0.1', date: '2026-06-22', items: ['作品网格首页上线'] },
  ],
  rag: [
    { version: '0.1', date: '2026-06-22', items: ['RAG 文档问答 Demo 上线'] },
  ],
  // ...
}
```

### 6.3 学习站目录抽取

- 新增 `data/learnNav.ts`,从 `nexus-learning-web/src/data/course.ts` 抽取模块/课时层级,用于 `Learn` 页左侧边栏。
- 不移动学习站源码,只复制一份精简目录数据到门户;未来学习站重写为原生时删除。

---

## 7. 交互与动效

### 7.1 路由切换过渡

- 使用 `react-router-dom` 的 `useLocation` + `AnimatePresence`(引入 `framer-motion` 或手写 CSS transition)。
- 为了**避免引入新依赖**,优先手写 CSS:
  - 页面容器初始 `opacity: 0; transform: translateY(8px)`。
  - 进入后 200ms 淡入 + 上移。
- 对于 iframe 内部独立页面切换(如学习站内),本轮不干预。

### 7.2 iframe 加载反馈

- 骨架屏:3-4 个 shimmer 占位条(使用纯 CSS 动画)。
- 加载成功:骨架屏 opacity 降为 0,iframe opacity 从 0 → 1。
- 加载超时(>8s):显示“加载较慢,请重试”+ 刷新按钮。
- 加载失败:显示错误提示 + 返回首页按钮。

### 7.3 标签页标题反馈

- 使用 `useDocumentTitle` hook:
  - 进入页面设置 `document.title = "RAG 文档问答 · 个人集成学习网站"`。
  - 监听 `visibilitychange`:当页面隐藏时 title 变为 `"👋 快回来继续探索 AI 作品!"`;重新可见时恢复。
- 不引入 emoji(避免终端渲染问题),用纯文本感叹号表达。

### 7.4 首页搜索

- 输入时实时过滤,无结果显示空态提示。
- 搜索词高亮(可选,本轮可做可不做,看实现余量)。

---

## 8. 响应式断点

沿用 Tailwind 默认断点:

- `sm` (640px): 首页网格两列,导航展开。
- `lg` (1024px): Demo/Learn/Me 页侧边栏水平展开;小于 lg 时侧边栏折叠到顶部或汉堡菜单内。
- 移动端侧边栏先不做抽屉,直接把它放到主内容上方(垂直堆叠),避免引入复杂交互。

---

## 9. 测试与验收

1. `bash deploy/build-frontends.sh` 成功,无 TypeScript 错误。
2. `docker compose -f deploy/docker-compose.yml up -d --build` 后,访问 http://127.0.0.1:8080:
   - 首页 Hero、作品卡片、搜索正常。
   - 点击每个作品进入 Demo 页,侧边栏导航正确高亮,iframe 加载有骨架屏。
   - `/learn/` 被 iframe 包装,左侧显示课程目录。
   - `/me` 有个人卡片和版本历史。
   - 切换浏览器标签页,title 会变化。
3. 移动端宽度(375px)下,导航折叠,页面不横向溢出。
4. 线上 `https://www.shiyuan-wreg.cloud/` 同样验证一遍。

---

## 10. 风险与回退

| 风险 | 缓解 |
|---|---|
| iframe 加载慢导致骨架屏常驻 | 设置 8s 超时提示 + 重试按钮 |
| 学习站 iframe 嵌入后与直接访问行为不一致 | 学习站本身独立可用,iframe 仅作为门户包装;目录边栏仅做导航展示 |
| 引入大量组件导致构建变慢 | 组件职责单一,避免大依赖;本轮不引入 framer-motion |
| 移动端侧边栏复杂 | 先垂直堆叠,不做抽屉 |

---

## 11. 后续轮次(明确不做)

- **主题切换器**: 导航栏加主题下拉,支持浅色/深蓝/赛博绿,持久化到 localStorage。
- **多主题扩展**: 把 `:root` 变量扩展为 `[data-theme="deepblue"]`, `[data-theme="cyber"]`。
- **iframe demo 内部换肤**: RAG/FC/Nexus/DocHub 的 HTML 模板也读取同一套 CSS 变量,实现跨框架视觉统一。
- **更复杂动效**: 卡片 hover 微动效、滚动渐入、数字计数器等。

---

## 12. 实现文件清单(第一轮)

### 新增
- `frontends/portfolio/src/styles/theme.css`
- `frontends/portfolio/src/components/PageChangelog.tsx`
- `frontends/portfolio/src/components/SidebarLayout.tsx`
- `frontends/portfolio/src/components/SidebarNav.tsx`
- `frontends/portfolio/src/components/WorkCard.tsx`
- `frontends/portfolio/src/components/DemoInfoCard.tsx`
- `frontends/portfolio/src/components/IconBox.tsx`
- `frontends/portfolio/src/components/Tag.tsx`
- `frontends/portfolio/src/components/Button.tsx`
- `frontends/portfolio/src/components/PageTransition.tsx`
- `frontends/portfolio/src/hooks/useDocumentTitle.ts`
- `frontends/portfolio/src/data/changelogs.ts`
- `frontends/portfolio/src/data/learnNav.ts`

### 修改
- `frontends/portfolio/src/styles.css` → 引入 theme.css
- `frontends/portfolio/tailwind.config.js` → 映射 CSS 变量
- `frontends/portfolio/src/data/works.ts` → 加 icon/changelog
- `frontends/portfolio/src/components/NavBar.tsx` → 新导航 + 移动端
- `frontends/portfolio/src/components/DemoFrame.tsx` → 骨架屏 + 动画
- `frontends/portfolio/src/pages/Home.tsx` → Hero + 搜索 + WorkCard
- `frontends/portfolio/src/pages/Demo.tsx` → SidebarLayout + DemoInfoCard
- `frontends/portfolio/src/pages/Learn.tsx` → iframe 包装 + 课程目录
- `frontends/portfolio/src/pages/Me.tsx` → SidebarLayout + 卡片化
- `frontends/portfolio/src/App.tsx` → 页面过渡包装

---

## 13. 备注

- 所有新增组件使用 TypeScript 函数组件,Props 显式定义类型。
- 不引入除 lucide-react 之外的图标库(建议把 nexus-learning-web 的 `lucide-react` 经验复用到 portfolio;若不想加依赖,可用纯字符/手写 SVG)。
- 保持现有路由不变,不改动 nginx/Docker 配置。
