# ai-demos 门户视觉升级设计文档 —— 黑白高级感科技风

> 立项日期:2026-06-25
> 参照来源:Hugo 主题 **aiovtue**(樱花/Sakura 风,移植自 Valaxy)
> 目标基调:**黑白(单色)高级感科技风**(参照系:Linear / Vercel / Apple / Stripe-dark)
> 作用范围:`frontends/portfolio` 门户外壳(首页 / Demo 页 / 学习页 / 个人页 / 更新页)
> 工作分支:`worktree-feat+portfolio-ui-redesign`

---

## 0. 这份文档怎么用

这是一份**视觉方向设计规格(design spec)**,不是实现计划(plan)。它回答三个问题:

1. **现状为什么单调**(诊断,第 1 节)
2. **从 aiovtue 学到的可迁移原则**(每条都讲:它怎么做 → 为什么有效 → 我们改造成黑白科技风怎么做,第 2 节)
3. **黑白科技风的具体规格**(可直接落地的 design token、字体、组件改造、动效目录,第 3–7 节)

读完后,我们再据此写一份 implementation plan(逐 Task),在 worktree 里实施。文末有术语表(第 9 节)和系统学习路径(第 10 节)。

> 命名约定:本文把要新增的黑白主题命名为 **`mono`**(monochrome,单色)。它将作为门户的**新默认主题**,与现有 `light / deepblue / cyber` 并存于已有的主题切换器中。

---

## 1. 现状诊断

### 1.1 你提出的四个病灶

| 病灶 | 本质 | 对应的修复方向 |
|---|---|---|
| 页面单调 | 视觉只有"卡片 + 文字",没有层次与节奏 | 引入质感层(网格/噪点/辉光)、首屏 hero、节奏化布局 |
| 经典 AI 蓝紫配色 | 默认 accent = `#4f46e5`(靛蓝),撞脸所有 AI 模板 | 换成单色灰阶基调,去掉"模板感"色相 |
| 视觉不突兀但也不吸引 | 安全但平淡,缺记忆点 | 给一个标志性首屏 + 克制但精致的微交互 |
| 图标没设计 | 图标是装饰,不成体系、无身份 | 建立"图标 + 编号 + 单色"的 demo 身份系统 |

### 1.2 当前 token 体系(改造的起点)

文件:`frontends/portfolio/src/styles/theme.css`。当前已有完整的 CSS 变量体系和三套主题:

- `light`(默认):`--bg-base:#f6f7fb`,`--accent-primary:#4f46e5`(靛蓝紫)—— **这就是"AI 蓝紫"的来源**。
- `deepblue`:深蓝科技,accent `#2563eb`。
- `cyber`:近黑底 + 荧光绿 accent `#a3e635`。

> **好消息**:token 架构已经很规范(色彩 / 间距 / 圆角 / 阴影全部是 CSS 变量,且 dark 模式全量覆盖)。所以"换风格"= **新增一套 `mono` 主题变量 + 重制几个组件的样式**,不需要重写架构。这是改造成本低的根本原因。

> **关键认知**:`cyber` 主题其实已经接近"黑底科技"了,但它**靠荧光绿 accent 制造科技感**。黑白高级风的难点恰恰相反 —— **不靠颜色,靠灰阶层次、留白、发丝级边框和字体**撑起高级感。颜色一多就"潮"而不"贵"。

---

## 2. 从 aiovtue 学到什么(6 条可迁移原则)

aiovtue 是樱花粉 + 手写楷体的文艺博客风,**和我们要的黑白科技风表面相反**。但它"统一又有趣"的底层手法是风格无关的,可以整套搬过来,只是把"性格参数"从樱花换成黑白科技。下面每条都讲清因果。

### 原则 1:主色要有"派生色阶",并用 `color-mix` 渗透全站

**它怎么做**:主色 `#df9193` 派生出 light / lighter / dark 四档;卡片背景不是写死的灰,而是把主色按 8–10% 混进灰底:

```scss
background: color-mix(in srgb, var(--sakura-color-primary) 10%, var(--sakura-post-card-bg));
```

**为什么有效**:全站每个面板都隐隐透着同一股主色 → 这是"风格统一但不死板"的底层机制。统一感不是靠"都用同一个灰",而是靠"都带同一点主色味"。

