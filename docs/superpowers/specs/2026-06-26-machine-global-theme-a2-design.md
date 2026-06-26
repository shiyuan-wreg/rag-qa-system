# The Machine 全局主题(A2)设计文档

- **日期**:2026-06-26
- **阶段**:A2 —— 把监控 HUD 皮肤升级为全站可选主题
- **前置**:A1(/nexus 单页试装)+ B(nexus 后端 HUD 化 + 流式回显)已完成,在分支 `feat/machine-hud-skin`
- **状态**:设计待评审

---

## 1. 背景与目标

A1 把监控皮限定在 `/nexus` 外壳;B 把 nexus 后端 iframe 改成永久 HUD。现在升级为 **A2:machine 成为全站可选主题**,达到"合格换肤"的细节标准——不只换配色,还要统一直角、方括号边框、等宽字体、图标可见、HUD 氛围等所有细节。

### 已确认决策

- **默认主题不变**:`mono-light`(极简)继续做默认;machine 是主题切换器里新增的可选项("监控")。
- **氛围分级**:demo 页全套氛围(网格+扫描线+暗角+CRT);内容页(首页/学习/更新/个人)只要轻量氛围(网格+噪点)+ 配色 + 方括号 + 直角 + 等宽,**不要**扫描线/CRT,保证长文可读。
- **/nexus 永远监控皮**(方案 a):因其后端 iframe 是永久 HUD,`/nexus` 外壳无论当前选什么主题都保持监控风;machine 主题被选中时,其余页面才一起变监控。

### 非目标

- ❌ 不删除/不改动现有 4 个主题(极简/浅色/深蓝/赛博)。
- ❌ 不改 nexus 后端(B 已完成)。
- ❌ 内容页不加 3D 视差(视差仅在 demo 外壳的 MachineSkin 内生效)。

---

## 2. 主题注册

- `src/hooks/useTheme.ts`:`Theme` 类型加 `'machine'`;`ALL_THEMES` 数组加 `'machine'`;`DEFAULT_THEME` 保持 `'mono-light'`。
- `src/components/ThemeToggle.tsx`:`THEMES` 列表加 `{ key: 'machine', label: '监控' }`。
- `src/main.tsx`:初始化脚本已基于 `ALL_THEMES` 校验,无需改。

## 3. 调色板(theme.css)

在 `src/styles/theme.css` 新增 `[data-theme="machine"]` 块,变量值与 `machine-skin.css` 现有私有色板一致(黄 `#ffd700` / 黑 `#0a0a0c` 系),并额外设:

- `--grid-line`(让 texture.css 的全局网格在 machine 下显现)
- `--noise-opacity`(全局噪点)
- `--font-sans` 指向等宽字体栈(JetBrains Mono + CJK 回退)

这样所有用标准变量/Tailwind 类的组件**自动**变监控配色与等宽字体。`--grid-line`/`--noise-opacity` 一设,内容页的轻量氛围(网格+噪点)由现有 `texture.css` 自动渲染,零额外代码。

## 4. 共享细节规则(machine-skin.css)

把"细节规则"从只作用于 `.machine-skin`,扩展为**同时**作用于 `[data-theme="machine"]`(全局)与 `.machine-skin`(/nexus 强制)。每条规则写成两个并列选择器。涉及:

### 4.1 直角(精准,不误伤圆点/旋钮)

```css
[data-theme="machine"] :is(.rounded-sm,.rounded,.rounded-md,.rounded-lg,.rounded-xl,.rounded-2xl),
.machine-skin :is(.rounded-sm,.rounded,.rounded-md,.rounded-lg,.rounded-xl,.rounded-2xl) {
  border-radius: 0;
}
/* 按钮 Button.tsx 用 rounded-full 胶囊,HUD 下也要直角 */
[data-theme="machine"] .btn-lift,
.machine-skin .btn-lift { border-radius: 0; }
```

`rounded-full` 默认**保留**(圆点 bullet、ParallaxToggle 旋钮/轨道、头像、角色标签),仅按钮 `.btn-lift` 单独去圆。

### 4.2 方括号边框(四角)

复用现有 8 段渐变画四角技术。给"卡片级"组件统一加标记类 `hud-frame`,样式作用于:

```css
[data-theme="machine"] .hud-frame,
.machine-skin .hud-frame,
.machine-skin .sidebar-link {  /* 侧边栏项保留已有四角 */
  /* --corner / --corner-len + 8 段渐变,直角边框 */
}
```

需加 `hud-frame` 类的组件(§8 清单):WorkCard、AnnouncementBoard、DemoInfoCard、DemoFrame、SidebarLayout、Me 的各 section、Changelog 文章卡。

### 4.3 图标可见

```css
[data-theme="machine"] .demo-icon,
.machine-skin .demo-icon { filter: invert(1); }
```

(`Icon`/`Logo` 等 `currentColor` 矢量图标随 `--text-primary` 自动变黄,无需处理。)

### 4.4 滚动条

```css
[data-theme="machine"] ::-webkit-scrollbar-thumb { background: var(--accent-primary); }
[data-theme="machine"] ::-webkit-scrollbar-track { background: var(--bg-base); }
```

## 5. 分级氛围机制

