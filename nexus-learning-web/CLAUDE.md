# CLAUDE.md — Nexus 交互式学习站点

> 这是给 Claude 读取的目录上下文。任何进入 `nexus-learning-web` 的 Claude 实例，请先阅读本文件。

---

## 项目定位

`nexus-learning-web` 是 `ai-demos` 项目的配套交互式学习站点，基于 React + Vite + TypeScript + TailwindCSS 构建。

它不是独立项目，而是服务于 Nexus（ai-demos）的学习内容：把原本静态的 Word/Markdown 课程文档，转换为有即时测验、代码实验、进度追踪的 Web 学习体验。

---

## 核心技术栈

- **React 18** + **Vite 5** + **TypeScript**
- **TailwindCSS 3** + **@tailwindcss/typography**
- **react-markdown** + **remark-gfm** + **react-syntax-highlighter**
- **lucide-react** 图标
- **localStorage** 进度持久化（MVP 阶段）

---

## 目录结构与文件职责

```
nexus-learning-web/
├── index.html              # HTML 入口
├── package.json            # 依赖与脚本
├── vite.config.ts          # Vite 配置，端口 5174
├── tsconfig.json           # TS 配置，路径别名 @/* → src/*
├── tailwind.config.js      # Tailwind 配置，包含 typography 插件
├── postcss.config.js       # PostCSS 配置
├── README.md               # 给用户看的项目说明
├── CLAUDE.md               # 本文件
├── src/
│   ├── main.tsx            # React 应用入口
│   ├── App.tsx             # 主应用：Sidebar + ProgressBar + LessonContent + 导航
│   ├── styles.css          # Tailwind 指令 + 自定义滚动条 + prose-custom
│   ├── vite-env.d.ts       # Vite 类型声明
│   ├── types/course.ts     # 课程类型定义（Module, Lesson, QuizQuestion, CodeLab, Progress）
│   ├── data/course.ts      # 课程数据源：4 模块 8 课 + 测验 + 代码实验 + 辅助函数
│   ├── components/
│   │   ├── Sidebar.tsx     # 左侧目录，显示模块和课程，高亮当前，标记完成
│   │   ├── LessonContent.tsx  # 课程内容渲染：目标、正文 Markdown、代码实验室、测验、常见错误等
│   │   ├── Quiz.tsx        # 即时测验：单选/多选/代码填空，提交后显示对错和解析
│   │   ├── CodeLab.tsx     # 代码实验室：可编辑代码、复制、跳转在线运行
│   │   └── ProgressBar.tsx # 顶部进度条，显示完成百分比和错题数量
│   └── hooks/
│       └── useProgress.ts  # localStorage 读写进度，提供 completeLesson / resetProgress 等方法
```

---

## 运行命令

```bash
# 开发
npm run dev          # http://localhost:5174

# 构建
npm run build        # 输出到 dist/

# 预览构建产物
npm run preview      # http://localhost:4173
```

---

## 课程内容数据模型

课程数据在 `src/data/course.ts` 中。数据结构：

```typescript
Module {
  id: string
  title: string
  description: string
  order: number
  lessons: Lesson[]
}

Lesson {
  id: string
  moduleId: string
  moduleTitle: string
  order: number
  title: string
  description: string
  objectives: string[]
  prerequisites: string[]
  keyConcepts: string[]
  content: string        // Markdown
  codeLabs: CodeLab[]
  quizzes: QuizQuestion[]
  commonMistakes: string[]
  furtherReading: { title: string; url?: string }[]
  checklist: string[]
}

QuizQuestion {
  id: string
  type: 'single' | 'multiple' | 'code'
  question: string
  options?: { id: string; text: string }[]
  correctAnswer: string | string[]
  explanation: string
  code?: string
}

CodeLab {
  id: string
  title: string
  description: string
  starterCode: string
  expectedOutput?: string
  hint?: string
}
```

---

## 关键组件说明

### App.tsx

- 维护当前课程 ID 状态。
- 调用 `useProgress()` 读写 localStorage。
- 渲染 `Sidebar` + `ProgressBar` + `LessonContent`。
- 提供上一节/下一节导航。

### Sidebar.tsx

- 接收 `modules`、`currentLessonId`、`completedLessons`。
- 每个模块显示完成数量。
- 每节课显示完成状态。

### LessonContent.tsx

- 渲染课程所有区块。
- 使用 `react-markdown` + `react-syntax-highlighter` 渲染 Markdown 和代码。
- 内嵌 `Quiz` 和 `CodeLab` 组件。

### Quiz.tsx

- 支持单选、多选、代码填空。
- 多选题要求选择完全正确才得分。
- 提交后显示解析，解析文字放在 `explanation` 字段。

### CodeLab.tsx

- 显示可编辑的代码文本框。
- 一键复制代码。
- 点击"在线运行"跳转外部 Python 编译器（当前未实现内建沙箱）。

### useProgress.ts

