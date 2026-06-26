% 个人集成学习网站 · 前端代码逐层精讲(从零到换肤)
% ai-demos portfolio 前端
% 2026-06-26

---

## 写在最前面:这份文档怎么读

**你的处境**:你能跑通这个网站、能改后端逻辑,但对「前端这堆 `.tsx`、`.css`、`React`、`Vite` 到底是什么、怎么拼起来的」是模糊的。之前我默认你懂 React/Vite 就直接抛术语,等于让没学过算术的人直接看群论,这是我的错。

**这份文档的目标**:从「网页到底是什么」这一最底层讲起,一路爬到我们这次要做的「换肤(skin)」,中间每一步都对照**你本地真实的代码文件**。读完你应该能:

1. 说清楚浏览器、HTML、CSS、JavaScript 各自干什么;
2. 说清楚 React、TypeScript、Vite、Tailwind、npm 各自解决什么问题;
3. 在脑子里画出我们这个网站从「用户敲网址」到「屏幕出画面」的完整链路;
4. 打开 `frontends/portfolio/` 里任意一个文件,知道它在整体里是什么角色;
5. 彻底理解「换肤」是怎么实现的,以及为什么「单页试装(A1)」比「全局换肤(A2)」简单、为什么 A1 能无损升级成 A2。

**怎么用**:建议**左边开这份文档,右边开 VS Code**,讲到某个文件时你就把那个文件打开对着看。文档里引用的代码,都是从你本地原文件里摘的,行号也标了。

**阅读顺序**:第 1~2 章是纯零基础铺垫(网页三大件 + 工程化工具),已经懂的可以快速扫过;第 3 章开始是我们项目;第 5 章是本次换肤任务的核心;第 7 章把「A1 vs A2」彻底讲透。

---

# 第 1 章 · 网页到底是什么(纯零基础)

## 1.1 浏览器在做什么

你打开 Chrome,输入一个网址,回车,屏幕上出现一个花花绿绿的页面。这中间发生的事,本质上是**三步**:

1. **要文件**:浏览器按网址,去某台服务器上「要」一些文本文件。
2. **读文件**:服务器把文件发回来。这些文件是纯文本,里面用特定语法描述了「这个页面长什么样、有什么内容、能干什么」。
3. **画出来**:浏览器读懂这些文本,在屏幕上把它画成你看到的样子。

**关键认知**:浏览器收到的,**全是纯文本**。再复杂的网页,扒到最底层,都是浏览器能读懂的几种文本文件。其中最核心的三种,就是下面说的「三大件」。

## 1.2 三大件:HTML / CSS / JavaScript

这三个常被比喻成盖房子:

| 角色 | 比喻 | 管什么 | 举例 |
|---|---|---|---|
| **HTML** | 房子的**毛坯结构** | 内容和骨架:这里有个标题、那里有段文字、下面有个按钮 | 「页面上有一个写着‘登录’的按钮」 |
| **CSS** | 房子的**装修** | 样子:颜色、大小、位置、字体、间距 | 「那个按钮是蓝色的、圆角、居中」 |
| **JavaScript** | 房子的**水电和机关** | 行为:点击后发生什么、数据怎么变 | 「点登录按钮后,弹出输入框」 |

**只用 HTML**:能出内容,但丑(默认黑字白底)、死(点了没反应)。
**加上 CSS**:变好看了,但还是死的。
**再加 JavaScript**:活了,能交互、能变化。

这三件是浏览器**原生就懂**的。后面要讲的 React、Vue、Tailwind 等等,**没有一个是浏览器原生懂的**——它们最终都要被「翻译」回这三件,浏览器才认。记住这句话,后面很多困惑会自动解开。

## 1.3 一个能跑的最小网页

把下面这段存成 `test.html`,双击就能用浏览器打开:

```html
<!doctype html>
<html>
  <head>
    <title>我的第一个网页</title>
    <style>
      /* 这里是 CSS:装修 */
      #hello { color: red; font-size: 30px; }
    </style>
  </head>
  <body>
    <!-- 这里是 HTML:结构和内容 -->
    <h1 id="hello">你好</h1>
    <button onclick="change()">点我</button>

    <script>
      // 这里是 JavaScript:行为
      function change() {
        document.getElementById('hello').innerText = '被点过了';
      }
    </script>
  </body>
</html>
```

逐块看:

- `<h1 id="hello">你好</h1>`:HTML。一个一级标题,内容是「你好」,给它起了个名字(id)叫 `hello`,方便后面找到它。
- `#hello { color: red; }`:CSS。「名字叫 hello 的那个元素,字设成红色、30 像素大」。`#` 表示按 id 找。
- `function change(){...}`:JavaScript。定义了一个动作:找到名叫 hello 的元素,把它的文字换成「被点过了」。
- `<button onclick="change()">`:HTML 的按钮,`onclick="change()"` 表示「被点击时,执行那个 change 动作」。

这就是一个完整网页的全部要素。**我们整个 ai-demos 前端,本质上就是把这三件,用更先进的工具、按更大的规模组织起来。**

## 1.4 DOM:浏览器眼里的网页

浏览器读 HTML 时,会在内存里把它变成一棵**树**。比如上面那段,树大概是:

```
html
└── body
    ├── h1 (id=hello, 文字="你好")
    └── button (文字="点我")
```

这棵树叫 **DOM**(Document Object Model,文档对象模型)。

为什么要知道它?因为**JavaScript 改网页,本质就是改这棵 DOM 树**。上面 `document.getElementById('hello')` 就是「在 DOM 树里找到那个 h1 节点」,`.innerText = '...'` 就是「改它的文字」。一改,浏览器立刻重画。

