# Kairos RAG 数据工程化设计文档

> 设计日期：2026-07-09  
> 目标读者：代码/系统（同时配套学习文档 `docs/learning/rag-data-engineering-basics.md`）  
> 关联需求：把 Kairos RAG 从“能跑的 demo”升级到“经得起追问的数据工程系统”，本阶段聚焦**数据清洗 + 元数据增强**（对应《RAG 七连问》第 1-4 问）。

---

## 1. 当前问题

现有 RAG 流程（`core/rag_tool.py`）只有四步：

```
load_documents → split_documents → get_or_create_vectorstore → retrieve
```

缺陷：
- 只支持单个文件，无法批量加载目录。
- 没有数据清洗：重复页眉页脚、短碎片、低质量内容直接入库。
- 没有元数据：每个 chunk 只有 `source` 文件名，没有章节、关键词、实体、质量分。
- 检索时不做质量过滤，垃圾片段会污染生成结果。

这些缺失导致 RAG 回答质量不稳定，也无法向面试官解释“你的 RAG 到底做了哪些工程化工作”。

---

## 2. 设计目标

本阶段完成后，RAG 建库流程变为：

```
加载目录 → 文档去重 → 文本切分 → chunk 级清洗/质量评分 → 元数据增强 → 入库 → 带过滤的检索
```

具体交付：
- `rag/loader.py`：支持目录/多文件批量加载（`.txt`、`.md`、`.pdf`）。
- `rag/cleaner.py`：文档级去重、chunk 级噪声过滤、质量评分。
- `rag/enricher.py`：章节、关键词、实体、摘要、文档类型、入库时间。
- `rag/splitter.py`：保留并继承 metadata 到每个 chunk。
- `rag/retriever.py`：支持按 `quality_score` 过滤检索。
- `core/rag_tool.py`： orchestration 新流程。
- `tests/test_rag_cleaner.py`、`tests/test_rag_enricher.py`：单元测试。
- `docs/learning/rag-data-engineering-basics.md`：配套零基础学习文档。

---

## 3. 数据流与模块职责

```
                  ┌─────────────────┐
                  │  rag/loader.py  │  加载目录/多文件
                  └────────┬────────┘
                           │ Document list
                           ▼
                  ┌─────────────────┐
                  │  rag/cleaner.py │  文档去重
                  │  deduplicate()  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  rag/splitter.py│  按章节/长度切分
                  │ split_documents │
                  └────────┬────────┘
                           │ Chunk list
                           ▼
                  ┌─────────────────┐
                  │  rag/cleaner.py │  噪声过滤、质量评分
                  │ clean_chunks()  │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ rag/enricher.py │  关键词、实体、摘要、章节
                  │ enrich_chunks() │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │rag/vectorstore.py│  嵌入 + Chroma 存储
                  └─────────────────┘
```

---

## 4. 关键设计决策

### 4.1 清洗放在切分之后做 chunk 级

原因：
- 文档级去重（重复 PDF/文件）放在切分前，避免重复计算。
- 页眉页脚、短碎片等噪声只有在切分后才能识别。
- 质量评分依赖 chunk 本身的信息密度，必须在切分后计算。

### 4.2 元数据增强同时支持 LLM 和启发式两种模式

原因：
- LLM 抽取关键词/实体/摘要效果好，但增加成本和启动时间。
- 启发式方法（正则、词频、章节解析）不依赖外部调用，适合本地快速验证。
- 默认优先 LLM；LLM 不可用时自动降级到启发式，保证系统不挂。

### 4.3 章节信息从 Markdown 标题解析

原因：
- Kairos 现有的文档主要是 `.md`（学习文档、指南）。
- PDF 标题解析复杂，本阶段用文件名作为 fallback section。
- 后续可扩展 PDF 书签/版面分析。

### 4.4 检索时过滤 `quality_score < 0.5` 的 chunk

原因：
- 低质量 chunk（页眉页脚、短碎片、乱码）即使语义相似也会误导模型。
- 0.5 是经验阈值，后续可通过 eval 调整。

---

## 5. 模块详细设计

### 5.1 `rag/loader.py`

