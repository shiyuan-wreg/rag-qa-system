# RAG 数据工程零基础入门

> 目标：理解为什么 RAG 不能只靠“加载→切分→嵌入→检索”四步，学会数据清洗和元数据增强这两个最基础也最重要的工程化环节，并能看懂 Kairos 里对应的实现。

---

## 1. 一句话定义

RAG 数据工程 = **把原始文档变成“干净、有结构、可追溯”的知识片段**，让向量检索和 LLM 生成建立在高质量数据上，而不是垃圾数据上。

---

## 2. 为什么需要数据工程

一个最常见的 demo 级 RAG 流程是这样的：

```
读 PDF → 切 chunk → 嵌入 → 存向量库 → 检索 → 让 LLM 回答
```

这个流程能跑通，但一到真实场景就会暴露出三类问题：

### 2.1 数据脏

PDF 里不只有正文，还有页眉、页脚、目录页、空白页、页码。HTML 里还有导航栏、广告、Cookie 提示。如果你不过滤，这些碎片也会被切成 chunk 入库。用户问“报销流程是什么”，检索结果可能第一条是“第 3 页”，第二条是页脚的版权声明。

### 2.2 数据重复

同一个知识点可能在三份文档里都出现，描述略有不同。全入库后，检索时三条都召回，LLM 拼在一起可能自相矛盾。例如一份是 2024 年的旧流程，一份是 2025 年的新流程，模型随机选一个，回答就错了。

### 2.3 没有上下文信息

每个 chunk 只知道“我从哪个文件来”。它不知道自己在哪个章节、关键词是什么、实体是谁、质量高不高。LLM 拿到片段后无法判断：这段内容权威吗？和另一段冲突吗？是不是页眉噪声？

**结果就是：垃圾进，垃圾出。**  Embedding 模型再先进，也救不了低质量数据。

---

## 3. 最小动手示例

假设你有一份 Markdown 文档：

```markdown
# Python 基础

## 1. 变量

变量是存储数据的容器。

---

页眉：Kairos 学习文档

## 2. 函数

def hello():
    print("hello")
```

### 3.1 没有数据工程的切分结果

```python
chunks = [
    "# Python 基础\n\n## 1. 变量",
    "变量是存储数据的容器。",
    "---",
    "页眉：Kairos 学习文档",
    "## 2. 函数",
    "def hello():\n    print(\"hello\")"
]
```

问题：
- `---` 是分隔线，没有语义，却被切成一个 chunk。
- `页眉：Kairos 学习文档` 重复出现，没有价值。
- 每个 chunk 都不知道自己属于哪个章节。

### 3.2 有数据工程的切分结果

```python
chunks = [
    {
        "content": "变量是存储数据的容器。",
        "section": "1. 变量",
        "keywords": ["变量"],
        "quality_score": 0.95
    },
    {
        "content": "def hello():\n    print(\"hello\")",
        "section": "2. 函数",
        "keywords": ["函数", "def"],
        "quality_score": 0.92
    }
]
```

变化：
- 分隔线和页眉被过滤掉了。
- 每个 chunk 都知道自己属于哪个章节。
- 有了质量分，检索时可以优先召回高质量片段。

---

## 4. 核心概念

### 4.1 数据清洗

数据清洗不是“删掉一点东西”这么简单，它是一套 pipeline：

#### 4.1.1 去重

**文档级去重**：同一个 PDF 被上传了两遍，只保留一份。做法是对文件内容算 MD5，MD5 相同就认为是同一个文件。

**近似去重**：同一个知识点在两份文档里描述略有不同。做法是对文本算 SimHash 或 MinHash，海明距离小于阈值就判定为近似重复，保留来源更权威的那份。

#### 4.1.2 噪声过滤

常见的噪声：
- 长度太短的 chunk（低于 30 字，大概率是页眉页脚）。
- 有效字符比例太低的 chunk（全是符号、乱码、URL）。
- 在多个页面重复出现的固定文本（页眉页脚、版权声明）。

过滤策略：
- 基于规则：长度阈值、有效字符比例、重复频率。
- 基于模型：用轻量分类模型判断 chunk 是不是“实质内容”。

#### 4.1.3 质量评分

