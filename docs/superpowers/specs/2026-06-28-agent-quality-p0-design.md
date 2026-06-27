# Agent 回答质量优化 P0 设计

> 日期:2026-06-28
> 目标:释放 RAG / FC 两个 demo 的回答质量(更详细、结构化、可溯源),靠 **prompt 工程 + 检索结果格式化 + 前端 Markdown 渲染**,不动检索算法、不接真实 API。
> 依据:桌面《ai-demos RAG + Function Calling 质量优化方案》P0 项;当前代码 HEAD `fc2e723`。

---

## 1. 背景与问题

当前 RAG/FC 回答短、不精准、像「raw data」。根因(P0 关心的部分):

- **生成层约束太弱**:两个 Agent 的 system prompt 都是功能性描述,没要求详细、结构化、引用溯源。
- **RAG 检索结果格式化粗糙**(`core/rag_tool.py`):把片段编号罗列,`replace("\n"," ")` 破坏代码格式,不带来源,模型无从引用。
- **前端渲染限制**:`rag_app` / `fc_app` 前端用 `escapeHtml(content)` + `white-space: pre-wrap` 渲染回答,即使模型输出 Markdown,`#`、`**`、` ``` ` 也只会裸露成纯文本,反而更难看。所以「结构化输出」必须配套前端渲染。

P1+(本设计**不做**):检索 top_k/rerank/hybrid、chunk 元数据管道改造、接真实天气/搜索 API、FC `calculate` 的 eval→安全求值替换、查询改写/多轮优化、评估飞轮。

## 2. 范围(P0)

| 改动 | 文件 | 性质 |
|---|---|---|
| RAG system prompt 重写 | `core/agent.py` | prompt |
| RAG 检索结果格式化 | `core/rag_tool.py` | 代码(纯函数,可单测) |
| FC system prompt 重写 | `backends/fc_app/main.py` | prompt |
| FC 缺参数代码强制反问 | `backends/fc_app/main.py` | 代码(chat 循环) |
| 两端 Markdown 渲染 | `backends/rag_app/main.py`、`backends/fc_app/main.py` 内联 HTML/JS | 前端 |

非目标:不改 `rag/splitter.py`、`rag/retriever.py`、`rag/loader.py`(`source` 元数据已由 langchain `TextLoader` 写入,`split_documents` 保留,格式化直接读即可);不接真实 API;不改 FC `calculate` 的 eval;不部署生产(本地验收即止)。

## 3. 详细设计

### 3.1 RAG system prompt(`core/agent.py` 的 `self.system_message`)

角色:**耐心、专业的技术文档讲师**。规则:

1. 先给**核心结论 / 直接答案**;
2. 再分 2-4 点详解,每点讲清「是什么」+「为什么」;
3. 尽量给一个**具体例子或代码片段**;
4. 涉及文档内容**必须先调用 `search_docs`**,基于检索结果回答,并用 `[1] [2]` 标注引用对应片段编号;
5. 检索结果不足时明确说「根据现有资料无法确定」,**不编造**;
6. 用 **Markdown** 组织(标题 / 列表 / 代码块 / 表格),前端会渲染成富文本。

保留原有约束(不可丢):`execute_python` 仅算术、不可拿来写示例代码 / 定义函数;`read_file`/`list_files` 用于看文件目录;工具失败时说明情况、不反复重试同一工具。

### 3.2 RAG 检索结果格式化(`core/rag_tool.py` 的 `RAGTool.search()`)

把现有罗列式改为带来源、带排序提示、保留原始格式:

- **删除** `.replace("\n", " ")`(保留代码 / 段落换行);
- 输出开头带用户 `query` 一行 + 「以下是按相关度排序的相关片段」提示;
- 每个片段:`[i] 来源:<basename(source)>` 换行后接 `doc.page_content`(strip 但不压换行);
- 单片段截断上限 `500 → 800` 字符,仍保留上限防 token 爆;超长加 `…`;
- `top_k` 维持 3(加大召回 + 重排属 P1)。

`source` 取 `doc.metadata.get("source", "未知来源")`,只取 `os.path.basename`。

### 3.3 FC system prompt(`backends/fc_app/main.py` 的 `Agent.system_message`)

角色:**智能任务助手**。用工具后把结果组织成自然、完整的回答:

1. 说明调用了什么工具及原因;
2. 给出工具返回的结果;
3. 据结果给**建议 / 下一步**(如查到下雨→提示带伞);
4. 缺必要参数时**主动反问用户、不猜测**(配合 3.4 的代码强制);
5. 用 **Markdown** 结构化输出。保留「工具失败如实说明、不编造结果」。

### 3.4 FC 缺参数代码强制反问(`backends/fc_app/main.py` 的 `Agent.chat` 循环)

在执行某个 tool_call **之前**,校验其 `required` 参数:

- 从 `TOOLS` 构建 `tool_name -> required[]` 映射(读 `function.parameters.required`);
- 对每个 tool_call,检查 `tool_args` 是否缺少 required 项,或其值为空字符串 / `None`;
- **若缺**:不调用工具,改为向 `messages` 追加一条该 `tool_call_id` 的 `role:"tool"` 结果,内容形如「缺少必要参数:`time`。请向用户说明并询问,不要猜测。」→ 下一轮模型据此生成反问;`tool_calls_log` 仍记录该调用但标注未执行;
- **若不缺**:照常执行。

实现要点:保持原循环结构,仅在「逐个执行工具」处插入校验分支;一次 message 里多个 tool_call 分别判定。

### 3.5 前端 Markdown 渲染(`rag_app` + `fc_app` 内联 HTML)

- 各自**内联**一段 ~100 行极简 `renderMarkdown(text)` 函数(**不依赖 CDN**;与现有主题 token 一样接受跨文件重复,P0 不抽共享);
- 支持:ATX 标题(`#`~`######`)、`**粗**` / `*斜*`、行内 `` `code` ``、围栏代码块 ```` ``` ````、有序 / 无序列表、表格(`| a | b |`)、链接 `[t](url)`、段落与换行;`[1]` 这类引用标记原样保留;
- **安全**:先对整段 `escapeHtml`,再在转义后的文本上做 Markdown→HTML 变换(回答源自 LLM,防注入);
- 只对 **assistant 回答** 调 `renderMarkdown` 并 `innerHTML`;**user 消息** 仍走纯文本 `escapeHtml`(避免用户输入被当 markdown);
- 工具调用标签区(`.tools`)逻辑不变。