新增 `load_directory(path)`：
- 递归遍历目录。
- 按后缀选择 loader：`.txt`/`.md` → `TextLoader`；`.pdf` → `PyPDFLoader`。
- 返回 `List[Document]`，每个 Document 的 `metadata.source` 为相对路径。
- 保持 `load_documents(path)` 兼容单文件。

### 5.2 `rag/cleaner.py`

#### 5.2.1 文档级去重 `deduplicate_documents(docs)`
- 计算每个文档 `page_content` 的 MD5（去除首尾空白、统一换行）。
- MD5 相同视为精确重复，只保留第一个。
- 对于近似重复，使用 `difflib.SequenceMatcher` 快速比率 > 0.85 判定，保留来源更权威/更新的一个。

#### 5.2.2 Chunk 级清洗 `clean_chunks(chunks)`
- **长度过滤**：`len(page_content.strip()) < 30` 直接丢弃。
- **信息密度过滤**：计算有效字符（CJK、字母、数字、常见标点）占总字符比例，低于 0.4 丢弃。
- **重复噪声过滤**：统计每个 chunk 在所有 chunk 中的出现次数或高度相似次数；出现频率 > 30% 的视为页眉页脚，丢弃。
- **质量评分**：
  - `info_density`：有效字符比例。
  - `completeness`：chunk 是否以句末标点结尾（是则 1.0，否则 0.6）。
  - `quality_score = 0.6 * info_density + 0.4 * completeness`。
- 在 `metadata` 中写入 `info_density`、`completeness`、`quality_score`。

### 5.3 `rag/enricher.py`

#### 5.3.1 章节提取 `extract_section(docs)`
- 对 Markdown 文件，解析 `# `、`## `、`### ` 标题。
- 记录每个标题在文档中的字符位置。
- 切分后根据 chunk 起始位置找到最近的前置标题，作为 `section`。
- 非 Markdown 文件，`section` = "未分类" 或文件名。

#### 5.3.2 LLM 元数据抽取 `enrich_with_llm(chunks)`
- 将 chunks 分批（每批最多 10 个）。
- 调用 `core.llm.LLMClient` 抽取每个 chunk 的 `keywords`、`entities`、`summary`。
- Prompt 要求返回固定 JSON 格式。
- 失败时自动降级：keywords 用简单词频，entities 为空列表，summary 取前 20 字。

#### 5.3.3 启发式降级
- `keywords`：按空格/标点分词，过滤停用词，取频率最高的 5 个。
- `entities`：使用正则匹配版本号、技术名词（如 `Python 3.x`、`Spring Boot`）作为 fallback。
- `summary`：取 chunk 第一句或前 30 字。

#### 5.3.4 统一写入 metadata
- `source`：文件相对路径（已有）。
- `doc_type`：`markdown` / `text` / `pdf`。
- `section`：章节标题。
- `keywords`：关键词列表。
- `entities`：实体列表。
- `summary`：一句话摘要。
- `ingest_time`：ISO 格式时间。
- `quality_score`：来自 cleaner。

### 5.4 `rag/splitter.py`

- 保持 `RecursiveCharacterTextSplitter`。
- 确保每个切分后的 chunk 继承父文档的 metadata。
- 后续可扩展为 MarkdownHeaderTextSplitter，先做章节切分再做长度切分。

### 5.5 `rag/retriever.py`

- `retrieve(vectorstore, query, k=3, min_quality_score=0.5)`。
- 使用 Chroma 的 `where` 过滤：`{"quality_score": {"$gte": min_quality_score}}`。
- 返回 filtered 结果。

### 5.6 `core/rag_tool.py`

更新 `_init_vectorstore()` 流程：

```python
raw_docs = load_directory(self.docs_path)  # 支持目录
deduped_docs = deduplicate_documents(raw_docs)
chunks = split_documents(deduped_docs)
cleaned_chunks = clean_chunks(chunks)
enriched_chunks = enrich_chunks(cleaned_chunks)
self.vectorstore = get_or_create_vectorstore(enriched_chunks, ...)
```

更新 `format_retrieved()`：
- 显示 `section`、关键词、来源。
- 保留引用 `[1]`、`[2]`。

