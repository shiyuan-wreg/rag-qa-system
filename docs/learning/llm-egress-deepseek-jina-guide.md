# LLM 出口迁移实战:从通义千问到 DeepSeek + Jina(深度学习指南)

> 本文配套 2026-06-26 的开发:把 ai-demos 的 LLM 调用从大陆通义千问切到 DeepSeek(聊天)+ Jina(向量检索)。
> 目标读者:你自己(以后复盘)。写法:从最基础讲起,讲清每一步"为什么",而不只是"怎么做"。

---

## 0. 一句话全景

> **首尔服务器连不到大陆的通义千问 API,我们把聊天换成海外可达的 DeepSeek,把 RAG 的向量检索换成海外可达的 Jina;过程中顺带修了一个被 DeepSeek "用出来"的老 bug。**

这件事看似简单(换个 API),但牵出 6 个独立知识块:跨境网络、LLM 服务商账号体系、OpenAI 兼容协议、Function Calling、Embeddings/向量检索、工具描述与实现的对齐。下面逐块拆。

---

## 1. 跨境网络诊断:为什么"连不上"

### 1.1 现象

部署后 `/rag/` 一直 502 / 超时。聊天和检索都要调通义千问的 API(`dashscope.aliyuncs.com`),但从首尔服务器发请求,**卡住直到超时**。

### 1.2 关键工具:`curl` 的 `http_code`

诊断网络第一步,是分清"**连不上**"和"**连上了但被拒**"。`curl -w '%{http_code}'` 打印 HTTP 状态码:

| http_code | 含义 | 说明 |
|---|---|---|
| `000` | **根本没连上** | TCP/TLS 没建起来(网络不通、超时、DNS 失败) |
| `401` / `403` | 连上了,鉴权失败 | 网络 OK,是 key 的问题 |
| `200` | 连上且成功 | — |

> **术语:HTTP 状态码** 是服务器对一次请求的"回执"。但要先有"回执"才说明网络通了。`000` 意味着连回执都没拿到 —— 问题在网络层,不在应用层。这一步分流,决定你接下来查网络还是查鉴权。

实测:
```
dashscope.aliyuncs.com      → 000(20s 超时)   ← 网络不通
dashscope-intl.aliyuncs.com → 404(0.2s)        ← 网络通(404 只是没这个路由)
```

### 1.3 为什么大陆端点连不上:GTM + 跨境路由

> **术语:GTM(Global Traffic Manager,全局流量管理)** 是一种"智能 DNS"。同一个域名,它会根据**请求来源的地理位置**返回不同的服务器 IP,把用户导到最近的机房。

`dashscope.aliyuncs.com` 背后是 GTM(DNS 解析出来的真实主机名是 `gtm-cn-...`)。从首尔请求时,它返回的是**中国大陆机房的 IP**(`8.152.x`)。而从韩国到大陆这些 IP 的网络路由是**不通/被限速的**(跨境网络的常见现象)。

**怎么确认是 IP 层不通,而不是 DNS 错?** 用 `curl --resolve` 强制指定 IP:
```bash
curl --resolve dashscope.aliyuncs.com:443:8.152.159.24 https://dashscope.aliyuncs.com/
# → 000 超时   说明:就是连不到这个大陆 IP
```

### 1.4 一个干扰项:IPv4 vs IPv6

诊断中发现 dashscope 还解析出了 IPv6 地址(`2408:...`)。

> **术语:IPv4 / IPv6** 是两代互联网地址。IPv4 像 `8.152.159.24`,IPv6 像 `2408:400a:...`。很多服务器**只配了 IPv4 出口,没有 IPv6 路由**。

```bash
ip -6 addr show scope global | grep -c inet6   # → 0,服务器没有全局 IPv6
```
所以即使 DNS 给了 IPv6,服务器也走不通(瞬间失败)。**排查时要分别强制 `curl -4` / `curl -6`**,否则你会被"到底是 v4 还是 v6 的问题"搞混。结论:v4 到大陆 IP 超时,v6 没路由 —— 两条路都死。

### 1.5 方法论小结