给每个 chunk 打一个质量分，维度包括：
- **信息密度**：有效字符占总字符比例。
- **语义完整性**：是否以句末标点结尾，是否表达了一个完整意思。
- **来源权威性**：官方文档 > 内部 Wiki > 个人笔记。

质量分不是二元的“好/坏”，而是 0-1 之间的连续值。检索时可以设定阈值，比如只召回 `quality_score >= 0.5` 的 chunk。

### 4.2 元数据增强

元数据 = chunk 的“身份证”。除了 `source` 文件名，还应该包含：

| 元数据 | 作用 |
|---|---|
| `section` | 章节标题，帮助 LLM 理解上下文 |
| `keywords` | 关键词，辅助检索和相关性判断 |
| `entities` | 实体（产品名、版本号、技术名词），帮助精准匹配 |
| `summary` | 一句话摘要，快速判断片段主题 |
| `doc_type` | 文档类型（markdown / text / pdf），不同类型处理策略不同 |
| `ingest_time` | 入库时间，支持增量更新和版本管理 |
| `quality_score` | 质量分，检索时过滤和排序 |

元数据增强有两种实现方式：
- **启发式**：用正则、词频、标题解析提取，速度快、无成本，但精度有限。
- **LLM 抽取**：让模型从 chunk 中抽取关键词、实体、摘要，精度高，但有成本和延迟。

生产环境中通常两者结合：能规则提取的用规则，复杂的用 LLM，LLM 失败时自动降级到规则。

---

## 5. Kairos 项目实例

本阶段 Kairos 在 `rag/` 下新增了三个模块，把原来的四步流程扩展为七步：

```
加载目录 → 文档去重 → 切分 → chunk 清洗/评分 → 元数据增强 → 嵌入 → 带过滤的检索
```

### 5.1 加载目录：`rag/loader.py`

原来只能加载单个文件：

```python
def load_documents(path: str):
    if path.endswith(".txt"):
        loader = TextLoader(path, encoding="utf-8")
    elif path.endswith(".pdf"):
        loader = PyPDFLoader(path)
    return loader.load()
```

现在支持加载整个目录：

```python
def load_directory(path: str) -> list:
    """递归加载目录下的 .txt / .md / .pdf 文件。"""
    docs = []
    for root, _, files in os.walk(path):
        for f in sorted(files):
            if f.endswith((".txt", ".md", ".pdf")):
                docs.extend(load_documents(os.path.join(root, f)))
    return docs
```

为什么需要批量加载？因为真实知识库不可能只有一份文件。

### 5.2 数据清洗：`rag/cleaner.py`

```python
def clean_chunks(chunks):
    """过滤噪声并计算质量分。"""
    result = []
    for chunk in chunks:
        text = chunk.page_content.strip()
        # 1. 长度过滤
        if len(text) < 30:
            continue
        # 2. 信息密度过滤
        density = compute_info_density(text)
        if density < 0.4:
            continue
        # 3. 质量评分
        chunk.metadata["info_density"] = density
        chunk.metadata["completeness"] = 1.0 if text[-1] in "。！？.!?" else 0.6
        chunk.metadata["quality_score"] = 0.6 * density + 0.4 * chunk.metadata["completeness"]
        result.append(chunk)
    return result
```

`compute_info_density` 计算有效字符比例：CJK 汉字、英文字母、数字、常见标点都算有效，HTML 标签、乱码符号不算。

### 5.3 元数据增强：`rag/enricher.py`

章节提取示例（Markdown）：

```python
def extract_section(markdown_text: str, chunk_start: int) -> str:
    """根据 chunk 在原文中的起始位置，找到最近的前置标题。"""
    headings = []
    for m in re.finditer(r"^(#{1,6})\s+(.+)$", markdown_text, re.M):
        headings.append((m.start(), m.group(2)))
    # 找最近的前置标题
    section = "未分类"
    for pos, title in headings:
        if pos <= chunk_start:
            section = title
        else:
            break
    return section
```

关键词/实体抽取示例（LLM 模式）：

```python
def enrich_with_llm(chunks):
    """调用 LLM 批量抽取 keywords、entities、summary。"""
    prompt = """对以下每个文本片段，抽取 keywords（3-5 个）、entities（重要实体）、summary（一句话摘要）。
返回 JSON 格式：{"results": [{"keywords": [...], "entities": [...], "summary": "..."}, ...]}
"""
    # 批量调用 core.llm.LLMClient
    # 解析 JSON 后写回 chunk.metadata
```