后面讲 React 时你会看到 `document.getElementById('root')`——一模一样的动作,只是 React 把后续的「改 DOM」这件苦活全接管了。

---

# 第 2 章 · 从"手写网页"到"工程化"(为什么需要 React/Vite/TS)

第 1 章那种手写单文件,做个人小页面够了。但做我们这种「6 个 demo + 首页 + 个人页 + 公告页 + 学习站 + 换肤」的站,手写会死。这一章讲:**痛点是什么,每个工具来解决哪个痛点。**

## 2.1 手写的三个致命痛点

1. **重复**:每个页面顶部都有同一个导航栏。手写就要把导航栏的 HTML 在每个页面**复制一遍**。改一个字,要改十处。
2. **手动改 DOM 太累**:稍微复杂点的交互(比如「加载中显示骨架屏,加载完显示内容」),用原生 JS 手动 `getElementById`、`innerText`、增删节点,代码会长到无法维护。
3. **没有类型检查**:JavaScript 里写错变量名、传错参数,浏览器不会提前告诉你,只会在用户点的时候才崩。

下面的工具,就是逐个解决这些痛点的。

## 2.2 React:把界面拆成"可复用的积木"(组件)

**React 是一个 JavaScript 库**,解决痛点 1 和 2。它的核心思想一句话:**把界面拆成一个个可复用的「组件(Component)」**。

- 一个**组件**,就是「一段 HTML 结构 + 它相关的样式和行为」打包成的一个积木,可以起个名字反复用。
- 比如「导航栏」是一个组件 `NavBar`。你写一次,在每个页面只要写一句 `<NavBar />` 就把它放进去了。改导航栏只改 `NavBar` 一个文件,所有页面同步更新。痛点 1 解决。

React 里写界面用一种叫 **JSX** 的语法——**看起来像 HTML,但其实写在 JavaScript 文件里**。例如我们项目里(`src/components/AnnouncementBoard.tsx` 简化版):

```jsx
function AnnouncementBoard() {
  return (
    <section>
      <span>更新公告</span>
      <span>v0.4.1</span>
    </section>
  )
}
```

这个 `AnnouncementBoard` 就是一个组件(在 React 里组件就是一个**返回 JSX 的函数**)。`return (...)` 里那坨长得像 HTML 的东西就是 JSX。

**关于「手动改 DOM」(痛点 2)**:React 的杀手锏是——你**不再手动改 DOM**。你只管描述「数据是什么样,界面就该是什么样」,数据一变,React 自己去算「DOM 树哪里要改」,然后高效地改。你从「指挥工人一块砖一块砖砌」变成「画好图纸,React 当包工头」。后面 `DemoFrame.tsx` 的「加载中/加载完」就是这个机制的实例。

> 顺带:你听过的 **Vue** 和 React 是**同类竞品**(都是做组件化界面的)。我们项目用的是 **React**,不是 Vue。两者思想相通,学会一个另一个很快。

## 2.3 TypeScript:带"类型"的 JavaScript

**TypeScript(简称 TS)= JavaScript + 类型标注**,解决痛点 3。

原生 JavaScript 里,一个变量可以一会儿是数字一会儿是文字,函数参数传错也不报错。TypeScript 让你给变量、参数标上「类型」,**在你写代码、还没运行的时候**就检查错误。

例子(我们 `src/data/changelogs.ts` 里真实的写法):

```ts
export interface ChangelogEntry {
  version: string   // version 必须是字符串
  date: string
  items: string[]   // items 必须是「字符串的数组」
}
```

这段 `interface`(接口)就是一份「类型说明书」:凡是声明为 `ChangelogEntry` 的东西,必须有 `version`、`date`、`items` 三个字段,且类型固定。如果你哪天写漏了 `date`,或把 `items` 写成了数字,编辑器会**立刻标红**,根本轮不到上线出 bug。

**文件后缀**:`.ts` 是纯 TypeScript;`.tsx` 是「TypeScript + JSX」,也就是**用 TS 写的 React 组件**文件。我们前端绝大多数文件是 `.tsx`。

**重要**:浏览器**不懂** TypeScript。TS 必须先被「编译」回普通 JavaScript,浏览器才能跑。谁来编译?下面的 Vite。

## 2.4 Vite:开发服务器 + 打包工具

**Vite(读「vee-t」,法语「快」)** 是个「构建工具」,解决一堆工程化杂活:

1. **翻译**:把浏览器不认识的 `.tsx`(TypeScript + JSX)实时翻译成浏览器认识的 JavaScript。
2. **开发服务器**:你敲 `npm run dev`,Vite 起一个本地服务器(比如 `localhost:3000`),你改一行代码,网页**自动刷新**,所见即所得。上次 The Machine 那个项目,你看到的 `[vite] connected`、`page reload` 就是它。
3. **打包(build)**:上线前敲 `npm run build`,Vite 把你几十个源文件压缩、合并成几个体积最小的最终文件(放进 `dist/` 文件夹),这才是真正部署到服务器的东西。我们部署时跑的 `deploy/build-frontends.sh` 内部就是 `npm run build`。

一句话:**Vite 是把「人写的源代码」变成「浏览器能跑的成品」的那台机器,顺带在开发时提供热刷新。**

## 2.5 npm、package.json、node_modules

写现代前端不可能什么都自己造。React、Vite 这些都是别人写好的「包(package)」,你**下载来用**。