- localStorage key: `nexus-learning-progress`
- 提供：
  - `completeLesson(lessonId)`
  - `recordQuizResult(lessonId, correct, total)`
  - `addWrongQuestion(questionId)` / `removeWrongQuestion(questionId)`
  - `resetProgress()`

---

## 如何扩展

### 添加新课程

1. 在 `src/data/course.ts` 的对应模块 `lessons` 数组中新增 `Lesson` 对象。
2. 确保 `id` 唯一，`order` 连续。
3. 测验题 `correctAnswer` 与 `options` 的 `id` 对应。
4. 运行 `npm run dev` 验证。

### 添加新模块

1. 在 `src/data/course.ts` 的 `modules` 数组中新增 `Module` 对象。
2. 把课程放到该模块的 `lessons` 中。
3. `Sidebar` 会自动渲染。

### 接入后端（第二阶段）

参考 `C:\Users\hzs17\Desktop\cs-quiz-app` 的架构：

- 后端：Fastify 5 + Drizzle ORM + better-sqlite3
- API：/api/courses, /api/lessons, /api/progress
- 前端：用 TanStack Query 替换 localStorage，或用 localStorage 做缓存 + 后端同步

### 添加错题本页面

1. 在 `src/pages/` 新建 `WrongBook.tsx`。
2. 读取 `useProgress().progress.wrongQuestions`。
3. 根据 questionId 在 `course.ts` 中查找对应题目。
4. 在 `App.tsx` 中添加路由或页面切换。

---

## 与 cs-quiz-app 的关系

`cs-quiz-app` 是用户之前开发的 Web 端面试题库：

- 位置：`C:\Users\hzs17\Desktop\cs-quiz-app`
- 技术栈：React + Vite + TypeScript + TailwindCSS + Fastify + SQLite
- 模式：Markdown 题源 → 数据库存储 → REST API → 前端刷题

`nexus-learning-web` 是它的简化版/精神续作：

- 复用前端技术栈和交互学习模式。
- MVP 阶段纯前端，课程数据写死，进度存在 localStorage。
- 第二阶段可完全复用 `cs-quiz-app` 的后端架构。

---

## 与 ai-demos/Nexus 的关系

`nexus-learning-web` 是 `ai-demos` 的子项目：

- 学习内容对应 Nexus 的技术栈和 Phase 1 ~ 4。
- 课程代码示例可在 `ai-demos/core/`、`ai-demos/rag/` 中找到对应实现。
- 学习完课程后，用户应继续推进 `ai-demos` 的 Phase 2 / 3 / 4。

---

## 修改注意事项

1. **课程数据是核心**：大部分内容修改都在 `src/data/course.ts`。
2. **类型必须一致**：修改 `course.ts` 时确保与 `types/course.ts` 匹配。
3. **Markdown 转义**：`content` 中的代码块、表格、反斜杠需要正确转义。
4. **不要破坏 Quiz 逻辑**：`Quiz.tsx` 对 `correctAnswer` 的数组/字符串处理有特定逻辑。
5. **样式基于 Tailwind**：修改样式优先改 `styles.css` 或 Tailwind 类名。

---

## 常见修复场景

| 问题 | 可能原因 | 修复方式 |
|---|---|---|
| Build 报错 `prose class does not exist` | @tailwindcss/typography 未加载 | 检查 tailwind.config.js 插件配置 |
| TypeScript 报错找不到 Lesson | course.ts 未导入 Lesson 类型 | import type { Module, Lesson } from '../types/course' |
| 测验提交无反应 | correctAnswer 类型不匹配 | 检查单选用 string，多选用 string[] |
| 侧边栏不显示新课程 | moduleId 或 lessons 数组错误 | 检查 course.ts 数据结构 |
| 进度不保存 | localStorage 被禁用或 key 冲突 | 检查 STORAGE_KEY 和 loaded 状态 |

---

## 项目文件索引

| 文件 | 修改频率 | 用途 |
|---|---|---|
| `src/data/course.ts` | 高 | 课程内容 |
| `src/components/LessonContent.tsx` | 中 | 课程渲染 |
| `src/components/Quiz.tsx` | 中 | 测验交互 |
| `src/components/CodeLab.tsx` | 低 | 代码实验 |
| `src/hooks/useProgress.ts` | 低 | 进度管理 |
| `src/App.tsx` | 低 | 主布局 |
| `src/styles.css` | 低 | 全局样式 |
| `tailwind.config.js` | 低 | Tailwind 配置 |

---

## 开发优先级建议

如果用户没有明确说明，按以下优先级处理：

1. **课程内容补充**：把剩余章节（Phase 3 Web UI、Phase 4 记忆持久化等）做成交互课。
2. **错题本页面**：这是提升复习效率的高价值功能。
3. **后端持久化**：复用 cs-quiz-app 架构，把进度存到 SQLite。
4. **代码在线运行**：后端集成安全 Python 沙箱。

---

本文件由 Claude 于 2026-06-21 创建，后续维护时请同步更新。