**我们怎么改造**:黑白风没有"彩色主色",但这条原则照搬 —— 我们的"主色"是**中性灰阶 + 一束白光**。卡片/悬浮态用 `color-mix` 在不同明度的灰之间过渡,辉光统一用半透明白。"渗透"的不是色相,是**明度层次**。

### 原则 2:导航/每个入口给"专属色",而不是全站一个 accent

**它怎么做**:导航每个链接一个图标色,铺成红→橙→黄一条暖色谱(`#e03131 → #f03e3e → #ff8787 → #fab005 → #ffd43b`)。

**为什么有效**:既有变化(每项不同)又成体系(同一条色谱)。打破"全站一个 accent"的单调。

**我们怎么改造**:黑白风不能用色相区分,改用**「编号 + 图标 + 单色明度」三件套**建立 demo 身份(详见第 7 节)。例如 `01 RAG / 02 FC / 03 Nexus / 04 DocHub / 05 Learn`,每个配一个线性图标,差异来自图标形态和编号,而非颜色。这是把"色谱区分"翻译成"序列区分"。

### 原则 3:用一款有性格的字体定义气质

**它怎么做**:正文+标题都用霞鹜文楷(LXGW WenKai Screen,开源手写楷体),字体文件本地打包。

**为什么有效**:同样的布局,换成手写楷体就从"冷技术站"变"温暖博客"。**字体是气质的最大单一变量**。

**我们怎么改造**:把"手写楷体"换成科技风对应物 —— **几何无衬线(grotesk)做 UI + 等宽字体(monospace)做元信息**。等宽字体用在编号、标签、时间、技术栈这些"数据"上,是 Linear / Vercel 的标志性手法,瞬间"高级科技"。中文用几何感黑体(HarmonyOS Sans / MiSans),不用手写体。详见第 4.2 节。

### 原则 4:首屏 hero 要"有内容、有记忆点"

**它怎么做**:全屏背景图 + 暗 overlay + 双层动态波浪 + glitch 故障大标题 + 打字机一言 + 毛玻璃 social 卡 + 浮动下滚箭头。

**为什么有效**:首屏是门面,决定"第一眼是否被记住"。它把好几个"视觉锤"叠在一起。

**我们怎么改造**:把"照片+波浪"的文艺首屏换成**科技首屏** —— 动态网格背景(grid)+ 径向白色辉光 + 等宽字体打字机标题(可保留 glitch,但用黑白版)+ 一个终端/代码风格的元素。不堆照片,堆"结构感"。详见第 5.2 节。

### 原则 5:建一套可复用的「微交互动效系统」

**它怎么做**:8 方向 fade-in/out keyframe 类 + `IntersectionObserver` 滚动入场 + 持续浮动(loop-float)+ View Transition API 主题切换(从点击点扩散的圆形过渡)+ 图片懒加载淡入 + 导航下划线 width 0→100% + 卡片 hover scale。全部包 `prefers-reduced-motion` 降级。

**为什么有效**:这些动效不是一处一处临时写的,而是**统一的类**,所以全站动效语言一致 → 这是"精致感"的来源。一致的克制动效 = 高级;杂乱花哨 = 廉价。

**我们怎么改造**:照搬这套系统,但**风格收敛到"克制"** —— 黑白高级风的动效要"少而准":hover 时边框提亮 + 微辉光、滚动入场上浮 8px、主题切换用 View Transition。不要弹跳、不要彩色光晕。详见第 6 节。

### 原则 6:卡片用"描边 + 节奏化布局",而非千篇一律浮卡

**它怎么做**:卡片 `border:1px solid rgba(0,0,0,.85)`(重描边,非阴影);列表奇偶卡左右镜像(`flex-direction:row-reverse` + `text-align` 翻转)。

**为什么有效**:描边 = 手账/插画风,不是 Material 浮卡的"千篇一律";左右交替 = 列表有节奏不呆板。

**我们怎么改造**:黑白科技风同样**弃阴影、用发丝边框**(hairline,`1px rgba(255,255,255,0.10)`),但描边要"细、冷",不是粗黑线。节奏感改用**不等宽网格 / bento 布局**(大小卡混排)而非简单镜像。详见第 5.3 节。

---

## 3. 目标风格定义:黑白高级感科技风

### 3.1 参照系与关键词