- **npm**(Node Package Manager):包的「应用商店 + 下载器」。`npm install` 就是「把这个项目需要的所有包下载下来」。
- **package.json**:项目的「身份证 + 购物清单」。里面记着项目名、需要哪些包(`dependencies`)、以及可执行的命令(`scripts`,比如 `dev`、`build`)。
- **node_modules**:`npm install` 把下载的包全堆在这个文件夹里。它通常几百兆、上万个文件,所以**不进 git**(用 `.gitignore` 排除),换台机器重新 `npm install` 生成即可。

看我们 `frontends/portfolio/package.json` 的片段就懂了:

```json
{
  "scripts": {
    "dev": "vite",          // npm run dev → 启动开发服务器
    "build": "vite build"   // npm run build → 打包成品
  },
  "dependencies": {
    "react": "...",
    "react-router-dom": "...",   // 路由(下面讲)
    "react-dom": "..."
  }
}
```

## 2.6 SPA:单页应用

最后一个关键概念。我们的门户是一个 **SPA(Single Page Application,单页应用)**。

**传统多页网站**:每个页面是一个独立的 `.html` 文件。点链接 = 浏览器整页跳转、重新加载,白屏一下。

**SPA**:**整个站只有一个 `.html` 文件**,里面几乎是空的。所有页面内容由 JavaScript(React)在浏览器里**动态画出来**。点导航时,URL 变了,但浏览器**不重新加载页面**,而是 React 把当前内容「换掉」,所以切换很顺滑、不白屏。

「URL 变了,该显示哪个页面」这件事,由一个叫**路由(Router)**的东西管。我们用的是 `react-router-dom`。第 4 章会看到它的真身。

---

# 第 3 章 · 我们网站的宏观架构

铺垫完工具,现在看我们这盘棋的全局。

## 3.1 一张图:外壳 + 多个后端 + nginx

我们的站不是一个程序,是**好几个独立程序被拼到同一个网址下**:

```
                   用户浏览器
                       │
                       ▼
        ┌──────────  nginx(交通警察/反向代理)──────────┐
        │  看网址前缀,决定把请求转给谁                    │
        └───┬───────────┬────────────┬──────────┬────────┘
            │           │            │          │
        "/" 开头    "/nexus/" 开头  "/rag/"    "/fc/" ...
            │           │            │          │
            ▼           ▼            ▼          ▼
     ┌───────────┐  ┌─────────┐  ┌────────┐  ┌────────┐
     │ portfolio │  │nexus_app│  │rag_app │  │ fc_app │
     │(React外壳)│  │(Python) │  │(Python)│  │(Python)│
     │ 静态文件   │  │ 后端服务 │  │ 后端   │  │ 后端    │
     └───────────┘  └─────────┘  └────────┘  └────────┘
```

- **portfolio(门户外壳)**:就是我们这几天在讲的 React 前端。负责首页、个人页、公告页,以及每个 demo 的「外框」。它打包后是一堆**静态文件**(html/js/css),由 nginx 直接发给浏览器。
- **各 demo 后端**(nexus_app、rag_app...):每个是一个**独立的 Python 程序**,自己渲染自己的界面、自己处理 AI 逻辑。
- **nginx**:站在最前面的「交通警察」(术语叫**反向代理**)。它看用户请求的网址前缀:`/nexus/` 开头的转给 nexus_app,`/` 转给门户静态文件。**对用户来说是一个网站,背后其实是好几个程序。**

## 3.2 目录结构导览

打开 `ai-demos/`,顶层三个关键文件夹:

```
ai-demos/
├── frontends/          前端们
│   ├── portfolio/          ← 门户外壳(本文主角,React)
│   └── nexus-learning-web/ ← 学习站(也是个 React 应用)
├── backends/           后端们(各 demo 的 Python 服务)
│   ├── rag_app/
│   ├── fc_app/
│   ├── nexus_app/
│   └── ...
└── deploy/             部署配置(nginx 配置、docker 编排)
```

再钻进本文主角 `frontends/portfolio/`:

```
portfolio/
├── index.html          ← 那个"几乎空"的单页外壳
├── package.json        ← 购物清单 + 命令
├── tailwind.config.js  ← Tailwind 配置(换肤的关键一环,第5章)
├── vite.config.ts      ← Vite 配置
└── src/                ← 我们写的源代码全在这
    ├── main.tsx            ← 入口:启动 React、初始化主题
    ├── App.tsx             ← 路由表:URL → 哪个页面
    ├── styles.css          ← 样式总入口
    ├── pages/              ← 各"页面"组件
    │   ├── Home.tsx            首页
    │   ├── Demo.tsx            demo 页外壳(本次换肤目标)
    │   ├── Me.tsx / Changelog.tsx ...
    ├── components/         ← 可复用小组件
    │   ├── NavBar.tsx          顶部导航
    │   ├── DemoFrame.tsx       包 iframe 的框
    │   └── ...
    ├── data/               ← 纯数据(不是界面)
    │   ├── works.ts           6 个作品的信息
    │   └── changelogs.ts      更新公告数据
    ├── hooks/              ← 可复用逻辑
    │   └── useTheme.ts         换肤逻辑
    └── styles/
        ├── theme.css          ← 各主题的颜色定义(换肤核心)
        └── texture.css        ← 网格/噪点质感
```

**这个目录结构本身就是知识**:`pages/` 放整页、`components/` 放复用积木、`data/` 放纯数据、`hooks/` 放复用逻辑、`styles/` 放样式。各司其职,这是 React 项目的通用组织法。

## 3.3 端到端:访问 `/nexus` 那一刻发生了什么