### 5.7 `core/agent.py`

System prompt 增加：
- “检索结果包含章节、关键词、摘要等元数据，可用来判断片段是否真正相关。”
- “如果多个 chunk 内容冲突，优先参考质量分高、来源权威的片段。”

---

## 6. 数据结构与示例

清洗并增强后的 chunk metadata 示例：

```json
{
  "source": "docs/learning/python-basics.md",
  "doc_type": "markdown",
  "section": "3. 函数与模块",
  "keywords": ["函数", "def", "模块", "import"],
  "entities": ["Python"],
  "summary": "介绍 Python 函数的定义方式和模块导入机制。",
  "info_density": 0.87,
  "completeness": 1.0,
  "quality_score": 0.92,
  "ingest_time": "2026-07-09T12:00:00Z"
}
```

---

## 7. 验证计划

### 7.1 单元测试

- `test_rag_cleaner.py`：
  - 精确重复文档只保留一份。
  - 短碎片被过滤。
  - 页眉页脚重复内容被过滤。
  - `quality_score` 在 0-1 之间。
- `test_rag_enricher.py`：
  - Markdown 标题解析正确。
  - LLM 模式可抽取 keywords/entities/summary。
  - 降级模式不崩溃。
- `test_rag_tool.py`：
  - 新 pipeline 初始化成功。
  - 检索结果包含 metadata。

### 7.2 端到端验证

- 使用 `docs/learning/` 目录建库。
- 查询 `"Python 函数怎么定义"`。
- 预期：返回的 chunk 带 `section`、`keywords`、`quality_score`，且低质量片段被过滤。

### 7.3 可观察指标

- 清洗前后 chunk 数量变化。
- 平均 `quality_score` 变化。
- 检索结果中是否出现页眉页脚类内容。

---

## 8. 风险与规避

| 风险 | 规避 |
|---|---|
| LLM 抽取增加启动时间和成本 | 可配置开关 `RAG_ENRICH_WITH_LLM=0` 关闭；批量调用；失败自动降级 |
| Markdown 标题解析不准 | 先用简单正则，后续可换成熟 parser；非 Markdown fallback |
| 质量阈值 0.5 可能误杀 | 通过 eval 数据调整；先保留日志可观察 |
| Chroma metadata filter 语法兼容 | 用标准 `where` 字典；单元测试覆盖 |

---

## 9. 后续阶段（本阶段不实现，仅预留接口）

- PDF 表格/图片抽取（第 3 问深化）。
- 增量更新与 embedding 版本管理（第 5 问）。
- 冲突检测与消解（第 6 问）。
- 文档版本控制、审核、回滚（第 7 问）。

本阶段先把第 1-4 问的地基打扎实，后续阶段才有地方接。

---

## 10. 文件变更清单

| 文件 | 动作 | 说明 |
|---|---|---|
| `rag/loader.py` | 修改 | 支持目录批量加载 |
| `rag/cleaner.py` | 新增 | 去重、噪声过滤、质量评分 |
| `rag/enricher.py` | 新增 | 章节、关键词、实体、摘要 |
| `rag/splitter.py` | 修改 | 保留 metadata |
| `rag/retriever.py` | 修改 | 支持 quality_score 过滤 |
| `core/rag_tool.py` | 修改 |  orchestration 新流程 |
| `core/agent.py` | 修改 | system prompt 增加元数据使用说明 |
| `tests/test_rag_cleaner.py` | 新增 | cleaner 单元测试 |
| `tests/test_rag_enricher.py` | 新增 | enricher 单元测试 |
| `tests/test_rag_tool.py` | 修改 | 覆盖新 pipeline |
| `docs/learning/rag-data-engineering-basics.md` | 新增 | 配套学习文档 |
| `docs/superpowers/specs/2026-07-09-rag-data-engineering-design.md` | 新增 | 本文件 |
| `docs/PROJECT-STATE.md` | 修改 | 更新 RAG 阶段状态 |
| `docs/dev-log.md` | 修改 | 记录本阶段工作 |
| `docs/session-log.md` | 修改 | 记录本阶段工作 |