> 网络诊断的因果链:**域名 →(DNS/GTM)→ IP →(路由)→ TCP →(TLS)→ HTTP**。
> 任何一环断了表现都是"连不上",但修法完全不同。逐环用工具定位:`getent ahostsv4/v6`(看 DNS 给什么 IP)、`curl --resolve`(绕过 DNS 测特定 IP)、`curl -4/-6`(分离协议)、`http_code 000 vs 4xx`(分网络层还是应用层)。

---

## 2. LLM 服务商的账号体系:同一个公司可能有两套账号

这是最反直觉、也最容易踩坑的一点。

### 2.1 阿里云:大陆站和国际站是两套独立王国

| | 大陆站 | 国际站 |
|---|---|---|
| 网站 | `bailian.console.aliyun.com` | `bailian.console.alibabacloud.com` |
| 端点 | `dashscope.aliyuncs.com` | `dashscope-intl.aliyuncs.com`(新加坡) |
| 账号 | 中国身份证 + 支付宝 | 境外手机号 + Visa/PayPal |
| 手机号 | 接受 +86 | **不接受 +86**(官方明确) |

关键实测:把端点指到国际站、但用**大陆站的 key**,结果:
```
401 Invalid API-key provided
```
> **因果:为什么大陆 key 在国际站是 401?** 因为这是两套**独立的账号/鉴权系统**。同一家公司,但大陆账号在国际系统里"查无此人"。这跟网络无关(网络是通的,才能拿到 401 这个回执)—— 是账号体系的隔离。

这也解释了为什么不能简单"换个端点"了事:换端点必须连账号一起换。

### 2.2 DeepSeek:只有一套

DeepSeek(深度求索)**没有**这种分裂:一个平台 `platform.deepseek.com`、一个端点 `api.deepseek.com`。

- 国内账号(+86、支付宝充值)申请的 key,**全球通用**。
- 端点跑在海外基础设施上(实测解析到 **AWS IP**),首尔直连可达。

> **因果:为什么 DeepSeek 能用国内账号 + 海外调用?** 因为它就一套系统,key 不绑区域;且 API 服务部署在全球可达的云上,不存在"大陆机房跨境不通"的问题。这正是它比阿里云国际站省心的根因。

---

## 3. 决策:三条路的权衡(为什么最后选 DeepSeek + Jina)

连不上大陆 dashscope,有三条出路:

| 方案 | 做法 | 成本 / 坑 |
|---|---|---|
| **A. 配出站代理** | 让服务器经一个"能连大陆的中间人"转发 | 需要额外一台一直开机、能连大陆、服务器够得到的机器。用户没有 → 不可行 |
| **B. 阿里云国际站 key** | 换国际端点 + 国际账号 key | 要境外手机号 + 境外卡 + 风控;**临时虚拟号会被风控拦,且账号根基不稳**(账号要托管生产 key,不能用临时号) |
| **C. 换 LLM 供应商** | 换一个海外可达、注册轻的 | 要改代码;RAG 的 embedding 要重做。但**注册只要邮箱/国内账号** |

最终选 **C(DeepSeek)**:工程上多干点活(我来写),换来行政上的省心(你不用搞境外号/卡)。

> **一句话权衡:国际站 = 花钱免劳力,换供应商 = 花劳力免麻烦。** 用户后续本来就打算用 DeepSeek,这笔投入还能复用 —— 这是压垮天平的最后一根稻草。

### 3.1 为什么 embedding 单独拎出来用 Jina

DeepSeek **只有聊天模型,没有 embeddings 接口**(下一节解释 embedding 是什么)。所以 RAG 的"检索"那一半 DeepSeek 给不了,得另找。选了 **Jina 托管 API**:
- 海外可达(实测)、免费额度、邮箱注册;
- 相比"本地跑 embedding 模型",**服务器零内存/磁盘负担**(不用装 torch ~1GB)。代价是多一个海外网络依赖(已实测可达,能接受)。

---

## 4. OpenAI 兼容 API 与 "一处抽象、多处复用"

### 4.1 什么是"OpenAI 兼容"

> **术语:OpenAI 兼容 API**。OpenAI 定义了一套调用大模型的 HTTP 接口格式(请求长什么样、返回长什么样)。后来很多厂商(DeepSeek、通义的兼容模式、众多开源托管平台)都**照这套格式实现自己的接口**。好处:你用同一套客户端代码 + 同一个 SDK(`openai` 这个 Python 包),**只改 `base_url` 和 `api_key`,就能从一家切到另一家**。