把前面的知识串起来,走一遍完整流程(本地开发模式):

1. 你在地址栏敲 `localhost:8080/nexus`,回车。
2. 请求先到 **nginx**。nginx 一看不是 `/nexus/`(注意没有结尾那个用于 iframe 的斜杠)而是门户路由,把门户的 `index.html` + 打包好的 JS 发回浏览器。
3. 浏览器加载 `index.html`,执行里面的 `main.tsx`(打包后的版本)。**React 启动。**
4. React 里的**路由**看当前 URL 是 `/nexus`,according 路由表决定:渲染 `Demo` 这个页面组件,并告诉它「你要展示的 demo 是 nexus,iframe 地址是 `/nexus/`」。
5. `Demo` 组件画出:左边侧边栏(导航 + 说明卡)+ 右边一个 `DemoFrame`。
6. `DemoFrame` 内部有个 `<iframe src="/nexus/">`。浏览器**为这个 iframe 单独再发一次请求**,这次是 `/nexus/`(带斜杠)。
7. 这个 `/nexus/` 请求又到 nginx,这回 nginx 转给 **nexus_app 那个 Python 程序**,它返回自己的界面 HTML,显示在 iframe 框里。

**第 6、7 步是理解换肤的关键**:门户(第 3~5 步)和 nexus 界面(第 6~7 步)是**两次独立请求、两个独立文档**,只是视觉上一个套在另一个里。这就是为什么「门户的皮穿不进 iframe」——它们根本是两家。

---

# 第 4 章 · 门户前端代码逐文件精读

现在真刀真枪读代码。建议每读一节就打开对应文件对照。

## 4.1 `index.html` —— 那个空壳

打开 `frontends/portfolio/index.html`,全文就 12 行:

```html
<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <title>个人集成学习网站</title>
  </head>
  <body>
    <div id="root"></div>                          <!-- ① 空容器 -->
    <script type="module" src="/src/main.tsx"></script>  <!-- ② 入口脚本 -->
  </body>
</html>
```

- **① `<div id="root"></div>`**:一个**空 div**,起名 `root`。整个 React 应用都会被画进这一个 div 里。现在它是空的,React 启动后才填满。
- **② `<script ... src="/src/main.tsx">`**:加载入口脚本 `main.tsx`。**这一行至关重要**——还记得上次 The Machine 黑屏吗?就是因为它的 index.html **漏了这一行**,React 入口从没被加载,`#root` 永远空着 = 黑屏。我给它补上这行就好了。

**对照**:SPA「整站只有一个几乎空的 html」这句话,这 12 行就是实证。

## 4.2 `main.tsx` —— 入口:启动 React + 初始化主题

打开 `src/main.tsx`。去掉字体 import 后核心是这样:

```tsx
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import './styles.css'
import { ALL_THEMES, type Theme } from './hooks/useTheme'

// ① 启动时,先决定用哪个主题
const stored = window.localStorage.getItem('ai-demos-theme')  // 读上次记住的
if (stored && ALL_THEMES.includes(stored)) {
  document.documentElement.setAttribute('data-theme', stored)        // 用记住的
} else {
  document.documentElement.setAttribute('data-theme', 'mono-light')  // 否则用默认
}

// ② 把 App 画进 #root
ReactDOM.createRoot(document.getElementById('root')!).render(
  <BrowserRouter>
    <App />
  </BrowserRouter>
)
```

逐块:

- **`import './styles.css'`**:把样式总入口引进来,所有 CSS 从这里生效。
- **① 主题初始化**:`localStorage` 是浏览器给每个网站的「小记事本」,能存一点数据、刷新不丢。这里读出上次用户选的主题名(存在 `ai-demos-theme` 这个键下),把它写成 `<html data-theme="...">`。**这一句是整个换肤机制的开关**,第 5 章详解。`document.documentElement` 就是 `<html>` 那个根节点。
- **② `ReactDOM.createRoot(...root...).render(<App/>)`**:找到那个空的 `#root`,把 `<App/>`(整个应用)画进去。还记得 1.4 节 `document.getElementById('root')` 吗?React 启动的本质就是「接管这个 root 节点,从此这块 DOM 归我管」。
- **`<BrowserRouter>`**:把整个 App 包在「路由器」里,这样 App 内部才能用「按 URL 切页面」的能力。

## 4.3 `App.tsx` —— 路由表:URL → 页面

打开 `src/App.tsx`。这是「哪个网址显示哪个页面」的总调度:

```tsx
export default function App() {
  return (
    <div className="min-h-screen bg-base">
      <NavBar />                          {/* ① 顶部导航,每页都有 */}
      <Routes>                            {/* ② 路由表开始 */}
        <Route path="/"        element={<Home />} />
        <Route path="/nexus"   element={<DemoRoute slug="nexus" src="/nexus/" />} />
        <Route path="/rag"     element={<DemoRoute slug="rag"   src="/rag/" />} />
        <Route path="/me"      element={<Me />} />
        <Route path="/changelog" element={<Changelog />} />
        {/* ...其余略... */}
      </Routes>
    </div>
  )
}
```

- **① `<NavBar />`**:导航栏组件,写在 `<Routes>` **外面**,所以它**不随页面切换而消失**——无论你在哪一页,顶部导航都在。这正是第 2.2 节「组件复用」解决痛点 1 的实例:导航只定义一次。
- **② `<Routes>` + `<Route>`**:路由表。每条 `<Route>` 说「当 URL 是 path 时,显示 element 这个组件」。
  - `/` → `<Home/>`(首页)
  - `/nexus` → `<DemoRoute slug="nexus" src="/nexus/"/>`(demo 页,并告诉它「这是 nexus,iframe 指向 /nexus/」)
  - `/me` → `<Me/>`(个人页)
