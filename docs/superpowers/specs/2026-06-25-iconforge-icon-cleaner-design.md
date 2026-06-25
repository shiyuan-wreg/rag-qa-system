# IconForge 图标净化器 — 设计文档(spec)

> 日期:2026-06-25
> 状态:已与用户确认,待写实现计划
> 所属:ai-demos monorepo,第 6 个 web demo,路由 `/iconforge/`

---

## 1. 背景与动机

用户在为个人网站准备图标时反复遇到同一类麻烦:拿到的图标素材"脏"——
位图描摹(vectorize)生成的 SVG 把原图的白底和抗锯齿边描成了上千条近白色填充路径,
落到页面上表现为"白边裁剪污染";或者素材是 PNG/JPG 位图需要先转矢量;
或者是彩色 SVG 需要压成单色纯黑以适配黑白科技风主题。

本次(2026-06-25)在修门户作品卡图标时,临时写了一段 Python 脚本解决了"剥近白路径 +
紧贴 viewBox"的问题,效果一次到位。用户希望把这个流程固化成可复用工具,并集成进
ai-demos 网站,避免每次临时写脚本。

## 2. 目标(一句话)

提供一个**无状态的 web 工具**:浏览器上传一张图标(PNG/JPG / 脏 SVG / 彩色 SVG),
用户**自选**要执行的净化操作,实时预览(亮底/暗底对比)并下载干净的单色纯黑线稿 SVG。
既解决用户的真实痛点,也作为作品集里一个展示工程能力的 demo。

## 3. 非目标(YAGNI)

- 不做账号/登录/持久化存储(无状态,处理完即返回,不落盘)。
- 不做照片级图像的矢量化(potrace 适合 logo/图标这类高对比素材,不适合连续色调照片)。
- 不做批量文件夹处理(本期只做单文件上传;CLI/批处理留作后续)。
- 不做多色保留的矢量化(本期单色为主;彩色输入的"保留配色描摹"不在范围)。

## 4. 功能模型:三个可独立勾选的操作

不是写死的自动管道,而是三个**可独立勾选**的操作,由用户决定跑哪几个。
后端按固定顺序 A→B→C 依次施加被勾选的步骤。

| 操作 | 作用 | 适用输入 |
|---|---|---|
| **A. 位图转矢量** | PNG/JPG → SVG(Pillow 灰度 + 阈值二值化 → potrace 描摹为路径) | 仅位图 |
| **B. 去除白边** | 剥掉近白/背景填充路径,并重算紧贴内容的 viewBox | SVG(或 A 的产物) |
| **C. 彩色转黑色** | 所有填充/描边统一为纯黑 `#171817`(= `rgb(23,24,23)`) | SVG(或 A 的产物) |

### 选择逻辑约束

- 输入 **PNG/JPG**:A 可选且是前提;勾选 A 后,B、C 叠加作用在描摹结果上。
- 输入 **SVG**:A 自动置灰(不适用);B、C 各自独立勾选。
- 三个都不勾:等于不处理,前端拦截并提示。
- 顺序固定 **A→B→C**(描摹必须先于清洗/单色化),但每步是否执行由勾选决定。

### 典型用法映射

- 本次救火场景 = 勾 **B + C**。
- 纯位图转矢量 = 只勾 **A**。
- 从位图一步到干净图标 = **A + B + C** 全勾。

## 5. 架构

完全照搬现有 DocHub(`md_converter_app`)的接线模式,不引入任何新模式。
新增服务 `backends/iconforge_app/`,FastAPI,容器端口 **8005**,nginx 走 `/iconforge/`。
核心净化逻辑与 web/IO 解耦,放在纯函数模块里,便于单元测试。