DeepSeek 就是 OpenAI 兼容的。所以"切到 DeepSeek"在代码层面 = 把客户端从"通义千问 SDK"换成"OpenAI SDK + DeepSeek 的 base_url"。

### 4.2 本项目早就埋了抽象:`LLMClient`

`core/llm.py` 里有个 `LLMClient`,它内部按 `provider` 分两条路:
```python
def _create_client(self):
    if self.provider == "qwen":
        import dashscope
        dashscope.api_key = self.api_key
        return dashscope.Generation          # 通义千问 SDK
    else:
        from openai import OpenAI
        return OpenAI(api_key=self.api_key, base_url=self.base_url)  # OpenAI 兼容
```
**问题是:之前只有 Nexus 用了这个抽象,FC 和 RAG 都各自硬编码直连通义千问。** 所以这次的核心重构是:

> **把三处硬编码的 `dashscope.Generation.call(...)` 全部改成走 `LLMClient`。** 一旦都走抽象层,"换供应商"就只是改配置(provider/model/base_url/key),不用再动每个调用点。

### 4.3 工厂方法 `from_config()`:把"读配置"集中到一处

新加的:
```python
@classmethod
def from_config(cls):
    from core.config import Config
    return cls(provider=Config.LLM_PROVIDER, model=Config.LLM_MODEL,
               api_key=Config.LLM_API_KEY or "", base_url=Config.LLM_BASE_URL)
```
> **设计意图:** 让 `core/agent.py`、`fc_app`、`evaluator`、`nexus` 都用 `LLMClient.from_config()`。配置只在一个地方读(`core/config.py`),以后再换供应商,改 `.env` 即可,代码一行不动。这叫"**配置与代码分离**"。

### 4.4 配置的"通用化 + 向后兼容"

`core/config.py` 新增:
```python
LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "qwen")
LLM_MODEL    = os.environ.get("LLM_MODEL", "qwen-turbo")
LLM_BASE_URL = os.environ.get("LLM_BASE_URL")                       # 新
LLM_API_KEY  = os.environ.get("LLM_API_KEY") or os.environ.get("DASHSCOPE_API_KEY", "")  # 新,带回退
JINA_API_KEY = os.environ.get("JINA_API_KEY", "")                  # 新
```
> **`LLM_API_KEY or DASHSCOPE_API_KEY` 这个回退**:即使有人还在用旧的 `DASHSCOPE_API_KEY` 变量,也不会突然失效。改造时保留旧路径的兼容,是降低风险的常用手法。

---

## 5. Function Calling(工具调用)原理

RAG 和 FC 都是"会用工具的 Agent"。这块是 LLM 应用的核心,值得讲透。

### 5.1 什么是 Function Calling

> **术语:Function Calling(函数/工具调用)**。普通聊天是"你问、模型用文字答"。Function Calling 让你额外告诉模型"**你有这些工具可用**"(每个工具有名字、说明、参数格式)。模型遇到需要工具的问题时,不直接答,而是**返回一个"我要调用 X 工具,参数是 Y"的结构化请求**;你的代码去真正执行这个工具,把结果喂回去,模型再基于结果作答。

一次带工具的对话,实际是这样一个**循环**:
```
用户问 → 模型说"调 search_docs(query=...)" → 你的代码跑 search_docs,得到片段
       → 把片段回填给模型 → 模型基于片段用文字回答 → 结束
```

### 5.2 工具的"自我介绍":tools schema

工具用一段 JSON 描述给模型(`core/tools.py` 的 `TOOLS`):
```json
{
  "type": "function",
  "function": {
    "name": "search_docs",
    "description": "从知识库中检索与问题相关的文档片段...",
    "parameters": { "type": "object",
      "properties": { "query": {"type":"string","description":"检索查询"} },
      "required": ["query"] }
  }
}
```
> **关键认知:模型只能看到 `description` 来判断"什么时候该用、怎么用"这个工具。** description 写得准不准,直接决定模型用得对不对。记住这句话 —— 第 7 节那个 bug 就栽在这。

### 5.3 多轮循环与 `max_turns`