- **参照系**:Linear(发丝边框 + 等宽元信息 + 极暗底)、Vercel(纯黑白 + 大留白 + 几何字体)、Apple 产品页(留白 + 微辉光)、Stripe dark(层次化深灰)。
- **关键词**:克制(restraint)、留白(negative space)、发丝边框(hairline)、灰阶层次(grayscale depth)、单色辉光(monochrome glow)、等宽元信息(mono metadata)、结构感(grid / structure)。

### 3.2 一句话设计原则

> **颜色做减法,层次做加法。** 把色相全部抽掉,用「明度 + 留白 + 边框 + 字体 + 一束白光」重建高级感。任何想加颜色的冲动,先问:能不能用灰阶层次或留白解决?

### 3.3 三条红线(避免翻车)

1. **不要纯黑纯白对撞**:底不是 `#000`,是 `#0a0a0b`(墨黑);白不是 `#fff`,是 `#f4f4f5`。纯黑纯白边缘刺眼、显廉价。
2. **不要靠阴影堆深度**:高级感来自发丝边框 + 微妙的表面明度差,不是大块投影。
3. **最多一束"信号色"**:整站默认纯单色;若日后要点睛,**只允许一个**信号色(建议冷白/极淡蓝白),且只用于"当前态/焦点",不铺面。

---

## 4. 设计 Token 规范(可直接落地)

下面给出新增的 `mono` 主题完整变量,直接对照 `theme.css` 现有结构编写,落地时追加到该文件即可。

### 4.1 色彩:灰阶 + 单束白光

```css
/* === 新增:黑白科技风(暗色,设为新默认) === */
[data-theme="mono"] {
  /* 背景:墨黑,不是纯黑 */
  --bg-base:   #0a0a0b;
  --bg-soft:   #0e0e10;
  --bg-soft-rgb: 14, 14, 16;

  /* hero:网格 + 顶部一束冷白辉光(替代彩色径向渐变) */
  --bg-hero:
    radial-gradient(900px 480px at 50% -8%, rgba(255,255,255,0.10), transparent 70%),
    linear-gradient(180deg, #0d0d0f 0%, #0a0a0b 60%, #08080a 100%);

  /* 表面:三档明度,靠明度差分层,不靠阴影 */
  --surface-default: #0f0f11;
  --surface-raised:  #161618;
  --surface-hover:   #1c1c20;
  --surface-soft:    #121214;

  /* 发丝边框:半透明白,细而冷 */
  --border-default: rgba(255,255,255,0.10);
  --border-subtle:  rgba(255,255,255,0.06);
  --border-strong:  rgba(255,255,255,0.18);   /* 焦点/hover 提亮用 */

  /* 文字:灰阶四档(zinc 色阶) */
  --text-primary:   #f4f4f5;
  --text-secondary: #a1a1aa;
  --text-tertiary:  #71717a;
  --text-muted:     #52525b;
  --text-link:      #fafafa;

  /* accent = 白本身(单色风的"主色"就是白) */
  --accent-primary:      #fafafa;
  --accent-primary-text: #0a0a0b;        /* 白底上的字用墨黑 */
  --accent-secondary-bg: rgba(255,255,255,0.08);
  --accent-secondary-text: #f4f4f5;

  /* 辉光:半透明白,极克制 */
  --glow-accent: rgba(255,255,255,0.14);

  /* 阴影:几乎不用投影,改用"内描边 + 极淡外发光" */
  --shadow-sm:  0 0 0 1px rgba(255,255,255,0.04);
  --shadow-md:  0 0 0 1px rgba(255,255,255,0.06), 0 8px 24px rgba(0,0,0,0.45);
  --shadow-lg:  0 0 0 1px rgba(255,255,255,0.08), 0 16px 48px rgba(0,0,0,0.55);
  --shadow-glow:0 0 0 1px rgba(255,255,255,0.14), 0 0 28px rgba(255,255,255,0.06);

  /* 质感层(第 4.4 节用) */
  --grid-line:  rgba(255,255,255,0.04);   /* 网格线 */
  --noise-opacity: 0.025;                 /* 噪点强度 */
}
```

可选的**亮色版**(纸白高级风,"paper"),供主题切换里做亮色档:

```css
[data-theme="mono-light"] {
  --bg-base: #fafafa;  --bg-soft: #ffffff;
  --surface-default:#ffffff; --surface-raised:#ffffff; --surface-hover:#f4f4f5;
  --border-default: rgba(0,0,0,0.10); --border-subtle: rgba(0,0,0,0.06); --border-strong: rgba(0,0,0,0.20);
  --text-primary:#09090b; --text-secondary:#3f3f46; --text-tertiary:#71717a; --text-muted:#a1a1aa;
  --accent-primary:#09090b; --accent-primary-text:#fafafa;
  --glow-accent: rgba(0,0,0,0.08);
  --grid-line: rgba(0,0,0,0.04); --noise-opacity: 0.02;
}
```

> **为什么这样选**:zinc 灰阶(`#fafafa → #52525b`)是冷中性灰,比 slate(带蓝)更"无色"、更高级。背景 `#0a0a0b` 略带一丝暖,避免纯黑的"死"。边框全用半透明白,这样在任何表面明度上都自适应,且天生比实色边框"轻"。

### 4.2 字体:几何无衬线 + 等宽元信息

这是把 aiovtue「用字体定义气质」翻译到科技风的关键一步。

```css
:root {
  /* UI 主字体:几何无衬线 grotesk;中文用几何黑体 */
  --font-sans: "Inter", "Geist", -apple-system, BlinkMacSystemFont,
               "HarmonyOS Sans SC", "MiSans", "PingFang SC", "Microsoft YaHei", sans-serif;

  /* 等宽:用于编号/标签/时间/技术栈/代码 —— 科技感的标志 */
  --font-mono: "Geist Mono", "JetBrains Mono", "IBM Plex Mono",
               ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
}
```

**用法规则(很重要,这是"高级科技"观感的一半)**:

- **大标题 / 正文** → `--font-sans`(几何无衬线),字重拉开:标题 600–700,正文 400。
- **元信息一律 `--font-mono`**:demo 编号(`01`)、技术栈标签(`FastAPI` `SSE`)、版本号(`v0.3`)、日期(`2026-06-25`)、导航的小标签。等宽字体 + 字间距 `letter-spacing: 0.04em` + 大写 + 偏小字号(12–13px)+ 次级灰,是 Linear/Vercel 的"签名"。
- **字体托管**:Inter / Geist / Geist Mono / JetBrains Mono 均开源可商用。优先**本地打包 woff2**(像 aiovtue 打包字体一样),避免 CDN 抖动;打包子集化(中文按需子集)控制体积。

> **因果**:为什么等宽字体一上就"科技"?因为人脑把等宽字 = 终端/代码 = 工程。把"数据型文字"(编号、标签、时间)排成等宽,潜意识就读出"这是个工程师做的工具站",正好贴合你 AI/Agent 作品集的定位。

### 4.3 间距 / 圆角 / 边框

- **间距**:沿用现有 `--space-*` 体系,但**整体留白加大一档**。高级感 = 舍得留白。区块上下 padding 用 `--space-16`(64px)起步,卡片内 `--space-6`(24px)。
- **圆角**:收敛。科技风偏"硬朗",建议主圆角降到 `--radius-md:8px` / 卡片 `10px`,**不要 16px 大圆角**(大圆角偏"亲和消费风",不够冷)。
- **边框**:全站统一 `1px solid var(--border-default)`(发丝)。hover/focus 时切到 `--border-strong` 提亮,而不是加阴影。

### 4.4 质感层:网格 + 噪点 + 辉光(打破"单调"的核心)

"单调"的根因是**背景是纯色平面**。加三层几乎不可见的质感即可破解:

1. **点阵/网格背景**(全站底层,极淡):
```css
body::before {
  content:""; position:fixed; inset:0; z-index:-1; pointer-events:none;
  background-image:
    linear-gradient(var(--grid-line) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
  background-size: 56px 56px;
  mask-image: radial-gradient(ellipse at 50% 0%, #000 30%, transparent 80%); /* 越往下越淡 */
}
```

2. **噪点(film grain)**:一张 base64 SVG 噪点铺满,`opacity: var(--noise-opacity)`,`mix-blend-mode: overlay`。让纯色表面有"胶片颗粒",消除塑料感。

3. **辉光(glow)**:hero 顶部一束冷白径向光(已写进 `--bg-hero`);卡片 hover 时 `box-shadow: var(--shadow-glow)` 给一圈极淡白光。

> 三层都是"几乎看不见"的强度 —— 看不见但能感觉到,这正是高级感的工作方式。

---

## 5. 组件级改造指南

对照 worktree 现有组件(`frontends/portfolio/src/components` 与 `pages`)逐个说明。

