# Nexus 交互式学习站点

> 项目位置：`C:\Users\hzs17\Desktop\ai-demos\nexus-learning-web`
> 项目定位：Nexus 项目的配套交互式学习平台
> 创建日期：2026-06-21

---

## 这是什么

这是一个基于 Web 的交互式学习站点，用于系统学习 **Nexus**（ai-demos 项目）相关知识：

- 大语言模型（LLM）原理与工程约束
- Agent 架构与 ReAct 范式
- RAG 检索增强生成
- Function Calling 与安全工具设计
- Multi-Agent 消息总线与协作机制
- Nexus Phase 1 ~ 4 架构
- 测试评估、工程化、简历面试

它和传统的 Word/Markdown 文档不同：每节课都有**目标 → 讲解 → 代码实验 → 即时测验 → 检查清单**的完整学习闭环。

---

## 技术栈

| 层级 | 技术 |
|---|---|
| 框架 | React 18 + Vite 5 |
| 语言 | TypeScript |
| 样式 | TailwindCSS 3 + @tailwindcss/typography |
| 图标 | lucide-react |
| 内容渲染 | react-markdown + remark-gfm + react-syntax-highlighter |
| 状态持久化 | localStorage（MVP 阶段） |

---

## 目录结构

```
nexus-learning-web/
├── index.html              # HTML 入口
├── package.json            # 依赖与脚本
├── vite.config.ts          # Vite 配置
├── tsconfig.json           # TypeScript 配置
├── tailwind.config.js      # Tailwind 配置
├── postcss.config.js       # PostCSS 配置
├── src/
│   ├── main.tsx            # React 应用入口
│   ├── App.tsx             # 主应用：布局 + 路由切换
│   ├── styles.css          # 全局样式 + Tailwind 指令
│   ├── vite-env.d.ts       # Vite 类型声明
│   ├── types/
│   │   └── course.ts       # 课程相关 TypeScript 类型
│   ├── data/
│   │   └── course.ts       # 课程数据（模块、课程、测验、代码实验）
│   ├── components/
│   │   ├── Sidebar.tsx     # 左侧课程目录
│   │   ├── LessonContent.tsx  # 课程内容渲染
│   │   ├── Quiz.tsx        # 即时测验组件
│   │   ├── CodeLab.tsx     # 代码实验室组件
│   │   └── ProgressBar.tsx # 顶部进度条
│   └── hooks/
│       └── useProgress.ts  # localStorage 进度管理
└── dist/                   # 构建产物（npm run build 生成）
```

---

## 快速开始

### 1. 安装依赖

```bash
cd C:\Users\hzs17\Desktop\ai-demos\nexus-learning-web
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

浏览器访问：http://localhost:5174

### 3. 构建生产版本

```bash
npm run build
```

构建产物在 `dist/` 目录。

### 4. 预览构建产物

```bash
npm run preview
```

---

## 如何添加新课程

所有课程内容都在 `src/data/course.ts` 中维护。

### 添加一节课

1. 打开 `src/data/course.ts`。
2. 在对应模块的 `lessons` 数组中新增一个 `Lesson` 对象。
3. 填写以下字段：
   - `id`：唯一标识，如 `'rag-evaluation'`
   - `moduleId` / `moduleTitle`：所属模块
   - `order`：课程在模块内的顺序
   - `title` / `description`：标题和简介
   - `objectives`：本节目标数组
   - `prerequisites`：前置知识数组
   - `keyConcepts`：关键概念标签数组
   - `content`：Markdown 格式的正文内容
   - `codeLabs`：代码实验室数组
   - `quizzes`：测验题目数组
   - `commonMistakes`：常见错误数组
   - `furtherReading`：进阶阅读数组
   - `checklist`：本节检查清单数组

### 添加测验题

```typescript
{
  id: 'q1-1',
  type: 'single',  // 'single' | 'multiple' | 'code'
  question: '题目内容',
  options: [
    { id: 'a', text: '选项 A' },
    { id: 'b', text: '选项 B' },
  ],
  correctAnswer: 'a',
  explanation: '答案解析'
}
```

### 添加代码实验

```typescript
{
  id: 'lab-1',
  title: '实验标题',
  description: '实验说明',
  starterCode: '初始代码',
  expectedOutput: '预期输出',
  hint: '提示信息（可选）'
}
```

---

## 与 cs-quiz-app 的关系

`cs-quiz-app` 是用户之前开发的 Web 端面试题库项目：

- 技术栈：React + Vite + TypeScript + TailwindCSS + Fastify + SQLite
- 模式：Markdown 题源 → 数据库存储 → REST API → 前端刷题

`nexus-learning-web` 复用了它的前端技术栈和"内容 → 交互 → 反馈"的学习模式，但当前阶段为纯前端 MVP：

- 课程数据直接写在 `course.ts` 中，不需要后端和数据库。
- 进度存在 `localStorage`，方便快速验证。

第二阶段可以接入 Fastify + SQLite，把课程数据、进度、错题本都持久化到后端。

---

## 与 ai-demos/Nexus 的关系

`nexus-learning-web` 是 `ai-demos` 项目的子项目：

- 学习内容对应 Nexus 的技术栈和实现阶段。
- 课程中的代码示例可以直接在 `ai-demos` 项目中找到对应实现。
- 学习完课程后，可以继续推进 `ai-demos` 的 Phase 2 / 3 / 4 开发。

---

## 当前阶段与路线图

### 第一阶段（已完成）

- 纯前端 MVP
- 8 节核心课程
- 即时测验 + 代码实验室
- localStorage 进度追踪

### 第二阶段（待实现）

- 接入 Fastify 后端
- SQLite 持久化学习进度
- 用户系统（JWT）
- 错题本页面
- 课程解锁机制

### 第三阶段（待实现）

- 代码在线运行沙箱
- 更多课程章节
- 学习数据分析
- Docker 部署

---

## 常见问题

### Q：为什么用 localStorage 而不是数据库？

A：MVP 阶段为了快速验证交互式学习模式。第二阶段会迁移到 SQLite + Fastify。

### Q：课程内容写在哪里？

A：`src/data/course.ts`。所有课程、测验、代码实验都在这里维护。

### Q：如何修改样式？

A：全局样式在 `src/styles.css`，Tailwind 配置在 `tailwind.config.js`。

### Q：想新增一个模块怎么办？

A：在 `src/data/course.ts` 的 `modules` 数组中新增一个 `Module` 对象，然后往里面添加课程。

---

## 维护者

- 胡智明（23 级软件工程本科）
- 项目归属：`C:\Users\hzs17\Desktop\ai-demos`