代码里有个保护:
```python
for turn in range(self.max_turns):   # max_turns = 5
    message = self.llm.chat([system]+messages, tools=TOOLS)
    if message["tool_calls"]:
        # 执行工具,把结果回填到 messages,continue 再问模型
    else:
        return message["content"]     # 模型给出最终文字答案,结束
```
> **为什么要 `max_turns`?** 防止模型陷入"调工具→看结果→又调工具→……"的死循环。到了 5 轮还没给最终答案就强制停。**第 7 节的 bug 就是触发了这个保护**,返回"处理时间过长"。

### 5.4 不同供应商的返回格式差异(以及如何抹平)

通义千问返回 `response.output.choices[0].message`(自家格式),OpenAI 兼容返回 `response.choices[0].message`(对象)。`LLMClient._extract_content` 把两者**归一化成同一个 dict**:
```python
return {"content": "...", "tool_calls": [{"id":..., "function":{"name":..., "arguments": "..."}}]}
```
> **这就是抽象层的价值**:上层的 Agent 循环只认这个统一 dict,完全不用关心底层是通义还是 DeepSeek。这次能"干净替换",正是因为这个归一化早就写好了。

### 5.5 一个小坑:`tools=None`

OpenAI 兼容服务里,有的会因为请求里带了 `tools: null` 而报错。所以 `LLMClient` 改成:**没有工具时就不传 `tools` 这个字段**(Nexus 的 agent 不用工具)。
```python
kwargs = {"model":..., "messages":..., "stream":...}
if tools: kwargs["tools"] = tools     # 只在有工具时才加
```

---

## 6. Embeddings 与向量检索:RAG 的另一半

### 6.1 什么是 Embedding

> **术语:Embedding(向量/嵌入)**。把一段文字交给 embedding 模型,它输出一串数字(比如 1024 个浮点数),叫"向量"。这串数字是这段文字"语义的坐标"。**语义相近的文字,向量也相近**(空间里离得近)。

### 6.2 向量检索(RAG 的"检索"环节)怎么工作

```
建库阶段:把文档切成小块 → 每块算 embedding → 存进向量库(Chroma)
查询阶段:把用户问题也算 embedding → 在库里找"向量最近"的几块 → 返回这些原文
```
这就是 `search_docs` 工具背后做的事。检索到的原文片段,再交给聊天模型(DeepSeek)去组织答案。这套"检索 + 生成"就叫 **RAG(Retrieval-Augmented Generation,检索增强生成)**。

> **本项目 RAG 管线(代码位置):** `rag/loader.py`(加载文档)→ `rag/splitter.py`(切块,500 字/块)→ `rag/vectorstore.py`(算 embedding + 存 Chroma)→ `rag/retriever.py`(查询时找最近块)。

### 6.3 为什么"换 embedding 模型"必须重建整个索引

通义的 embedding 和 Jina 的 embedding,**向量维度和向量空间都不一样**(一个可能是 1536 维、另一个 1024 维;即使维度相同,"语义坐标系"也不同)。

> **因果:为什么不能混用?** 库里存的是旧模型的向量,查询用新模型的向量 —— 两套坐标系对不上,"找最近"算出来是垃圾。所以换了 embedding 模型,**旧的 `chroma_db` 必须删掉,用新模型重新建库**。这次部署时就 `rm -rf chroma_db` 让它用 Jina 重建。

### 6.4 为什么手写 Jina 客户端,而不用现成库

`rag/vectorstore.py` 里手写了个十几行的 `JinaEmbeddings`,直接 POST `api.jina.ai/v1/embeddings`。Chroma 需要的接口很简单,只要两个方法:
```python
class JinaEmbeddings:
    def embed_documents(self, texts): ...   # 建库时:给一批文本块算向量
    def embed_query(self, text): ...         # 查询时:给问题算向量
```
> **为什么不用 langchain 自带的 `JinaEmbeddings`?** 避免依赖第三方封装的版本差异/暗坑。接口就两个方法,自己写更可控、更透明。这是"**少依赖、可掌控**"的取舍。
> 细节:Jina v3 支持 `task` 提示 —— 建库用 `retrieval.passage`,查询用 `retrieval.query`,告诉模型"这是文档" vs "这是问题",检索质量更好。