### 5.1 NavBar(导航栏)

- 背景:`rgba(10,10,11,0.72)` + `backdrop-filter: blur(12px)`(毛玻璃),滚动后加一条底部发丝线 `border-bottom:1px solid var(--border-subtle)`。
- 品牌名用 `--font-sans` 700;导航项用 `--font-mono` 小写 + `letter-spacing`。
- hover 用 aiovtue 那招:下划线 `width:0 → 100%`(`--accent-primary` 白线),0.3s。
- 当前页指示:用一个等宽编号或一个发亮的点,不用色块。

### 5.2 Hero(首屏 —— 重点新增)

替换现有 hero,做一个**科技首屏**:

- 背景:`--bg-hero`(网格 + 顶部冷白辉光)+ 4.4 的全局网格在 hero 区加密(`background-size:40px`)。
- 主标题:用 `--font-sans` 超大字重(clamp 到 ~64–96px),内容例如「构建可运行的 AI / Agent 应用」。可选 **glitch 效果的黑白版**(把 aiovtue 的红蓝错位改成"白 + 浅灰"双影,克制版)。
- 副标题:`--font-mono` 一行,做**打字机效果**(照搬 aiovtue 的 typewriter,但内容换成技术化短句,如 `RAG · Function-Calling · Multi-Agent · 已部署生产`)。
- 一个**终端风格元素**(可选,记忆点):一个假终端窗口,等宽字逐行打出 `$ curl https://www.shiyuan-wreg.cloud/rag ...` —— 强化"工程师的工具站"身份。
- 底部浮动下滚箭头(照搬 `loop-float`)。

### 5.3 WorkCard(作品卡 —— 破单调重点)

- 容器:`--surface-default` + 发丝边框,圆角 10px,**弃投影**。
- hover:`transform: translateY(-2px)` + 边框切 `--border-strong` + `--shadow-glow` 微白光 + 卡内右上角图标轻微放大。克制,无弹跳。
- 卡内结构(自上而下):
  1. 顶部一行:**等宽编号**`01` + 右侧线性图标(第 7 节)。
  2. 标题(`--font-sans` 600)。
  3. 一句话描述(`--text-secondary`)。
  4. 技术栈标签:`--font-mono` 小标签,边框 chip(`border:1px solid --border-subtle`,无填充),如 `FastAPI` `SSE` `通义千问`。
- 布局节奏:首页作品区改 **bento 网格**(大小卡混排:主推 demo 占大格,其余小格),替代等宽规整网格 —— 这是打破单调最有效的一招。

### 5.4 Demo 页(iframe 容器)

- 沿用现有"侧栏作品导航 + iframe 工具栏",但工具栏改极简:左侧等宽显示当前 demo 编号+名,右侧线性图标按钮(刷新/新窗口),全部发丝边框。
- iframe 外层加 1px 发丝边框 + 顶部一条极淡辉光,让嵌入内容"被框住"而不突兀。

### 5.5 Me(个人页)

- 沿用已定的**匿名 + 作品导向**结构(无姓名/学校/自我介绍,这条 2026-06-24 已多次确认,继续保持)。
- hero 区:把现有彩色渐变 glow 换成黑白网格 + 冷白辉光;头像用代码字形/几何 logo(单色)。
- 技能栈分组卡:标题用 SectionTitle + 等宽编号;技能项用 4.2 的等宽 chip。
- 定位标语保持「构建可运行的 AI/Agent 应用」。

### 5.6 Changelog(更新页)

- 沿用已定的**统一卡片列表**(2026-06-24 已收敛,不再用便签墙/酒馆告示)。
- 每条:左侧等宽版本号 `v0.3` + 日期(mono);右侧更新条目。卡片发丝边框,与全站一致。
- 首页公告板单卡同样套用 mono 风格(发丝边框 + 等宽版本号 + 整卡可点)。

---

## 6. 微交互动效目录(克制版)

照搬 aiovtue 的动效"系统化"思路,但收敛到高级风需要的几个:

| 动效 | 触发 | 实现 | 强度 |
|---|---|---|---|
| 滚动入场 | 元素进入视口 | `IntersectionObserver` + `translateY(8px)→0` + opacity | 0.5s ease-out,只播一次 |
| 卡片 hover | 鼠标悬停 | `translateY(-2px)` + 边框提亮 + 微白光 | 0.25s |
| 导航下划线 | hover | `width:0→100%` 白线 | 0.3s |
| 主题切换 | 点击切换 | View Transition API,从点击点扩散圆形过渡 | 照搬 aiovtue |
| 打字机 | hero 加载 | 逐字 + 闪烁等宽光标 `_` | 80ms/字 |
| 持续浮动 | 下滚箭头/装饰 | `loop-float` 上下 6px | 2s 无限 |
| 图片懒加载淡入 | 进入视口 | opacity 0→1,占位用 `--surface-soft` | 0.45s |

- **全部包 `prefers-reduced-motion: reduce` 降级**(无障碍,照搬 aiovtue)。
- 红线:不要弹跳(bounce)、不要彩色光晕、不要超过 0.5s 的长动画。**克制 = 高级**。

---

## 7. Demo 身份系统(图标 + 编号 + 单色)

解决"图标没设计"。不靠色相区分,靠**序列 + 图标形态**:

| 编号 | Demo | 线性图标(建议 Lucide) | 一句话 |
|---|---|---|---|
| `01` | RAG 文档问答 | `file-search` / `book-open` | 检索增强问答 |
| `02` | Function Calling | `terminal` / `function-square` | 工具调用 Agent |
| `03` | Nexus | `workflow` / `git-branch` | Multi-Agent 工作流 |
| `04` | DocHub | `file-text` / `folder-tree` | Markdown 文档站 |
| `05` | Learn | `graduation-cap` / `sparkles` | 交互式学习站 |

- **统一图标库**:全站只用一套线性图标(推荐 **Lucide**,细线、几何、开源,科技感强;或 Iconify 里选一套 stroke 风格)。禁止混用多套风格。
- **统一处理**:全部单色(`currentColor`),`stroke-width` 一致,尺寸网格对齐。
- **身份来自三件套**:等宽编号 + 专属图标 + 在 hover/当前态时该图标发白光。颜色全程不参与区分。

> 这正是把 aiovtue「每个导航项一个专属色」的**区分需求**,用黑白风能接受的方式(序列+形态)重新实现。

---

## 8. 实施计划(分阶段,落地时再细化为 plan)

> 下面是路线图概览;正式实施前会另写一份逐 Task 的 implementation plan。

- **阶段 A — Token 与字体地基**:在 `theme.css` 追加 `mono` / `mono-light` 主题;接入 Inter/Geist + Geist Mono/JetBrains Mono(本地 woff2 子集);把 `mono` 设为默认;主题切换器加入新档。**这一步完成,全站就已变黑白科技底色**。
- **阶段 B — 质感层**:加全局网格 + 噪点 + 辉光(4.4)。
- **阶段 C — 组件重制**:NavBar → WorkCard → Demo 页 → Me → Changelog 逐个套用 mono 规格(第 5 节)。
- **阶段 D — Hero 新增**:科技首屏(网格 + 打字机 + 可选终端/ glitch 黑白版)。
- **阶段 E — 身份系统**:接入 Lucide,落地编号 + 图标(第 7 节)。
- **阶段 F — 动效系统**:滚动入场 + hover + View Transition 主题切换(第 6 节)。
- **阶段 G — 验证**:本地 Docker 全路由 200 + 逐页视觉确认 → 满意后合并 master + 重新部署首尔服务器。

每阶段构建后在 `:8080` 即时可看(worktree 已与本地 stack 联动)。

---

## 9. 术语表

- **Design token**:把颜色、间距、字号等设计决策抽象成命名变量(CSS 自定义属性),改一处全站生效。本项目集中在 `theme.css`。
- **Hairline border(发丝边框)**:1px 极细、通常半透明的边框。高级 UI 用它替代阴影来分层。
- **`color-mix()`**:CSS 函数,按比例混合两种颜色。用来从基色派生出"带一点主色味"的表面色。
- **Grotesk**:一类几何感强、无衬线的字体(如 Inter、Geist),科技/工程气质。
- **Monospace(等宽字体)**:每个字符等宽,源自终端/代码。用在元信息上 = 工程观感。
- **Bento 布局**:像便当盒一样大小格子混排的网格,打破等宽规整网格的单调。
- **View Transition API**:浏览器原生页面/状态过渡 API,可做"从点击点扩散"的主题切换动画。
- **`IntersectionObserver`**:监听元素是否进入视口的浏览器 API,用来触发滚动入场动画。
- **`prefers-reduced-motion`**:用户系统"减少动态效果"偏好;尊重它做降级是无障碍基本要求。
- **Glitch 效果**:文字红蓝(本项目改白灰)错位 + 抖动的故障美学效果。
- **Film grain(噪点)**:叠一层极淡随机噪点,消除纯色表面的"塑料感"。