- 注意 6 个 demo 都用同一个 `Demo` 组件,只是传进去的 `slug` 和 `src` 不同。**「Demo 外壳是所有 demo 共用的同一个组件」——这句话的证据就在这里。** 这也是为什么换肤要「只挂 nexus」需要按条件判断(第 7 章)。

`slug`、`src` 这种「父组件传给子组件的参数」,在 React 里叫 **props**(properties)。可以理解成「调用积木时塞给它的配置」。

## 4.4 `pages/Demo.tsx` —— demo 页外壳(本次换肤目标)

打开 `src/pages/Demo.tsx`。这是 A1 要套皮的那一页:

```tsx
export default function Demo({ slug, src }: { slug: string; src: string }) {
  const work = WORKS.find((w) => w.slug === slug)!   // ① 按 slug 找到这个作品的信息

  return (
    <div className="h-[calc(100vh-3.5rem)] flex flex-col">
      <SidebarLayout                                  {/* ② 左右分栏布局 */}
        sidebar={                                     {/* 左:侧边栏 */}
          <div>
            <SidebarNav items={navItems} activeKey={slug} />  {/* 作品导航 */}
            <DemoInfoCard work={work} />                       {/* 技术说明卡 */}
          </div>
        }
      >
        <DemoFrame src={src} title={work.title} index={work.index} /> {/* 右:iframe 框 */}
      </SidebarLayout>
    </div>
  )
}
```

- **① `WORKS.find(...)`**:`WORKS` 是 `data/works.ts` 里那个「6 个作品信息」的数组(就是上次我们删 changelog 死字段的那个文件)。这里按 `slug` 把当前作品捞出来。**数据与界面分离**:作品信息存在 `data/`,界面只管展示——这是好架构的体现。
- **② 组件树**:`Demo` 把页面拆成「`SidebarLayout`(布局)= 左 `SidebarNav`+`DemoInfoCard` + 右 `DemoFrame`」。这棵小树,就是我上次给你画的那张图的代码版。

**`className="..."` 是什么?** 这一串(`h-[calc(...)] flex flex-col`)是 **Tailwind 的样式类**,第 5.3 节讲。现在你只需知道:**这些 class 决定了这页长什么样,换肤改的就是它们最终取到的颜色。**

## 4.5 `components/DemoFrame.tsx` —— iframe 与"加载中"机制

打开 `src/components/DemoFrame.tsx`。它干两件事:① 放那个嵌入 demo 的 iframe;② 处理「加载中→加载完/失败」的显示。借它把两个重要概念讲清楚。

**(a) iframe 与文档隔离**

文件底部:

```tsx
<iframe
  title={title}
  src={src}                         // 比如 "/nexus/"
  onLoad={handleLoad}               // 加载成功时调用
  onError={handleError}             // 加载失败时调用
  className="w-full h-full border-0"
/>
```

`<iframe>` 是 HTML 原生标签,意思是「在当前网页里,嵌入**另一个完整网页**」。`src="/nexus/"` 就是被嵌入的那个网页地址。

**为什么门户的皮穿不进去?** 浏览器有条铁律叫「同源策略 / 文档隔离」:iframe 里是一个**独立文档**,有自己的 HTML、自己的 CSS、自己的 DOM 树。外层门户的 CSS 变量、`data-theme`,**作用范围到 iframe 边界为止,进不去**。这不是我们没做,是浏览器安全机制**故意**不让跨文档样式渗透。所以:
- **A(外壳换肤)**:改的是 iframe **外面**这个框,门户自己的代码,能做。
- **B(demo 自身换肤)**:要改 iframe **里面**那个 nexus_app 的界面,得去改 nexus_app 自己的代码——另一家。

**(b) 状态(state):React 怎么管"加载中"**

文件开头:

```tsx
const [status, setStatus] = useState<'loading' | 'loaded' | 'error'>('loading')
```

这行引入 React 最核心的概念 **state(状态)**。`status` 是一个变量,初始值 `'loading'`。特别之处:**当你用 `setStatus(...)` 改它时,React 会自动重画用到它的界面。**

看它怎么用(中部简化):

```tsx
{status === 'loading' && ( <骨架屏 /> )}   // status 是 loading 时,显示灰色占位骨架
{status === 'error'   && ( <错误提示 /> )}  // status 是 error 时,显示"加载失败"
```

流程:一开始 `status='loading'`,显示骨架屏 → iframe 加载好了,`onLoad` 触发 `handleLoad`,里面 `setStatus('loaded')` → React 发现 status 变了,自动重画,骨架屏消失、demo 显出来。

**这就是第 2.2 节说的「你不手动改 DOM」**:你没写一句「删除骨架屏节点、插入 iframe」,你只是改了 `status` 这个数据,React 自动算出 DOM 该怎么变。**数据驱动界面**,这是 React 的灵魂。

> 小结术语:**组件**=返回 JSX 的函数;**props**=父传子的参数(只读);**state**=组件自己的、会变的数据(一变就重画);**hook**=以 `use` 开头的特殊函数(如 `useState`、`useEffect`、我们自己的 `useTheme`),给函数组件加上「状态」「副作用」等能力。

---

# 第 5 章 · 样式与换肤系统(本次任务的核心)

这一章是重点中的重点。读完你会彻底懂「换肤」在代码上是怎么回事。