### 6.5 本地 vs 托管 embedding 的权衡(为什么没选本地)

| | 本地模型(sentence-transformers) | Jina 托管 |
|---|---|---|
| 服务器负担 | 装 torch ~1GB,常驻内存 ~400MB | **零负担** |
| 网络依赖 | 无 | 多一个海外 API 依赖 |
| 适合 | 内存充裕的机器 | **2GB 小机器(本项目)** |

服务器只有 1.6G 内存,选了零负担的 Jina。

---

## 7. 案例:被 DeepSeek "用出来"的老 bug(工具描述必须和实现对齐)

这是本次最有教学价值的一段。

### 7.1 现象

切到 DeepSeek 后,`/rag/` 问"什么是 Python 装饰器",返回 **"处理时间过长"**(触发了 max_turns)。日志显示模型反复调 `execute_python`,每次都报:
```
[工具] execute_python({"code": "def my_decorator(func): ..."})
[工具返回] Error: syntax error - invalid syntax (line 2)
```
模型发的是**合法的** Python 装饰器代码,却报语法错误,然后换个写法再试,循环到超时。

### 7.2 根因:`execute_python` 名不副实

看实现 `core/tools.py`:
```python
tree = ast.parse(code, mode='eval')   # ← 关键
```
> **术语:`ast.parse(mode='eval')` vs `mode='exec'`**。`mode='eval'` 只能解析**单个表达式**(比如 `2+3*4`、`[1,2]+[3]`),**不能有 `def`、`print`、多行语句**。它本质是个"**算术计算器**",不是通用 Python 执行器。

但工具的 `description` 写的是"安全执行一段受限的 Python 表达式,用于数学计算、数据结构验证等" —— **描述听起来像能跑程序**。

### 7.3 为什么之前(通义)没事,换 DeepSeek 才爆

> **因果链:** 工具描述模糊 → 不同模型理解不同。通义千问很少去调 `execute_python`(或只发简单表达式);**DeepSeek 更"积极"用工具,看到"装饰器"就想写段 `def` 代码演示** → 发给只认表达式的计算器 → SyntaxError → 模型以为是自己代码写错,换个写法重试 → 死循环 → max_turns。

这是个**潜伏的老 bug**:实现和描述早就不一致,只是通义没把它"用出来",DeepSeek 把它暴露了。

### 7.4 修法:让描述对齐实现 + 引导模型

不是去扩大 `execute_python` 的能力(那要做沙箱,安全敏感、超出范围),而是**让描述诚实**:
```python
# 工具描述改成:
"纯算术计算器:只能计算单个算术表达式...不能定义函数、不能用 print、
 不能写多行代码。只在需要精确数字计算时调用,其它问题请直接用文字回答。"

# 报错也改成会"教"模型停手:
"Error: 本工具只支持单个算术表达式...请不要再调用本工具,直接用文字回答用户。"
```
再松一下 system prompt:把原来"**必须**用 execute_python"改成"先用 search_docs 检索,然后**直接根据检索结果用文字回答**;execute_python 只是算术计算器,别拿它写示例代码"。

> **教训:工具的 `description` 是模型唯一的"使用说明书"。description 和真实能力一旦不一致,迟早出事 —— 换个更主动的模型就会触发。写工具时,描述要诚实地反映实现的边界。**

---

## 8. 验证方法论:别只看 200

> 这次反复强调一件事:**"路由返回 200" ≠ "功能正常"**。

- 200 只说明"网页/接口能打开"。RAG 真正能不能检索、聊天真正能不能调通 LLM,**必须发真实请求看真实结果**。
- 例子:之前部署黑白改版后 `/iconforge/` 返回 200,但点进去是空白页(React 路由漏了)。**200 骗了我们**。
- 这次的验证都是真实调用:FC 问天气看是否触发 `get_weather`;RAG 问"语料里有的问题"(Python 谁创建)看是否检索到正确片段;Nexus 看是否吐 `final_answer`。
- 可达性也都是**从服务器侧实测**(不是从本机猜)。因为本机(中国)和服务器(韩国)网络环境不同 —— 本机连不上 Jina,服务器连得上。**在哪运行就在哪测**。

> 方法论:**验证要打到"行为"层,不是"状态码"层;要在"真实运行环境"里测,不是在开发机猜。**

