# DocHub Markdown 文档站设计文档

- **文档日期**：2026-06-23
- **项目**：ai-demos
- **服务名**：DocHub（暂定）
- **定位**：把 Markdown 文集一键转换成可浏览的 HTML 文档站
- **设计状态**：待实现

---

## 1. 写在最前面

### 1.1 这个服务解决什么问题

当前 `C:\Users\hzs17\Desktop\md_to_html.py` 能把 Markdown 批量转成 HTML，但存在几个问题：

1. **使用不便**：必须打开命令行，手动指定路径。
2. **目录分散**：每次转换只生成当前目录的索引，没有全局总目录把多次转换结果汇总起来。
3. **无法在线浏览**：生成的 HTML 是静态文件，浏览时要手动找文件路径。
4. **没有访问控制**：如果部署到公网，任何人都能使用。

DocHub 的目标是把上述流程 Web 化，并集成进 ai-demos。

### 1.2 设计边界

**Phase 1 包含**：
- Web 上传单个 `.md` 文件转换
- Web 输入本地目录路径批量转换
- 生成全局总目录 + 子目录索引
- 在线浏览转换结果
- 简单密码登录保护
- 保留命令行用法
- 集成进 ai-demos（docker-compose + nginx + portfolio）

**Phase 1 不包含**：
- zip 上传解压（后续可添加）
- 多用户/复杂权限
- 数据库持久化（使用文件系统 + 内存 session）
- 实时协作编辑

---

## 2. 关键术语解释

| 术语 | 解释 |
|---|---|
| Markdown | 一种轻量级标记语言，用简单符号表示标题、列表、代码块等，适合写文档。 |
| HTML | 网页标记语言，浏览器能直接渲染。 |
| FastAPI | Python Web 框架，用于构建后端 API 和 Web 页面。 |
| Jinja2 | Python 模板引擎，用来把数据和 HTML 模板结合生成页面。 |
| Session | 服务器记住用户登录状态的机制，通常通过 cookie 实现。 |
| 反向代理 | 对外暴露统一入口，根据路径把请求转发给内部不同服务的程序（如 nginx）。 |

如果这些基础概念不熟悉，可以先看 `docs/learning/nexus-prerequisites-web-backend.md`。

---

## 3. 集成架构

### 3.1 服务边界

```
浏览器
  │
  ▼
nginx (80/443)
  ├── /          → frontends/portfolio (静态门户)
  ├── /rag/      → backends/rag_app:8001
  ├── /fc/       → backends/fc_app:8002
  ├── /nexus/    → backends/nexus_app:8003
  └── /doctomd/       → backends/md_converter_app:8004  ← 新增
```

### 3.2 目录结构

```
backends/md_converter_app/
├── main.py              # FastAPI 入口
├── cli.py               # 保留的命令行入口
├── converter.py         # 转换核心（重构 md_to_html.py）
├── auth.py              # 简单认证
├── models.py            # 数据模型（Job、Session 等）
├── templates/           # Jinja2 HTML 模板
│   ├── base.html
│   ├── index.html       # 总目录页
│   ├── dir_index.html   # 子目录索引页
│   ├── login.html
│   └── home.html
├── static/              # CSS/JS
├── output/              # 转换结果输出目录
│   ├── index.html       # 全局总目录
│   ├── uploads/         # 上传文件转换结果
│   └── paths/           # 本地路径转换结果
├── uploads/             # 上传临时目录
├── requirements.txt
└── Dockerfile
```

---

## 4. 后端设计

### 4.1 接口清单

| 接口 | 方法 | 认证 | 说明 |
|---|---|---|---|
| `/` | GET | 可选 | 服务首页/说明 |
| `/login` | GET/POST | 不需要 | 登录页 |
| `/logout` | POST | 需要 | 退出登录 |
| `/api/convert/upload` | POST | 需要 | 上传单个 `.md` 文件转换 |
| `/api/convert/path` | POST | 需要 | 指定本地目录路径转换 |
| `/api/jobs` | GET | 需要 | 查看转换任务列表 |
| `/api/jobs/{id}` | GET | 需要 | 查看任务详情 |
| `/api/jobs/{id}/download` | GET | 需要 | 下载转换结果 zip（Phase 2） |
| `/browse/` | GET | 需要 | 全局总目录页 |
| `/browse/{path}` | GET | 需要 | 浏览具体 HTML 页面 |