```
backends/iconforge_app/
  main.py        FastAPI:POST /api/clean、首页、健康检查;挂载 static、模板
  cleaner.py     编排层:按勾选的 ops 顺序(A→B→C)依次调用 tracer/svgutil,纯函数
  svgutil.py     SVG 解析:路径提取、亮度取舍(去白边)、bbox 计算、viewBox 重写、单色化
  tracer.py      位图→矢量:Pillow 预处理(灰度 + Otsu 阈值二值化)→ potrace 子进程 → SVG
  models.py      请求/响应 Pydantic schema(CleanRequest ops/params、CleanResponse svg/stats/warnings)
  config.py      默认色 #171817、默认亮度阈值 120、padding 6%、最大上传大小
  static/        前端静态资源(JS/CSS,套 mono 主题)
  templates/     首页 HTML(Jinja2,单页)
  tests/         pytest 单元测试
  Dockerfile     python:3.12-slim,apt 安装 potrace
  requirements.txt   fastapi uvicorn pillow python-multipart jinja2
```

各模块单一职责:
- `svgutil`:只懂 SVG 文本 ↔ 路径/颜色/几何,不懂 HTTP、不懂位图。
- `tracer`:只懂位图 → SVG 字符串,不懂清洗规则。
- `cleaner`:只负责"按 ops 编排顺序",不实现具体算法。
- `main`:只负责 HTTP 边界(上传解析、错误码、返回 JSON)、托管前端。

## 6. 数据流 / API

无状态、单一端点:

```
POST /iconforge/api/clean        (multipart/form-data)
  file: <上传的图>                 必填
  ops:  ["trace","dewhite","mono"] 勾选的操作子集(顺序无关,后端按 A→B→C 重排)
  params(可选,JSON 或表单字段):
        color:      目标色,默认 "#171817"
        threshold:  去白边亮度阈值(0-255),默认 120(三通道均 > 阈值视为白/背景,丢弃)
        padding:    紧贴 viewBox 的留白比例,默认 0.06
        raster_threshold: 位图二值化阈值,默认 Otsu 自动
        invert:     位图是否反相(浅底深字 vs 深底浅字),默认 false

→ 200 JSON:
  {
    "svg":   "<清洗后的 SVG 字符串>",
    "stats": { "pathsKept": 6, "pathsDropped": 930,
               "bbox": [296, 313], "bytesIn": 169049, "bytesOut": 3070 },
    "warnings": []      // 例如 potrace 未安装、描摹质量低提示等
  }
```

- 后端 `cleaner.clean(file_bytes, filename, ops, params) -> CleanResult`,纯函数易单测。
- 前端拿到 `svg` 字符串后**本地渲染预览 + 触发下载**,服务端不落盘。
- 比 DocHub 更简单:无 store、无 auth、无 uploads/output 持久目录。

## 7. 前端 UI(套黑白 mono 主题,极简单页)

```
┌─────────────────────────────────────────────┐
│  IconForge 图标净化器          [06 / 上传图标]  │
│  ┌─────────────┐   勾选要执行的操作:           │
│  │  拖拽/点击    │   ☐ A 位图转矢量 (PNG/JPG)   │
│  │   上传区      │   ☑ B 去除白边               │
│  │  PNG JPG SVG │   ☑ C 彩色转黑色             │
│  └─────────────┘   ▸ 高级参数(亮度阈值/padding)│
│                     [ 净化 ]                  │
├─────────────────────────────────────────────┤
│  预览:  原图 │  结果(亮底) │  结果(暗底)        │
│  统计:  路径 936→6 · 169KB→3KB · bbox 296×313 │
│         [下载 SVG]  [复制 SVG 源码]            │
└─────────────────────────────────────────────┘
```

关键点:
- **结果同时在亮底与暗底各渲染一遍**——图标要上 mono-light / mono 两套主题,
  一眼判断反白后是否好看。
- 上传后按文件类型自动灰掉不适用的勾选(SVG 灰掉 A)。
- 高级参数默认折叠;普通用户不展开也能一次到位。

## 8. 错误处理