- **内容页(轻量)**:靠 §3 的 `--grid-line`/`--noise-opacity`,texture.css 自动出网格+噪点。无扫描线/CRT/暗角。
- **demo 页(全套)**:复用 `MachineSkin` 组件作为"全氛围提供者"(网格+扫描线+暗角+噪点+四角框+HUD 文字+可选视差)。
  - `Demo.tsx`:当 `slug === 'nexus'`(永远)**或** `theme === 'machine'` 时,用 `<MachineSkin>` 包裹内容。
  - `Learn.tsx`(也是 iframe 页):当 `theme === 'machine'` 时同样包裹。
- `MachineSkin` 内对调色板变量的覆盖**保留**——这正是 `/nexus` 在非 machine 主题下仍呈监控风的依据;machine 主题下该覆盖与全局变量同值,无副作用。

## 6. useTheme 跨组件实时同步(顺带修复)

现状:`useTheme` 每个调用各持独立 `useState`,NavBar 切主题时 `Demo`/`Learn` 实例不会实时更新 → 在 demo 页切到 machine 不会即时套全氛围。

修复(沿用 `useMotionPreference` 的事件同步模式):`setTheme` 写入后派发 `window` 事件 `ai-demos-theme-change`;hook 监听该事件与 `storage` 事件,实时同步所有实例的 `theme`。这样切主题全站(含 demo 包裹)即时生效。

## 7. 全局 HUD 角标(克制)

machine 主题选中时,在全站右下角显示一行极淡的版本/系统信息(`v{version} · MONITORING`),作为氛围点缀。实现:`App.tsx` 中按当前 `theme === 'machine'` 条件渲染一个 `fixed` 定位、`pointer-events:none`、低透明度的小组件 `GlobalHud`。demo 页 `MachineSkin` 内已有更丰富的 HUD 文字,二者不冲突(角落不同 / demo 页可只保留 MachineSkin 的)。

> 评审点:若觉得全局角标多余,可砍掉 §7,只保留 demo 页 MachineSkin 内的 HUD 文字。

## 8. 改动文件清单

| 文件 | 动作 |
|---|---|
| `src/hooks/useTheme.ts` | 加 `machine` 到类型/ALL_THEMES;加事件同步 |
| `src/components/ThemeToggle.tsx` | 加"监控"选项 |
| `src/styles/theme.css` | 加 `[data-theme="machine"]` 调色板 |
| `src/styles/machine-skin.css` | 细节规则扩展到 `[data-theme="machine"]`;加 `.hud-frame` 通用方括号、按钮直角、图标、滚动条 |
| `src/pages/Demo.tsx` | machine 主题时包裹 MachineSkin(nexus 仍永远包裹) |
| `src/pages/Learn.tsx` | machine 主题时包裹 MachineSkin |
| `src/components/MachineSkin.tsx` | (基本不变,作为全氛围提供者复用) |
| `src/components/WorkCard.tsx` | 加 `hud-frame` |
| `src/components/AnnouncementBoard.tsx` | 加 `hud-frame` |
| `src/components/DemoFrame.tsx` | 加 `hud-frame` |
| `src/components/SidebarLayout.tsx` | 加 `hud-frame` |
| `src/components/DemoInfoCard.tsx` | 把已有 `demo-info-card` 纳入 `hud-frame` 体系(或并加) |
| `src/pages/Me.tsx` | 各 section 卡加 `hud-frame` |
| `src/pages/Changelog.tsx` | 文章卡加 `hud-frame` |
| `src/components/GlobalHud.tsx` | 新增(§7,可选) |
| `src/App.tsx` | 渲染 GlobalHud(machine 时) |

## 9. 数据流

1. 用户在 NavBar 主题切换器点"监控" → `setTheme('machine')` → 写 `data-theme="machine"` 于 `<html>` + localStorage + 派发同步事件。
2. 全局:`[data-theme="machine"]` 调色板生效 → 所有组件自动变监控配色/等宽;texture.css 出网格+噪点;细节规则(直角/方括号/图标/滚动条)生效。
3. demo 页:`Demo`/`Learn` 的 `useTheme` 经事件同步更新 → 条件包裹 `MachineSkin` → 全氛围(扫描线/CRT/暗角/视差/HUD)。
4. 切回其他主题 → `data-theme` 改变 → machine 规则全部失效;`/nexus` 因 `slug==='nexus'` 仍保留 MachineSkin 监控外壳。

## 10. 验证

- 切到"监控"主题:首页/学习/更新/个人**全部**变监控配色 + 直角 + 卡片四角方括号 + 等宽 + 网格噪点;无扫描线/CRT(内容页可读)。
- demo 页(rag/fc/nexus/doctomd/iconforge/learn)在 machine 下有全氛围(扫描线/暗角/HUD)。
- 切回极简/浅色/深蓝/赛博:四个旧主题外观与改动前**完全一致**(machine 规则不渗漏);`/nexus` 仍为监控外壳。
- 切主题即时全站生效(含 demo 包裹),无需刷新。
- 圆点/开关旋钮/头像仍为圆形;按钮为直角。
- `npm run build` 通过无类型错误。

## 11. 回退

machine 是新增主题,不改旧主题与默认值。回退=移除 `machine` 注册 + 新增 CSS 块 + 组件标记类,其余功能零影响。

## 12. 后续(本阶段不做)

- 角色标签/更多 pill 是否方形化(留待按视觉反馈微调)。
- 主题相关的图片/插画资源适配(当前无)。