---

## 10. 系统学习路径(想深入做好黑白高级风)

按"先看、再拆、后练"的顺序:

1. **建立审美参照**(看):精读 Linear(linear.app)、Vercel(vercel.com)、Geist 设计系统(vercel.com/geist)、Stripe 文档站。重点观察它们**怎么用灰阶分层、等宽字体放在哪、留白多大、边框多细**。
2. **理解灰阶与色彩空间**(知其所以然):了解 OKLCH/HSL 与"为什么 zinc 比 slate 更无色"、为什么不用纯黑纯白。Tailwind 的 zinc/neutral 色阶是现成参照。
3. **字体工程**(练基本功):学 woff2 子集化(`fonttools`/`subfont`)、`font-display: swap`、中文按需子集 —— 这是"本地打包字体不卡"的关键。
4. **微交互**(练手感):掌握 `IntersectionObserver` 滚动入场、CSS `transition` 缓动曲线、View Transition API。原则永远是"少而准"。
5. **质感层**(进阶):CSS 多重背景(网格)、`mask-image` 渐隐、SVG 噪点 + `mix-blend-mode`、径向辉光。
6. **回到本项目**(落地):按第 8 节阶段 A→G 实施,每阶段在 `:8080` 验证,逐页和我确认视觉。

---

## 最终确认决策(2026-06-25,经预览页 `mono-tech-preview.html` 评审定稿)

> 评审方式:做了一个可在浏览器打开的实时预览页,逐项确认。以下为锁定结论,implementation plan 据此执行。

1. **默认主题 = `mono-light`(纸白高级风)**:暗色 `mono`(墨黑)同时实现,作为切换器里的暗色档。先看亮色效果。
2. **首页加科技 hero**:网格背景 + 冷白辉光 + glitch 黑白大标题 + 等宽打字机副标题 + **假终端记忆点**(逐行敲命令)+ 浮动下滚箭头。三个记忆点(glitch / 打字机 / 终端)**全部保留**。
3. **glitch 参数定稿(自然版)**:
   - 弃用 `steps()` 匀速跳动(机械感根源);改 `ease-in-out`。
   - 静止态保留**极轻恒定错位**(上半 `-.5px` / 下半 `+.5px`,各裁一半)→ 常态就有"失衡"高级感。
   - 故障**偶发爆发**:两层动画时长**互质**(5.7s / 4.3s)→ 很少同步、不规律。
   - 每次爆发窗口**约 22% 周期(≈1.0–1.3s)**,窗口内含 5–6 个微抖动(位移 0.5–3px,opacity 0.45→0.8)→ 失衡状态持续抖动一段、连抖几下再恢复平静,明显可感而非一闪而过。
   - 包 `prefers-reduced-motion: reduce` 降级。
4. **纯黑白,不用信号色**。"选中/当前态"靠**四件套特效**区分(全程无色相):
   - **冷冽底**:表面切到带一丝冷意的中性灰(亮 `#eceff3` / 暗 `#0c0e13`)+ 右上角冷光斜射(`--cold-sheen`,极淡冷调,非彩色)。
   - **偏移 + 动态模糊**:内容 `snap` 动画,从左 `-5px`、`blur(3px)` → `0`、`blur(0)`,0.3s,cubic-bezier(.2,.7,.2,1)。
   - **扫描线**:一道冷光自上而下扫过(`scan` 0.7s,播一次)。
   - 抬升 `translateY(-3px)` + 边框切 `--border-strong` + 图标 `scale(1.06)`。
   - 各特效可单独调强弱/开关;包 reduced-motion 降级。
5. **图标库**:先用 **Lucide**(细线几何);后续用户会替换为指定图标 —— 因此图标要做成**可集中替换**(统一 Icon 组件 + 映射表,换源只改一处)。
6. **旧主题留档**:`light / deepblue / cyber` **保留**在切换器中(防新主题不满意可回退),只是默认改为 `mono-light`。

---

## 附:历史开放问题(已被上方"最终确认决策"取代,留档)

(原 6 个待拍板问题已全部在评审中确认,见上节。)