| 情况 | 处理 |
|---|---|
| 非图片 / MIME 不符 | 400,友好提示"请上传 PNG/JPG/SVG" |
| 文件超过大小上限 | 400,提示上限值 |
| 三个操作都没勾 | 前端拦截,不发请求 |
| 对 SVG 勾了 A(位图转矢量) | 后端忽略 A 并加 warning(A 不适用于矢量输入) |
| potrace 未安装 / 描摹失败 | 返回 warning,不崩溃;若 A 是唯一操作则返回 400 说明 |
| SVG 解析不出任何路径 | 提示"这不像可清洗的矢量图" |

## 9. 测试(pytest)

核心逻辑与 web 解耦,便于单测:

- `svgutil`:
  - 合成一个含"近白路径 + 深色路径"的 SVG → 断言去白边后近白路径被丢弃。
  - 断言 bbox 紧贴深色内容、viewBox 按 padding 重写。
  - 断言单色化把所有 fill/stroke 改成 `#171817`。
- `cleaner`:
  - ops 组合(仅 B / 仅 C / B+C / 空)各跑一遍,断言对应行为与顺序。
  - SVG 输入勾 A 时被忽略并产生 warning。
- `tracer`:
  - 有 potrace 时,拿一张 8×8 黑白 PNG 描摹,断言输出含 `<path`;
  - 未安装 potrace 则 `pytest.skip`。
- API 冒烟:`POST /api/clean` 上传一张小图,断言返回含 `svg` 与 `stats`。

## 10. 集成接线(照搬 DocHub 五处)

1. `backends/iconforge_app/Dockerfile` —— `apt-get install -y potrace`,装 Python 依赖。
2. `deploy/docker-compose.yml` —— 新增 `iconforge` 服务(`expose: ["8005"]`),
   加入 nginx 的 `depends_on`。
3. `deploy/nginx/nginx.conf` 与 `deploy/nginx/nginx.local.conf` —— 新增
   `location /iconforge/`,反代到 `http://iconforge:8005`,与 `/doctomd/` 同款写法。
4. `frontends/portfolio/src/data/works.ts` —— 新增第 6 张作品卡
   (编号 `06`,path `/iconforge`,配图标与 changelog)。
5. `frontends/portfolio/public/icons/iconforge.svg` —— **用本工具自己生产**
   (dogfooding:随便找张图标跑一遍工具,产物即其卡片图标;同时作为一次真实验收)。

## 11. 关键技术说明

- **去白边算法**(来自本次救火脚本,泛化):解析所有 `<path>`,读其 `fill` 的 rgb;
  三通道均 > 阈值(默认 120)视为白/背景予以丢弃,仅保留深色字形路径;
  从保留路径的 `d` 中提取全部坐标数对,取 min/max 得 bbox;按 padding 比例外扩后
  重写 `viewBox` 与 `width/height`,使字形紧贴显示框(解决"图标太小")。
- **单色化**:把保留路径的 `fill`/`stroke` 统一改为目标色;深色字形保持 `#171817`,
  从而在暗色主题下经 `.demo-icon { filter: invert(1) }` 正确反白。
- **位图→矢量**:Pillow 读图 → 转灰度 → (Otsu 或指定阈值)二值化 → 存为 PBM/BMP →
  `potrace -s`(SVG 输出)→ 得到单色路径 SVG;随后可继续走 B/C。

## 12. 已定决策

- 形态 = **Web demo**(用户在 2026-06-25 确认;CLI/批处理留作后续,不在本期)。
- 功能 = **三个可独立勾选的操作**(A 位图转矢量 / B 去除白边 / C 彩色转黑色),
  非强制自动管道(用户明确要求"让用户自己选择")。
- 顺序固定 A→B→C;无状态、不落盘、无账号。
- 接线 100% 照搬 DocHub(`md_converter_app`)模式,端口 8005,路由 `/iconforge/`。
- 自身卡片图标用本工具 dogfooding 生产。