### 4.2 转换流程

```
用户提交转换请求
    │
    ▼
创建 Job（生成 job_id、记录时间、来源类型）
    │
    ▼
扫描/读取 Markdown 文件
    │
    ├── 上传文件：保存到 uploads/{job_id}/，解压/读取
    └── 本地路径：扫描指定目录下所有 .md
    │
    ▼
逐个调用 converter.py 生成 HTML
    │
    ▼
生成子目录索引 index.html
    │
    ▼
更新全局总目录 output/index.html
    │
    ▼
返回 job_id，前端跳转 /browse/
```

### 4.3 转换核心（converter.py）

复用现有 `md_to_html.py` 的核心逻辑，但做以下调整：

- 抽离为函数，不直接操作命令行参数。
- 支持指定输出目录。
- 支持生成全局总目录。
- HTML 模板使用 Jinja2，方便扩展。

核心函数签名：

```python
def convert_markdown_file(md_path: Path, out_path: Path, index_link: str = "") -> None

def build_dir_index(directory: Path, html_files: list[Path], root: Path) -> None

def build_global_index(output_root: Path) -> None

def convert_directory(src_dir: Path, out_dir: Path, job_id: str) -> list[Path]
```

### 4.4 全局总目录设计

全局总目录页 `output/index.html` 展示所有转换过的文集，按来源分类：

```html
<h1>DocHub 文档总目录</h1>

<h2>上传的文档</h2>
<ul>
  <li><a href="uploads/job-xxx/index.html">job-xxx（2026-06-23）</a></li>
</ul>

<h2>本地路径转换</h2>
<ul>
  <li><a href="paths/job-yyy/index.html">job-yyy - ai-demos/docs</a></li>
</ul>
```

每次转换完成后调用 `build_global_index` 更新该页面。

### 4.5 Job 模型

```python
class ConversionJob:
    job_id: str
    source_type: str  # "upload" 或 "path"
    source_name: str  # 文件名或路径名
    status: str       # pending / running / done / error
    created_at: str
    output_dir: Path
    error_message: str = ""
```

Job 列表保存在内存中，服务重启后丢失（Phase 1 可接受）。

---

## 5. 前端设计

### 5.1 页面结构

| 页面 | 说明 |
|---|---|
| `/login` | 密码登录页 |
| `/`（登录后） | 转换控制台：上传文件、输入路径、历史任务列表 |
| `/browse/` | 全局总目录 |
| `/browse/{path}` | 单个 HTML 文档浏览页 |

### 5.2 首页（登录后）布局

```
+------------------------------------------+
|  DocHub - Markdown 文档站                |
+------------------------------------------+
|  [上传 Markdown 文件]  [输入本地路径]     |
|  --------------------------------------  |
|  最近转换任务                             |
|  - job-xxx  上传  2026-06-23  [浏览]     |
|  - job-yyy  路径  2026-06-23  [浏览]     |
+------------------------------------------+
```

### 5.3 样式

与现有 ai-demos demo（rag/fc/nexus）保持一致：
- 简洁现代风格
- 支持明暗主题（`prefers-color-scheme`）
- 响应式布局

---

## 6. 认证与权限

### 6.1 实现方式

使用基于 starlette-session 或自定义 cookie 的简单认证：

1. 密码存储在 `.env` 的 `DOCHUB_PASSWORD`。
2. 用户访问 `/login` 输入密码。
3. 密码正确后，服务器写入加密的 session cookie。
4. 受保护接口检查 session，未登录则重定向到 `/login`。
5. `/logout` 清除 cookie。

### 6.2 命令行用法保留

`cli.py` 保留原脚本功能，支持：

```bash
python cli.py C:/Users/hzs17/Desktop/notes -o C:/Users/hzs17/Desktop/output
```

命令行转换不经过 Web 认证，直接操作文件系统，适合本地批量处理。

### 6.3 与 ai-demos 其他服务的权限关系