如果 LLM 不可用，自动降级到启发式：
- `keywords`：按词频取前 5。
- `entities`：正则匹配版本号、技术名词。
- `summary`：取 chunk 第一句或前 30 字。

### 5.4 检索过滤：`rag/retriever.py`

```python
def retrieve(vectorstore, query: str, k: int = 3, min_quality_score: float = 0.5):
    return vectorstore.similarity_search(
        query,
        k=k,
        filter={"quality_score": {"$gte": min_quality_score}}
    )
```

`filter` 是 Chroma 的 where 语法，只召回质量分大于等于 0.5 的 chunk。

### 5.5 流程串联：`core/rag_tool.py`

```python
def _init_vectorstore(self):
    raw_docs = load_directory(self.docs_path)
    deduped_docs = deduplicate_documents(raw_docs)
    chunks = split_documents(deduped_docs)
    cleaned_chunks = clean_chunks(chunks)
    enriched_chunks = enrich_chunks(cleaned_chunks)
    self.vectorstore = get_or_create_vectorstore(enriched_chunks, ...)
```

---

## 6. 常见错误与排查

| 错误/现象 | 可能原因 | 解决方法 |
|---|---|---|
| 检索结果里出现“第 3 页”“版权声明” | 页眉页脚没过滤 | 调低重复频率阈值，或增加页眉页脚规则 |
| 同一个问题召回三条几乎一样的内容 | 去重没做好 | 引入 SimHash/MinHash 近似去重 |
| 检索结果变少了 | quality_score 阈值太高 | 降低阈值，或检查清洗逻辑是否误杀 |
| LLM 抽取失败，元数据为空 | API key 或网络问题 | 检查是否自动降级到启发式 |
| Markdown 章节解析错误 | 标题格式不统一 | 规范标题写法，或增强 parser |

---

## 7. 常见面试问法

1. **“你的 RAG 数据清洗做了哪些工作？”**
   - 答：文档级去重、chunk 级噪声过滤、质量评分。具体包括 MD5 精确去重、SimHash 近似去重、长度/信息密度过滤、页眉页脚频率检测、质量分计算。

2. **“你怎么判断一个 chunk 是不是噪声？”**
   - 答：多个维度：长度是否过短、有效字符比例是否过低、是否在多个文档中重复出现、是否包含大量无意义符号。

3. **“元数据增强有什么用？”**
   - 答：让 chunk 有上下文。`section` 帮助定位章节，`keywords` 和 `entities` 帮助精准检索和冲突判断，`quality_score` 帮助过滤低质量片段，`ingest_time` 支持增量更新。

4. **“LLM 抽取元数据成本高怎么办？”**
   - 答：批量调用、失败自动降级到启发式、用规则能解决的问题不调用 LLM、只在入库时调用一次。

5. **“如果不同文档内容冲突了怎么办？”**
   - 答：本阶段先把来源权威性、时间、章节等元数据打全。下一阶段可以做冲突检测：语义相似但关键实体不同，判定为冲突；然后按权威性/时效性排序，或让 LLM 在回答中标注差异。

---

## 8. 下一步

本阶段只做了 RAG 数据工程的基础层：清洗 + 元数据增强。接下来可以继续深入：

- **PDF 深度解析**：表格结构化提取、图片 OCR + 多模态描述、版面分析。
- **增量更新**：文档变更检测、chunk 级 diff、最小化嵌入更新。
- **冲突处理**：语义矛盾识别、权威性排序、LLM 融合标注。
- **版本控制与回滚**：文档版本管理、入库审核、隔离/回滚/审计日志。

这些对应《RAG 七连问》的第 3-7 问，本阶段已经把地基打好。

---

## 9. 在 Kairos 里跑起来

本地验证命令：

```bash
# 1. 确保 JINA_API_KEY 和 LLM_API_KEY 已配置在 .env
# 2. 启动容器（RAG 在容器内跑）
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml up -d --build

# 3. 测试 RAG 端到端
python -m pytest tests/test_rag_cleaner.py tests/test_rag_enricher.py tests/test_rag_tool.py -v
```

观察指标：
- 清洗前后 chunk 数量变化。
- 每个 chunk 的 `quality_score`、`section`、`keywords`。
- 检索结果是否还包含页眉页脚类内容。