## 4. 验证(evidence-before-claims)

1. **确定性单测**(pytest,新增 `tests/` 下用例):构造带 `metadata['source']` 与含换行 / 代码的假 docs,断言 `RAGTool.search()`(或抽出的格式化纯函数)输出:① 保留换行;② 含来源 basename;③ 含 query;④ 超长截断带 `…`。
2. **FC 缺参数单测**:模拟一个缺 `time` 的 `set_reminder` tool_call,断言工具未被执行且 `messages` 末尾出现「缺少必要参数」提示。
3. **人工 eval**:~8-10 个问题分别跑 RAG / FC(本地 docker),肉眼对比改前 / 改后:RAG 看是否分点 + 引用 + 例子;FC 看是否解释过程 + 给建议 + 缺参反问。
4. **浏览器肉眼验** Markdown 渲染:标题 / 列表 / 代码块 / 表格在两个 demo 均正确渲染,user 消息不被 markdown 化。
5. **回归**:现有测试套件保持绿(`venv` 内 pytest)。

## 5. 部署

本次**仅本地**:`docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.local.yml up -d --build` 重建 rag/fc 镜像(源文件改动重建即生效)+ 肉眼验收。**推生产延后**,后续可与尚未部署的主题皮肤批次一并推首尔。

## 6. 风险 / 取舍

- **Markdown 渲染器是手写极简版**,不覆盖全部 CommonMark 边界(嵌套列表、引用块等);P0 覆盖常用语法即可,渲染失败应「降级为纯文本」而非报错。
- **Prompt 改动无法确定性单测**,质量靠人工 eval 判断,带主观性;用固定问题集降低波动。
- **渲染器代码两端重复**,后续若再加 demo 需第三次复制——记入 P1 可抽共享 JS。
- FC 缺参数校验依赖 `required` 声明准确;现有三工具的 `required` 均已正确声明。