你提到希望"所有功能仅对我个人开放"。本次设计先把权限做在 DocHub 内部。未来可以把 `auth.py` 中的认证逻辑抽成公共中间件，供 rag/fc/nexus 复用，实现全局权限控制。

---

## 7. 部署集成

### 7.1 Dockerfile

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY backends/md_converter_app/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backends/md_converter_app/ ./
EXPOSE 8004
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]
```

### 7.2 docker-compose.yml 新增

```yaml
md_converter:
  build:
    context: ..
    dockerfile: backends/md_converter_app/Dockerfile
  env_file: ../.env
  restart: always
  expose: ["8004"]
  volumes:
    - ../backends/md_converter_app/output:/app/output
    - ../backends/md_converter_app/uploads:/app/uploads
```

### 7.3 nginx 新增 location

```nginx
location /doctomd/ {
    proxy_pass http://md_converter:8004/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### 7.4 portfolio 集成

在 `frontends/portfolio/src/data/works.ts` 新增：

```typescript
{ slug: 'md', title: 'DocHub Markdown 文档站', desc: '把 Markdown 文集一键转成可浏览的 HTML 文档站。',
  tech: ['FastAPI', 'Markdown', 'Jinja2'], path: '/doctomd' }
```

在 `App.tsx` 路由中新增 `/doctomd` → `<DemoFrame work={...} src="/doctomd/" />`。

---

## 8. 安全考虑

| 风险 | 缓解措施 |
|---|---|
| 任意文件上传 | 限制上传类型为 `.md`，禁止可执行文件。 |
| 任意本地路径读取 | 通过 `.env` 开关 `DOCHUB_ALLOW_PATH_CONVERT` 控制，生产环境可关闭路径转换功能。 |
| 路径遍历 | 对用户提供的路径做校验，禁止 `../` 和绝对路径越狱。 |
| 上传文件过大 | 限制单文件大小（如 10MB）。 |
| 未授权访问 | 所有转换/浏览接口需要登录。 |
| 命令行与 Web 冲突 | 命令行直接写文件系统，Web 端读取 `output/` 目录；设计时避免同时写同一文件。 |

---

## 9. 测试策略

| 测试文件 | 覆盖内容 |
|---|---|
| `tests/test_converter.py` | Markdown 转 HTML、目录索引生成、全局总目录生成 |
| `tests/test_upload.py` | 文件上传 API、非法文件类型拒绝 |
| `tests/test_path_convert.py` | 本地路径转换、路径遍历防护 |
| `tests/test_auth.py` | 登录/未登录访问控制 |
| `tests/test_index.py` | 总目录页和子目录页可访问 |

---

## 10. 实现阶段（Phase 1 内部）

### 10.1 阶段 1.1：转换核心重构
- 把 `md_to_html.py` 拆成 `converter.py`。
- 支持指定输出目录和生成全局总目录。
- 保留 `cli.py` 命令行用法。

### 10.2 阶段 1.2：FastAPI Web 后端
- 实现上传转换、路径转换接口。
- 实现 Job 内存管理。
- 实现 `/browse/` 浏览。

### 10.3 阶段 1.3：认证与前端
- 实现登录/session。
- 实现首页、登录页、浏览页模板。

### 10.4 阶段 1.4：ai-demos 集成
- Dockerfile、docker-compose、nginx、portfolio 集成。
- 端到端验证。

---

## 11. 风险与权衡

| 风险 | 影响 | 缓解措施 |
|---|---|---|
| 路径转换在生产环境有安全风险 | 高 | 默认关闭路径转换，或限制可访问目录 |
| 上传文件导致磁盘占满 | 中 | 限制单文件大小和总容量，定期清理 |
| 与现有 md_to_html.py 功能重复 | 低 | 新服务完全替代旧脚本，旧脚本可删除或保留为 cli.py |
| 权限中间件未来迁移成本 | 中 | 认证逻辑单独放 `auth.py`，便于复用 |

---

## 12. 下一步

1. 用户审查并批准本设计文档。
2. 使用 `superpowers:writing-plans` 制定详细实现计划。
3. 按阶段 1.1 开始编码。