## 5.1 先补 CSS 三个基础概念

**(a) 选择器**:CSS 怎么「指定改谁」。

```css
#hello   { ... }   /* 选 id="hello" 的元素 */
.card    { ... }   /* 选 class="card" 的所有元素(. 表示 class) */
button   { ... }   /* 选所有 <button> */
[data-theme="cyber"] .card { ... }  /* 选:在 data-theme=cyber 的祖先内部的 .card */
```

最后一行很重要,换肤就靠这种「**带条件的选择器**」。

**(b) 层叠(Cascade)**:同一个元素被多条规则命中时,谁说了算?大致规则是「越具体的、越靠后的优先」。CSS 全名 Cascading Style Sheets,「层叠样式表」,层叠就是这个意思。

**(c) 继承**:有些样式(如文字颜色)会自动从父元素「传染」给子元素,除非子元素自己覆盖。这条在第 7 章讲「样式会不会漏出盒子」时要用到。

## 5.2 CSS 变量(自定义属性):换肤的物理基础

普通 CSS 是写死的:`color: red;`。**CSS 变量**让你给颜色起个名字、集中定义、到处引用:

```css
:root {
  --main-color: red;     /* 定义一个变量,名字 --main-color,值 red */
}
.title {
  color: var(--main-color);   /* 引用它 */
}
```

好处:几百处都写 `var(--main-color)`,将来想从红改蓝,**只改定义那一行**,全站同步变。

**换肤的全部秘密就是这一句话**:界面所有颜色都不写死,而是引用变量;不同主题 = 给同一批变量赋不同的值。切主题 = 换一整套变量值。

## 5.3 Tailwind:用"原子类"写样式

我们没有手写一大堆 CSS 文件,而是用 **Tailwind**。它提供海量「**原子类**」——每个 class 只干一件小事:

- `flex` = `display:flex`
- `flex-col` = 纵向排列
- `bg-base` = 背景色用 `--bg-base` 变量
- `text-primary` = 文字色用 `--text-primary` 变量
- `h-full` = 高度 100%

你在 JSX 里直接写 `className="flex flex-col bg-base text-primary"`,等于把这几条样式贴上去。好处是不用在 CSS 和组件间来回跳,样式就在结构旁边。第 4 章那些 `className` 你现在能读懂了:它们是一串原子类的组合。

## 5.4 换肤的完整链条(把上面全串起来)

我们的换肤,是这 4 个文件协作的一条链。**这是本文档最该记住的一张图**:

```
①  tailwind.config.js   ——  把 Tailwind 类名 接到 CSS 变量
        bg-base   → var(--bg-base)
        text-primary → var(--text-primary)
                         │
②  styles/theme.css     ——  给变量按"主题"赋不同的值
        [data-theme="mono-light"] { --bg-base:#fafafa; --text-primary:#09090b; }
        [data-theme="cyber"]      { --bg-base:#050507; --text-primary:#e4e4e7; }
                         │
③  <html data-theme="X"> ——  开关:决定此刻用哪一套
                         │
④  useTheme.ts / main.tsx —— 谁来拨这个开关 + 记住选择
```

走一遍:你在界面写了 `<div className="bg-base">`。
1. Tailwind 配置(①)把 `bg-base` 翻译成 `background: var(--bg-base)`。
2. `--bg-base` 的**具体值**,取决于此刻 `<html>` 上的 `data-theme`(③)是什么。
3. 是 `mono-light` 就取 `#fafafa`(纸白),是 `cyber` 就取 `#050507`(近黑)——值在 `theme.css`(②)里按主题分别定义。
4. 用户点切换器选了别的主题,`useTheme`(④)就改 `<html>` 的 `data-theme`,于是所有 `var(...)` 同时改值,**全站一瞬间换皮**,并把选择存进 localStorage 记住。

下面逐个看这 4 个文件的真身。

## 5.5 四个文件逐个看

**① `tailwind.config.js`(类名 → 变量)**

```js
export default {
  theme: { extend: { colors: {
    base:    'var(--bg-base)',        // 类名 bg-base / text-base 等用这个变量
    surface: { DEFAULT: 'var(--surface-default)', ... },
    primary: 'var(--text-primary)',   // 类名 text-primary 用这个
    border:  { DEFAULT: 'var(--border-default)', ... },
    accent:  { DEFAULT: 'var(--accent-primary)', ... },
  }}}
}
```

这就是「桥」:它告诉 Tailwind,「`base` 这个颜色名,实际值去读 `--bg-base` 变量」。**注意:这里没有任何具体颜色,全是变量名。** 具体颜色在下一个文件。

**② `styles/theme.css`(变量 × 主题)**

```css
/* 纸白主题 */
[data-theme="mono-light"] {
  --bg-base: #fafafa;
  --text-primary: #09090b;
  --accent-primary: #09090b;
  /* ...几十个变量... */
}

/* 赛博主题(已存在,跟 The Machine 同家族) */
[data-theme="cyber"] {
  --bg-base: #050507;
  --text-primary: #e4e4e7;
  --accent-primary: #a3e635;   /* 荧光绿 */
}
```

**看懂这个,你就懂了换肤的 90%**:每个 `[data-theme="X"] { ... }` 块,就是一整套皮的「配色表」。同名变量、不同值。我们这次做 The Machine,本质就是**再加一个这样的块**(把黄 `#FFD700`、黑 `#020202`、红 `#FF4500` 填进这些变量)。

**③ 开关:`<html data-theme="...">`**