---

## 9. 本次改动清单(文件级,便于复盘)

| 文件 | 改了什么 | 为什么 |
|---|---|---|
| `core/config.py` | 加 `LLM_BASE_URL/LLM_API_KEY/JINA_API_KEY`,带回退 | 配置通用化 |
| `core/llm.py` | 加 `from_config()`;`tools=None` 时不传该字段 | 集中读配置 + 兼容性 |
| `core/agent.py` | 直连 dashscope → `LLMClient`;改 system prompt | RAG 聊天走抽象 + 防 loop |
| `backends/fc_app/main.py` | 同上;Dockerfile 加 `COPY core/` | FC 聊天走抽象 |
| `eval/evaluator.py` | 直连 dashscope → `LLMClient` | 评估也走抽象 |
| `backends/nexus_app/main.py` | `LLMClient.from_config()`;key 门槛改 `LLM_API_KEY` | 统一 |
| `rag/vectorstore.py` | `DashScopeEmbeddings` → 手写 `JinaEmbeddings` | embedding 换 Jina |
| `core/rag_tool.py` | key 门槛改 `JINA_API_KEY` | embedding 现在用 Jina key |
| `core/tools.py` | `execute_python` 描述/报错对齐实现 | 修 loop bug |
| `requirements.txt` / `nexus/requirements.txt` | 加 `openai` | 用 OpenAI SDK |
| `.env.example` | 通用键 + DeepSeek/Jina 示例 | 文档 |

部署:服务器 `.env` 改新键 → `git pull` → `rm -rf chroma_db` → `compose up --build rag fc nexus`。

---

## 10. 系统学习路径 + 自测追问

### 想把这块吃透,按这个顺序补:
1. **HTTP 基础**:状态码(2xx/4xx/5xx)、`curl` 常用参数(`-w`、`--resolve`、`-4/-6`)。
2. **DNS 与 CDN/GTM**:域名怎么解析成 IP;为什么同一域名不同地区给不同 IP。
3. **OpenAI API 规范**:`chat/completions` 的请求/返回结构、`tools` 字段、`tool_calls`。动手:直接用 `curl` 打一次 DeepSeek 的 `chat/completions`(本文里有例子)。
4. **Function Calling 全流程**:亲手跑一遍"模型请求调工具 → 代码执行 → 回填 → 模型作答"。
5. **Embeddings & 向量库**:embedding 是什么、余弦相似度、Chroma 怎么存/查;为什么换模型要重建。
6. **RAG 架构**:loader/splitter/embedding/retriever 四件套,以及"检索 + 生成"如何配合。

### 自测追问(能答上来说明懂了):
1. `curl` 返回 `000` 和返回 `401`,分别说明问题出在哪一层?修法有何不同?
2. 为什么大陆 dashscope key 拿到国际端点会 401,而不是超时?(提示:能拿到 401 说明什么已经成立?)
3. DeepSeek 用国内账号申请的 key,为什么能从韩国服务器调用?和阿里云的区别在哪?
4. "OpenAI 兼容"具体兼容的是什么?为什么它让"换供应商"变成"改两行配置"?
5. Function Calling 里 `max_turns` 是干嘛的?这次它为什么被触发了?
6. 为什么换了 embedding 模型,旧的 `chroma_db` 必须删掉重建?
7. `execute_python` 这个 bug 的真正根因是什么?为什么通义没事、DeepSeek 才爆?这给"写工具"什么启示?
8. 为什么说"路由 200 不等于功能正常"?这次/上次各有什么例子?
9. 为什么 embedding 的可达性要"从服务器测"而不是"从本机测"?

### 还能往深挖(进阶):
- DeepSeek 的 `deepseek-chat` 实际返回的 model 字段是 `deepseek-v4-flash` —— 去查 DeepSeek 现在的模型矩阵和定价。
- Jina v3 的 `task` 参数(retrieval.passage/query/separation/classification)各自适合什么场景。
- 本项目遗留:Nexus retriever 的 `object Response can't be used in 'await'` —— 这是 httpx **同步 client 的返回值被 `await`** 了。去看 httpx 同步 vs 异步 client 的区别,想想怎么修(明天的任务)。
