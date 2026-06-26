# Demo 后端共享主题同步 + HUD 化(A3)设计与计划

- **日期**:2026-06-26
- **阶段**:A3 —— 让 5 个 demo 后端的内部 UI 跟随门户主题配色,并统一 HUD 结构 + 思考/错误反馈
- **前置**:A2(门户全局 machine 主题)已完成;门户侧打磨(副标题/网格/金色/图标/信息卡)已完成
- **分支**:`feat/machine-hud-skin`
- **来源反馈**:用户第 4/6/7 点 —— demo 内部不跟主题变色、nexus 撞色、需要思考指示 + 主题化错误框

---

## 1. 背景与决策

各 demo 后端是独立应用,UI 各自写死配色,与门户主题零联动:
- `rag_app/main.py`、`fc_app/main.py`:HTML 内嵌字符串(rag 紫色 `#667eea`)。
- `nexus_app/templates/index.html`:已 HUD,但固定金色,外层非监控主题时撞色。
- `iconforge_app`、`md_converter_app`:`templates/*.html` + `static/style.css`。

**已确认决策(用户选)**:
- **共享主题·实时同步**:每个 demo 读 `localStorage['ai-demos-theme']`,套对应调色板,监听 `storage` 事件即时变色。所有 demo 采用 HUD 结构(方框边界/等宽/闪烁状态点)但**颜色跟随主题**。
- 第 7 点:加"思考中"循环 `...` 指示;错误用三角形内嵌 `!` 警告框,样式由主题变量决定(各主题自动不同色)。

## 2. 机制(为什么 iframe 能实时同步)

门户与各 demo **同源**(生产 `shiyuan-wreg.cloud/` 与 `/rag/`;本地 dev 经 vite 同源代理)。
门户 `setTheme` 执行 `localStorage.setItem('ai-demos-theme', t)` 时,**同源的 iframe 文档会自动收到 `storage` 事件**(storage 事件在除发起改动的文档外的所有同源文档触发)。iframe 据此切 `data-demo-theme`,无需刷新、无需 postMessage。

## 3. 共享资产(DRY)

新建 `frontends/shared/demo-theme.html`(一段可直接内联/引入的 `<style>` + `<script>`),内容:

### 3.1 五主题调色板(token 化)
`html[data-demo-theme="X"]` 各定义统一 token,值对齐门户 `theme.css`:

| token | mono-light | light | deepblue | cyber | machine |
|---|---|---|---|---|---|
| `--d-bg` | #fafafa | #f6f7fb | #0b1120 | #050507 | #0a0a0c |
| `--d-surface` | #ffffff | #ffffff | #111827 | #0f0f12 | #0e0e11 |
| `--d-surface-soft` | #f8f8f9 | #f8fafc | #172033 | #141417 | #111114 |
| `--d-border` | rgba(0,0,0,.12) | #e2e8f0 | #1f2937 | #27272a | rgba(227,179,65,.30) |
| `--d-text` | #09090b | #0f172a | #f8fafc | #e4e4e7 | #e3b341 |
| `--d-dim` | #71717a | #64748b | #94a3b8 | #71717a | #9a8c5a |
| `--d-accent` | #09090b | #4f46e5 | #2563eb | #a3e635 | #e3b341 |
| `--d-accent-text` | #fafafa | #ffffff | #ffffff | #050507 | #0a0a0c |
| `--d-danger` | #dc2626 | #dc2626 | #f87171 | #ff5577 | #ff4500 |
| `--d-font` | sans | sans | sans | mono | mono |

(machine/cyber 用等宽字体强化终端感;其余 sans。)

### 3.2 共享组件 CSS(全用上面 token,主题自动变色)
- `.hud-box`:`background:var(--d-surface); border:1px solid var(--d-border); border-radius:0;` + 四角方括号(8 段 1px 渐变,色 `--d-accent`)。
- `.hud-head`:顶栏 + 闪烁状态点 `.dot`(machine 红点,其余用 `--d-accent`)。
- `.thinking`:三个循环跳动的点(`思考中` + `<span class="dots"><i></i><i></i><i></i></span>`,`@keyframes` 错相位 opacity)。
- `.alert`:警告框 —— 左侧三角 `▲` 内嵌 `!`(用 CSS 画或 `⚠`),边框/文字色 `--d-danger`,背景 `color-mix` 淡化。直角 + 角标。

### 3.3 同步脚本
```js
(function(){
  var KEY='ai-demos-theme', VALID=['mono-light','light','deepblue','cyber','machine'];
  function apply(t){ if(VALID.indexOf(t)<0)t='mono-light'; document.documentElement.setAttribute('data-demo-theme',t); }
  try{ apply(localStorage.getItem(KEY)); }catch(e){ apply('mono-light'); }
  window.addEventListener('storage', function(e){ if(e.key===KEY) apply(e.newValue); });
})();
```

## 4. 落地顺序(逐后端验收)

| 序 | 后端 | 动作 | 验收 |
|---|---|---|---|
| 1 | **rag**(参考实现) | HTML_PAGE token 化 + 内联共享块 + HUD 框 + thinking + alert | 切 5 主题即时变色,思考点动,制造错误看警告框 |
| 2 | 抽取共享块到 `frontends/shared/demo-theme.html`,rag 改为构建期注入 | 同上无回归 | |
| 3 | **fc** | 同 rag 套路 | |
| 4 | **nexus** | 固定金色→token,跟随主题(保留红点/扫描线结构) | 非监控主题不再撞色 |
| 5 | **iconforge** | `home.html`+`style.css` token 化 | |
| 6 | **md_converter** | `base/home/login.html`+`style.css` token 化 | |

> rag 先内联验证机制真的能透过 iframe 实时同步,再抽共享文件复制到其余,避免提前过度抽象。

## 5. 部署注意
- 本地:`docker cp backends/<app>/... deploy-<app>-1:/app/... && docker restart deploy-<app>-1`;改 nginx 容器 IP 变会 502,需 restart nginx。
- 生产:重建对应镜像。
- 同步脚本依赖同源;跨子域部署会失效(当前单域,无问题)。

## 6. 非目标
- 不改门户主题系统(已稳定)。
- 不引第三方依赖。
- demo 业务逻辑(RAG/FC 调用、评估)不动,只改样式与加载/错误反馈。

## 7. 回退
每个 demo 改动独立且仅限其 UI 字符串/模板;回退=还原该文件。门户零影响。