由 `main.tsx`(启动时,见 4.2)和 `useTheme.ts`(运行中切换)负责写。

**④ `hooks/useTheme.ts`(切换 + 记忆)**

```ts
export const ALL_THEMES = ['mono-light', 'light', 'deepblue', 'cyber']  // ← 注册表

export function useTheme() {
  const [theme, setThemeState] = useState(getInitialTheme)
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)  // 改开关
    window.localStorage.setItem('ai-demos-theme', theme)        // 记住
  }, [theme])
  return { theme, setTheme: setThemeState }
}
```

- `ALL_THEMES` 是「**已注册主题列表**」。切换器(`ThemeToggle.tsx`)就是遍历它生成按钮。**将来把 The Machine 升级成全局主题(A2),关键一步就是把 `'machine'` 加进这个数组。**
- `useEffect`:又一个核心 hook,意思是「当 `theme` 变化时,执行括号里的副作用」。这里就是「改 `<html>` 的 data-theme + 存 localStorage」。
- 返回 `{ theme, setTheme }`:别的组件拿到 `setTheme`,用户点哪个主题就 `setTheme('cyber')`,链条就转起来了。

## 5.6 回到 iframe:为什么皮穿不进去(再确认)

现在你有了完整模型,可以精确地理解了:换肤的全部作用方式,是改 `<html data-theme>` 让 `var(--xxx)` 取不同值。但**这套 `<html>` 和这些变量,只属于门户这个文档**。iframe 里的 nexus_app 是另一个文档,有它**自己的 `<html>`、自己的 CSS**,根本不读门户的变量。所以无论门户怎么换肤,iframe 内部纹丝不动。**这是 A 和 B 必须分两层做的根本原因,到此完全闭环。**

---

# 第 6 章 · HUD 与 The Machine 风格,落到技术点

## 6.1 HUD 是什么(再说一遍,这次配技术)

**HUD = Heads-Up Display,平视显示器**。源自战斗机:把数据投到飞行员正前方玻璃上,平视即见。游戏借用它指「叠在主画面之上的信息装饰层」——准星、血条、边框、扫描线。

「给 demo 套 HUD 皮」= 给朴素界面,**罩上一层监控终端质感的装饰**(深色底 + 荧光描边 + 角框 + 扫描线 + 数据流)。

## 6.2 The Machine 那些效果,分别是什么技术

上次我们拆过它的风格,这里把每个效果对到**具体 CSS/JS 技术点**,让你知道它们「可不可做、难不难」:

| 效果 | 技术点 | 难度 |
|---|---|---|
| 黄黑配色 | 就是一组 CSS 变量值 | 极易,填变量即可 |
| 四角括号瞄准框 | 4 个绝对定位的小 div,只画两条边(`border-top`+`border-left`) | 易,纯 CSS |
| 扫描线 | `linear-gradient` 重复条纹做背景 | 易,纯 CSS |
| 网格 / 噪点 | `linear-gradient` 网格 + 一张噪点图,半透明叠在最上层 | 易(我们 `texture.css` 已有类似) |
| 数据流瀑布 | 一堆随机十六进制文字 + CSS `@keyframes` 动画向上滚 | 中,要点 JS 生成内容 |
| 打字机渐入 | JS 用 `setInterval` 每隔几十毫秒多显示一个字 | 中,纯 JS 逻辑 |
| 3D 视差倾斜 | 监听鼠标位置,用 CSS `transform: perspective() rotateX/Y()` 让容器随鼠标轻微倾斜 | 中,JS 算角度 + CSS 变换 |

**结论**:这些没有一个是「做不到」或「很危险」的,全是成熟的 CSS/JS 技巧。区别只在「静态视觉(配色/边框/质感)非常容易」,「动效(数据流/打字机/3D)需要写一点 JS、且要考虑性能和‘看久了累不累’」。这正是下一步要跟你确认的「保真度」问题。

---

# 第 7 章 · A1 单页试装 vs A2 全局换肤:把难点彻底讲透

这是你最想搞懂的一章。难点的本质,一个词:**作用域(影响范围)**。

## 7.1 A2 全局换肤:做法与难点

**做法**:就是第 5 章那条链的标准玩法——
1. 在 `theme.css` 加一块 `[data-theme="machine"] { --bg-base:#020202; --accent-primary:#FFD700; ... }`;
2. 在 `useTheme.ts` 的 `ALL_THEMES` 里加 `'machine'`;
3. 切换器自动多出一个「The Machine」按钮。

**难点 = 波及面是整站**:一旦切到 machine,`<html data-theme="machine">` 一改,**首页、个人页、公告页、demo 外壳……每一个用了 `bg-base`/`text-primary` 的地方,全部立刻变黄黑**。于是:
- 你得**逐页检查**:首页作品卡在纸白下好看,套黄黑会不会糊?个人页、公告板的边框、阴影会不会怪?**测试面 = 整站每一页**。
- 出问题**回退也是全站**。
- 重动效(3D 倾斜、CRT 抖动)若做进主题,会**全站都抖**,长时间阅读累。

不是技术难,是**牵一发动全身,验证成本高**。

## 7.2 A1 单页试装:做法与难点

**做法**:不动 `<html>` 那个全局开关,而是**只在 Demo 页外面包一层「盒子」**,把皮关在盒子里。两种常见实现:

**写法一(作用域 class)**:给 Demo 页最外层套一个 class,比如 `<div className="skin-machine">`,然后写:

```css
.skin-machine {
  --bg-base: #020202;        /* 只在这个盒子内,重定义这些变量 */
  --text-primary: #FFD700;
  --accent-primary: #FFD700;
}
```

CSS 变量有个好性质:**就近覆盖**。盒子内的元素取 `var(--bg-base)` 时,会先看到盒子上重定义的黑色;盒子外的首页,还是全局的纸白。**皮自动被关在盒子里。**

**写法二(更隔离)**:用第 4.3 节讲的——`App.tsx` 里只有 `/nexus` 这条路由经过判断挂上 `skin-machine`,别的 demo 不挂。

**难点 = 只剩一个小点:别让样式漏出盒子**。因为 CSS 有「继承」(5.1c),文字颜色这类会往子元素传染;只要我们把变量重定义**严格写在 `.skin-machine` 这个盒子选择器下**,它的影响就到盒子边界为止。这是个可控的小心点,不是全站级风险。

**所以「A1 改起来方便」的准确含义**:
- 波及面 = 一页 → 验证只看一页;
- 出错 = 删一个 class / 一段 CSS 即可回退;
- 首页等其它页**零风险**(根本没碰)。

## 7.3 为什么 A1 能"无损升级"成 A2

关键:**A1 和 A2 用的是同一批 CSS 变量,只是写在不同的选择器下**。

- A1:`.skin-machine { --bg-base:#020202; ... }`(变量关在盒子选择器里)
- A2:`[data-theme="machine"] { --bg-base:#020202; ... }`(同一批变量,挪到主题选择器里)

**变量名一样、值一样,只是外面那层选择器从 `.skin-machine` 换成 `[data-theme="machine"]`**。所以 A1 做的配色调试工作,A2 一行都不浪费——把那一块 CSS「剪切」到主题选择器下,再在 `ALL_THEMES` 注册一下即可。这就是我说的「循序渐进、无损升级」的代码层依据。

## 7.4 一句话总结这一章

> A1 和 A2 在「写多少 CSS」上几乎一样;差别全在**作用域**:A1 把皮关在一页的盒子里(波及一页、易验证、易回退),A2 把皮挂到全站开关上(波及整站、要逐页验证)。先 A1 调好这套皮的配色与质感,确认好看,再「剪切」到主题选择器升级成 A2,几乎零浪费。

---

# 第 8 章 · 术语速查 + 进阶路径

## 8.1 术语速查表

| 术语 | 一句话解释 |
|---|---|
| HTML | 网页的结构和内容(毛坯) |
| CSS | 网页的样式(装修) |
| JavaScript (JS) | 网页的行为(水电机关) |
| DOM | 浏览器把 HTML 变成的那棵「节点树」;改网页=改 DOM |
| TypeScript (TS) | 带类型检查的 JavaScript,写错提前报错 |
| `.tsx` | 用 TS 写的 React 组件文件(TS + JSX) |
| React | 把界面拆成可复用「组件」、数据驱动界面的库 |
| 组件 (Component) | 返回 JSX 的函数,一块可复用的 UI 积木 |
| JSX | 写在 JS 里、长得像 HTML 的语法 |
| props | 父组件传给子组件的只读参数 |
| state | 组件自己的、会变的数据(一变就重画) |
| hook | 以 `use` 开头的特殊函数,给组件加能力(useState/useEffect/useTheme) |
| Vite | 把源码翻译/打包、并提供热刷新开发服务器的构建工具 |
| npm | 包管理器(下载第三方库) |
| package.json | 项目身份证 + 依赖清单 + 命令 |
| node_modules | npm 下载的库堆放处(不进 git) |
| SPA | 单页应用:整站一个 html,JS 动态画页面 |
| 路由 (Router) | 按 URL 决定显示哪个页面组件 |
| iframe | 在网页里嵌入另一个完整网页(独立文档) |
| 文档隔离 / 同源策略 | 浏览器铁律:iframe 内外样式互不渗透 |
| CSS 变量 | `--x: 值` 定义、`var(--x)` 引用的可复用颜色/尺寸 |
| Tailwind | 用大量「原子类」(`flex`/`bg-base`)写样式的方案 |
| data-theme | 挂在 `<html>` 上的属性,换肤的总开关 |
| nginx / 反向代理 | 按网址前缀把请求转给不同后端的「交通警察」 |

## 8.2 由浅入深的学习路径建议

1. **第一周·吃透三大件**:手写几个 `test.html`,玩 HTML 标签、CSS 选择器、JS 改 DOM。目标:能徒手做一个「点按钮变色」的小页面。
2. **第二周·读懂我们的代码**:对照本文第 4 章,把 `index.html → main.tsx → App.tsx → Demo.tsx → DemoFrame.tsx` 这条线读通,能讲出每个文件干嘛。
3. **第三周·React 基础三件套**:专门搞懂 `props / state(useState) / 副作用(useEffect)`。我们 `DemoFrame.tsx` 的加载状态、`useTheme.ts` 都是现成教材。
4. **第四周·换肤实战**:跟着本次 A1,亲手在 `theme.css` 加一块变量、给 Demo 页包盒子,改配色看效果。这是把第 5、7 章变成肌肉记忆的最好方式。
5. **进阶**:CSS 布局(flex / grid)、Tailwind 常用类、React 组件拆分原则。再往后才需要碰构建配置、性能优化这些。

**核心心法**:不要试图一次学完所有名词。**每次只为「看懂/改动手上这一个文件」去学最少的知识**,用项目当驱动。你已经有一个真实、自己的项目,这是最好的学习场——比任何教程都强。

---

*本文档随项目演进可更新。配套代码全部在 `frontends/portfolio/`,建议对照阅读。*
