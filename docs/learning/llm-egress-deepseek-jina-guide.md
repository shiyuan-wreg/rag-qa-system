# LLM 出口迁移实战:从通义千问到 DeepSeek + Jina(深度学习指南)

> 配套 2026-06-26 的开发:把 ai-demos 的 LLM 调用从大陆通义千问切到 DeepSeek(聊天)+ Jina(向量检索)。
> **写法约定**:每个结论都带"为什么";术语第一次出现给定义,关键术语再"往下钻一层";代码尽量给完整函数 + 逐行注释;尽量用**这次真实跑出来的命令输出/JSON/日志**,而不是编的例子。
> **怎么读**:第一遍通读建立全貌;第二遍对着每节末尾的"动手"自己敲一遍;最后做第 12 节的自测题,答不上来的回去重读对应节。

---

## 目录

0. 一句话全景与本次改了什么
1. 预备知识:一个 HTTP 请求到底经过哪些层
2. 跨境网络诊断:为什么"连不上"(含真实命令输出)
3. LLM 服务商的账号体系:同一家公司两套账号
4. 决策:三条路的权衡
5. OpenAI 兼容协议与 `LLMClient` 抽象(完整代码)
6. Function Calling 原理(真实 JSON + 多轮循环全代码)
7. Embeddings 与向量检索:RAG 的另一半(含相似度数学)
8. 案例精讲:被 DeepSeek "用出来"的老 bug
9. SSE 与 Nexus 多 agent(以及那个遗留 async bug)
10. 验证方法论:为什么"200 不算数"
11. 本次改动清单(文件级)
12. 系统学习路径 + 自测题(带答案要点)

---

## 0. 一句话全景与本次改了什么

> **首尔服务器连不到大陆的通义千问 API。我们把聊天换成海外可达的 DeepSeek,把 RAG 的向量检索换成海外可达的 Jina;过程中修了一个被 DeepSeek "用出来"的老 bug。**

这件事牵出 6 个独立知识块,本文逐块拆透:

| 知识块 | 核心问题 | 在第几节 |
|---|---|---|
| 跨境网络 | 为什么"连不上",怎么逐层定位 | §1 §2 |
| LLM 账号体系 | 为什么大陆 key 在国际端点是 401 | §3 |
| OpenAI 兼容协议 | 为什么"换供应商"能变成"改两行配置" | §5 |
| Function Calling | Agent 怎么"会用工具" | §6 §8 |
| Embeddings / 向量检索 | RAG 怎么"找到相关文档" | §7 |
| 工程方法论 | 怎么诊断、怎么验证、怎么不被假象骗 | §2 §10 |

---

## 1. 预备知识:一个 HTTP 请求到底经过哪些层

> 不懂这一层,后面所有"连不上"的诊断都是背命令。先把"一次 `https://api.deepseek.com/...` 请求"拆开。

当你的代码发一个 HTTPS 请求,实际依次发生:

```
1. DNS 解析    api.deepseek.com  ──查询──▶  得到 IP(如 3.173.21.63)
2. TCP 连接    和这个 IP 的 443 端口建立连接(三次握手)
3. TLS 握手    在 TCP 之上协商加密(证书校验、密钥交换)→ 得到加密通道
4. HTTP 请求   在加密通道里发 "POST /chat/completions ..." + 请求体
5. HTTP 响应   服务器回 "200 OK" + 响应体(或 4xx/5xx)
```

> **术语逐个钻:**
> - **DNS(Domain Name System,域名系统)**:把人类好记的域名(`api.deepseek.com`)翻译成机器用的 IP 地址。像电话簿。一个域名可以对应多个 IP。
> - **IP 地址**:机器在网络上的门牌号。IPv4 形如 `3.173.21.63`(4 段),IPv6 形如 `2408:400a:...`(更长,因为 IPv4 不够用了)。
> - **TCP(传输控制协议)**:在两台机器间建立可靠的双向数据通道。"三次握手"= 客户端说"我要连"、服务器说"可以"、客户端说"好" —— 三个来回才算连上。**如果路由不通,卡在这一步**,表现为超时。
> - **端口**:一台机器上区分不同服务的编号。HTTPS 默认 443,HTTP 默认 80,SSH 默认 22。
> - **TLS(传输层安全)**:给 TCP 通道加密,就是 HTTP**S** 里那个 S。包含"证书校验"(确认对方真是 deepseek 而不是冒充的)。
> - **HTTP 状态码**:服务器对请求的"回执编号"。2xx 成功、4xx 你的错(401 没鉴权、404 没这个路由)、5xx 服务器的错。

**关键推论(整篇诊断的基石):**

> 第 1~3 步任何一步断了,你**根本拿不到 HTTP 状态码**(连"回执"都没有)→ `curl` 显示 `000`。
> 只有第 4~5 步走通了,才会有状态码(哪怕是 401/404)。
> **所以:`000` = 网络层problem(DNS/路由/TCP/TLS);`4xx` = 网络通了,是应用层problem(鉴权/路由/参数)。** 这一刀,决定你接下来查网络还是查 key。

---

## 2. 跨境网络诊断:为什么"连不上"

### 2.1 现象与第一刀

部署后 `/rag/` 一直 502。RAG 要调通义千问。我们从服务器直接测端点:

```bash
# 真实命令与输出(从首尔服务器跑)
$ curl -s -o /dev/null -w 'http_code=%{http_code} time=%{time_total}s' \
       --max-time 20 https://dashscope.aliyuncs.com/
http_code=000 time=20.002494s
```

> `-o /dev/null` 丢弃响应体只看状态;`-w` 打印我们关心的字段;`--max-time 20` 最多等 20 秒。
> 结果 `000` + 正好 20 秒(被 max-time 砍断)= **TCP 都没连上**。按 §1 的推论,问题在网络层,不在 key。

对照:换国际端点:
```bash
$ curl ... https://dashscope-intl.aliyuncs.com/
intl: 404 0.214908s remote=47.236.175.160
```
`404` + 0.2 秒 = **网络通了**(404 只是"没有 `/` 这个路由",但 TCP/TLS/HTTP 全走通了),而且对端 IP 是 `47.236.x`(新加坡)。

> **学到的招式:用一个"已知正常"的对照组**。同样的命令打两个端点,一个 000 一个 404,立刻锁定"是这个特定域名/IP 的网络problem",排除"是我服务器整体断网"。

### 2.2 为什么大陆端点连不上:GTM + 跨境路由

先看 DNS 给了什么:
```bash
$ getent hosts dashscope.aliyuncs.com
2408:400a:3e:ef00:...  gtm-cn-rt54j1mlg03.dashscope.aliyuncs.com  dashscope.aliyuncs.com
```

两个线索:
1. 真实主机名是 **`gtm-cn-...`** —— `gtm` = Global Traffic Manager。
2. 解析出来是 **IPv6**(`2408:...`)。

> **术语:GTM(全局流量管理)= 智能 DNS。** 普通 DNS 不管你从哪来,都返回同样的 IP。GTM 会**看请求来源的地理位置,返回不同的 IP**,把你导到"最近/最优"的机房。
> 后果:从首尔问 `dashscope.aliyuncs.com`,GTM 认为你该走**中国大陆机房**,返回大陆 IP(`8.152.x`)。但**韩国 → 大陆这些 IP 的网络路由是不通/被限的**(跨境网络常态)。

怎么坐实"就是连不到那个大陆 IP",而不是 DNS 抽风?用 `--resolve` 强行指定 IP:
```bash
$ curl -4 --resolve dashscope.aliyuncs.com:443:8.152.159.24 https://dashscope.aliyuncs.com/
mainland 8.152.159.24:443  000  8.001925s     # ← 强制连大陆 IP,超时
```

> **术语:`curl --resolve 域名:端口:IP`** = "这个域名你别查 DNS 了,就当它是这个 IP"。用来**绕过 DNS、精确测某个 IP 通不通**。这是网络诊断的利器。

### 2.3 干扰项:IPv4 还是 IPv6 的锅?

因为 DNS 给了 IPv6,得排除"是不是只是 IPv6 不通"。分别强制:
```bash
$ curl -4 ... https://dashscope.aliyuncs.com/      # 强制 IPv4
v4: 000 15.002073s remote=          # 超时,连 remote IP 都没填上
$ curl -6 ... https://dashscope.aliyuncs.com/      # 强制 IPv6
v6: 000 0.000872s remote=           # 瞬间失败(0.0008s)
$ ip -6 addr show scope global | grep -c inet6
0                                    # 服务器没有全局 IPv6 地址
```

> 读法:
> - `curl -4` 超时 15 秒 = 走 IPv4 到大陆 IP,**路由不通**(慢慢超时)。
> - `curl -6` 瞬间(0.0008s)失败 = 服务器**根本没有 IPv6 出口**,内核立刻拒绝,不用等。
> - `ip -6 ... grep -c inet6 → 0` 证实没有全局 IPv6。
> **两条路都死:v4 超时、v6 没路由。** 分离协议测,才不会把两个独立problem搅成一团。

### 2.4 方法论小结(网络诊断的因果链)

```
域名 ──DNS/GTM──▶ IP ──路由──▶ TCP ──TLS──▶ HTTP
 │                │            │            │
getent/dig    --resolve     -4/-6 +       http_code
看给什么IP    绕过DNS测IP    看超时还是秒拒   000 vs 4xx
```
> 任何一环断,表现都是"连不上",但修法天差地别。**逐环用对应工具定位**,别一上来就猜。

**动手**:对你想用的任意 API(比如 `api.openai.com`),依次跑 `getent hosts`、`curl -w http_code`、`curl -4`/`-6`,观察输出,练手感。

---

## 3. LLM 服务商的账号体系:同一家公司两套账号

这是最反直觉、最坑的一点。

### 3.1 阿里云:大陆站和国际站是两套独立王国

| | 大陆站 | 国际站 |
|---|---|---|
| 控制台 | `bailian.console.aliyun.com` | `bailian.console.alibabacloud.com` |
| API 端点 | `dashscope.aliyuncs.com` | `dashscope-intl.aliyuncs.com`(新加坡) |
| 注册身份 | 中国身份证 + 支付宝 | 境外手机号 + Visa/PayPal |
| +86 手机号 | ✅ | ❌ 官方明确不接受 |

**关键实测**:把 SDK 指到国际端点、但用**大陆站的 key**:
```bash
# 在容器里,设环境变量把 dashscope SDK 指向国际站
$ DASHSCOPE_HTTP_BASE_URL=https://dashscope-intl.aliyuncs.com/api/v1 python3 -c "..."
base url in use: https://dashscope-intl.aliyuncs.com/api/v1
gen status: 401 | msg: Invalid API-key provided.        # ← 网络通了,但 key 不认
embed status: 401 | msg: Invalid API-key provided.
```

> **因果:为什么是 401 而不是超时?**
> 能拿到 `401` 这个**HTTP 状态码**,说明 §1 的第 1~5 步全走通了 —— **网络完全没problem**。401 是应用层在说"我收到了你的请求,但这个 key 我不认识"。
> 为什么不认识?因为大陆站和国际站是**两套独立的账号/鉴权数据库**。同一个阿里云,但大陆账号在国际系统里"查无此人"。
>
> **这把"网络problem"和"账号problem"彻底分开了**:之前 `dashscope.aliyuncs.com` 是 000(网络不通),现在 `dashscope-intl` 是 401(网络通、账号不对)。两个完全不同的problem,被两个不同的状态码精确区分。

### 3.2 顺带学到的:dashscope SDK 怎么改端点

排查时发现 dashscope 这个 Python 包,**在 import 时读一个环境变量**决定端点:
```python
# dashscope/common/env.py(SDK 源码)
base_http_api_url = os.environ.get(
    "DASHSCOPE_HTTP_BASE_URL",
    f"https://dashscope.aliyuncs.com/api/{api_version}",   # 默认大陆
)
```
> **学到的通用招式**:想知道一个 SDK 能不能改端点/超时等,直接进它源码 `grep 'environ\|getenv'`,看它读哪些环境变量。这比翻文档快。

### 3.3 DeepSeek:只有一套(这才是我们选它的根因)

DeepSeek(深度求索)**没有**这种分裂:
- 一个平台 `platform.deepseek.com`、一个端点 `api.deepseek.com`。
- 国内账号(+86 注册、支付宝充值)的 key **全球通用**。
- 端点跑在海外云上 —— 实测从首尔可达,且解析到 **AWS 的 IP**:
```bash
$ curl ... https://api.deepseek.com/
api.deepseek.com -> 401 0.185466s remote=3.173.21.63    # 通,3.173.x 是 AWS
```

> **因果:DeepSeek 为什么省心?** 一套系统 → key 不绑区域;API 在全球可达的云上 → 没有"大陆机房跨境不通"。**所以国内账号 + 韩国服务器调用,完全没problem。** 这正是它比阿里云国际站省事的本质。

---

## 4. 决策:三条路的权衡

连不上大陆 dashscope,三条出路:

| 方案 | 做法 | 致命点 |
|---|---|---|
| **A. 配出站代理** | 服务器经一个"能连大陆的中间人"转发 | 需要额外一台**一直开机、能连大陆、服务器够得到**的机器。用户没有 → 不可行 |
| **B. 阿里云国际站 key** | 换国际端点 + 国际账号 key | 要境外手机号 + 境外卡 + 风控。临时虚拟号会被风控拦,且**账号要长期托管生产 key,不能用临时号**(随时被封) |
| **C. 换 LLM 供应商** | 换海外可达、注册轻的 | 要改代码 + RAG embedding 重做。但**注册只要邮箱/国内账号** |

选 **C(DeepSeek)**。

> **一句话权衡:国际站 = 花钱免劳力;换供应商 = 花劳力免麻烦。** 工程的活我来干(你不写代码),换来你不用搞境外号/卡;而且你后续本就打算用 DeepSeek,这笔投入能复用。

**为什么 embedding 单独用 Jina**:DeepSeek 只有聊天模型,**没有 embeddings 接口**(§7 解释 embedding 是什么)。RAG 的"检索"那半 DeepSeek 给不了,另选 Jina 托管(海外可达、免费额度、邮箱注册;比本地跑模型省服务器内存)。

> **可达性都从服务器侧实测过**(api.deepseek.com / api.jina.ai),不靠想当然 —— 延续 §2 dashscope 踩坑的教训:**在哪运行,就在哪测可达性。**

---

## 5. OpenAI 兼容协议与 `LLMClient` 抽象

### 5.1 什么是"OpenAI 兼容"

> **术语:OpenAI 兼容 API。** OpenAI 定义了一套调大模型的 HTTP 接口规范 —— 请求发到 `/chat/completions`,请求体长这样,返回体长那样。后来很多厂商(DeepSeek、众多托管平台、通义的"兼容模式")都**照这套规范实现自己的接口**。
> 好处:同一套客户端代码 + 同一个 `openai` Python 包,**只改 `base_url` 和 `api_key` 就能从一家切到另一家**。这就是"兼容"的价值 —— 把"供应商"变成一个可替换的配置项。

DeepSeek 的真实请求长这样(我们实测过):
```bash
$ curl https://api.deepseek.com/chat/completions \
   -H "Authorization: Bearer $LLM_API_KEY" -H "Content-Type: application/json" \
   -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hi"}]}'
```
真实返回(节选):
```json
{
  "id": "07ce1ad6-...",
  "model": "deepseek-v4-flash",
  "choices": [{"index":0,
    "message": {"role":"assistant","content":"Hello! How can I help you today?"},
    "finish_reason":"stop"}],
  "usage": {"prompt_tokens":5,"completion_tokens":9,"total_tokens":14}
}
```
> 注意:我们传 `model=deepseek-chat`,它实际用的是 `deepseek-v4-flash`(`deepseek-chat` 是个会指向当前主力模型的别名)。`choices[0].message.content` 就是回答。这套结构就是"OpenAI 兼容"的标准形状。

### 5.2 项目早就埋了抽象:`LLMClient`(完整代码逐行讲)

`core/llm.py` 的核心(改造后的最终版):
```python
class LLMClient:
    def __init__(self, provider, model, api_key, base_url=None):
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self._raw_client = self._create_client()   # 构造时就建好底层客户端

    @classmethod
    def from_config(cls):                            # ← 本次新增:工厂方法
        from core.config import Config
        return cls(provider=Config.LLM_PROVIDER, model=Config.LLM_MODEL,
                   api_key=Config.LLM_API_KEY or "", base_url=Config.LLM_BASE_URL)

    def _create_client(self):
        if self.provider == "qwen":
            import dashscope                          # 通义千问自家 SDK
            dashscope.api_key = self.api_key
            return dashscope.Generation
        else:
            from openai import OpenAI                 # OpenAI 兼容(DeepSeek 走这)
            return OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(self, messages, tools=None, stream=False):
        if self.provider == "qwen":
            response = self._raw_client.call(
                model=self.model, messages=messages, tools=tools,
                result_format="message")             # 通义特有参数
        else:
            kwargs = {"model": self.model, "messages": messages, "stream": stream}
            if tools:                                 # ← 本次修:没工具就别传 tools
                kwargs["tools"] = tools
            response = self._raw_client.chat.completions.create(**kwargs)
        return self._extract_content(response)        # 归一化

    def _extract_content(self, response):
        if self.provider == "qwen":
            message = response.output.choices[0].message       # 通义的形状
            return {"content": message.get("content",""),
                    "tool_calls": message.get("tool_calls")}
        else:
            message = response.choices[0].message              # OpenAI 的形状
            tool_calls = []
            if message.tool_calls:
                for tc in message.tool_calls:
                    tool_calls.append({"id": tc.id, "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments}})
            return {"content": message.content or "", "tool_calls": tool_calls or None}
```

逐段读:
- **`_create_client`**:按 `provider` 决定底层用哪个 SDK。`qwen` → dashscope;其它(`openai`)→ OpenAI SDK,**`base_url` 在这里注入**(指向 `api.deepseek.com`)。
- **`chat`**:两家请求方式不同(通义是 `.call(...)`,OpenAI 是 `.chat.completions.create(...)`),但**对上层暴露同一个 `chat()` 方法**。
- **`_extract_content`**:两家返回结构不同(通义 `response.output.choices[0]`,OpenAI `response.choices[0]`),这里**抹平成同一个 dict** `{"content":..., "tool_calls":...}`。

> **这就是"抽象层"的全部意义**:上层(Agent)只跟统一的 `chat() → {content, tool_calls}` 打交道,**完全不知道底下是通义还是 DeepSeek**。所以这次"换供应商"能干净替换 —— 归一化早写好了,我们只是把没走抽象的几处接进来。

### 5.3 本次的三个具体改动点

1. **新增 `from_config()`**:把"从配置读 provider/model/key/base_url"集中到一处。以后换供应商只改 `.env`,代码不动(配置与代码分离)。
2. **`tools=None` 时不传 `tools` 字段**:某些 OpenAI 兼容服务收到 `tools: null` 会报错。Nexus 的 agent 不用工具,所以加了 `if tools:` 的判断。
3. **配置通用化 + 向后兼容**(`core/config.py`):
```python
LLM_BASE_URL = os.environ.get("LLM_BASE_URL")
LLM_API_KEY  = os.environ.get("LLM_API_KEY") or os.environ.get("DASHSCOPE_API_KEY", "")
JINA_API_KEY = os.environ.get("JINA_API_KEY", "")
```
> `LLM_API_KEY or DASHSCOPE_API_KEY` 这个回退:旧变量还在用也不会突然失效。**改造时保留旧路径兼容,是降风险的常用手法。**

### 5.4 之前的问题:抽象有,但没人用

勘探发现:`LLMClient` 早就存在,但**只有 Nexus 用它**;`core/agent.py`(RAG 用)和 `backends/fc_app/main.py`(FC 用)都**各自硬编码直连通义**:
```python
# 改造前,agent.py / fc_app 里都是这种:
response = dashscope.Generation.call(model=..., messages=..., tools=TOOLS,
                                     result_format="message")
choice = response.output.choices[0]      # 通义专属解析
```
> 本次重构的实质:**把这三处硬编码,全部改成走 `LLMClient.from_config().chat()`。** 一旦都走抽象,"切供应商"就只是改 `.env`。这也是"为什么之前埋了抽象、这次才真正受益"。

**动手**:打开 `core/llm.py`,对照上面逐行读一遍;再用 `curl` 亲手打一次 DeepSeek 的 `/chat/completions`,把返回的 JSON 和 `_extract_content` 的解析对上号。

---

## 6. Function Calling 原理(真实 JSON + 多轮循环全代码)

RAG 和 FC 都是"会用工具的 Agent"。这是 LLM 应用的核心机制,讲透。

### 6.1 普通聊天 vs Function Calling

> **普通聊天**:你问,模型用文字答。模型只有训练时的知识,不能查你的数据库、不能算精确数、不能读你的文件。
> **Function Calling(函数/工具调用)**:你额外告诉模型"你有这些工具"(每个工具有名字、说明、参数)。模型遇到需要工具的问题时,**不直接答,而是返回一个结构化的"我要调用 X(参数 Y)"**;你的代码真去执行,把结果喂回去,模型再据此作答。

一次带工具的对话,本质是这个**循环**:
```
用户问"什么是装饰器"
  └─▶ 模型:"我要调 search_docs(query='Python 装饰器')"   ← 模型不直接答,先要工具
       └─▶ 你的代码执行 search_docs,得到文档片段
            └─▶ 把片段作为 role=tool 的消息回填,再问模型
                 └─▶ 模型:基于片段用文字回答   ← 这轮没有 tool_calls,循环结束
```

### 6.2 工具的"自我介绍":tools schema(真实定义)

`core/tools.py` 里,每个工具用一段 JSON 描述给模型:
```json
{
  "type": "function",
  "function": {
    "name": "search_docs",
    "description": "从知识库中检索与问题相关的文档片段，用于回答需要依据文档内容的问题",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {"type": "string", "description": "检索查询，应是具体的问题或关键词"}
      },
      "required": ["query"]
    }
  }
}
```
> 字段含义:`name` 模型用来指定调哪个;`description` 模型据此判断**何时用**;`parameters` 用 [JSON Schema](https://json-schema.org/) 描述参数的类型/必填。
> **刻进脑子的一句话**:模型对工具的全部认知,就来自这段 `description` 和 `parameters`。它看不到工具的源码。**描述写得准不准,直接决定模型用得对不对**(§8 的 bug 就栽在这)。

### 6.3 多轮循环全代码(`core/agent.py`,改造后)

```python
def chat(self, user_input):
    self.messages.append({"role": "user", "content": user_input})
    tool_calls_log = []

    for turn in range(self.max_turns):                 # max_turns = 5,防死循环
        message = self.llm.chat(                        # ← 走抽象层,返回统一 dict
            [self.system_message] + self.messages, tools=TOOLS)

        if message.get("tool_calls"):                   # 模型要求调工具
            for tc in message["tool_calls"]:
                tool_calls_log.append({
                    "name": tc["function"]["name"],
                    "arguments": json.loads(tc["function"]["arguments"])})
            self._handle_tool_calls(message)            # 执行工具 + 把结果回填
            continue                                    # 再循环,带着工具结果重新问模型
        else:
            answer = message["content"]                 # 没有 tool_calls = 最终答案
            self.messages.append({"role": "assistant", "content": answer})
            return {"answer": answer, "tool_calls": tool_calls_log, "error": False}

    return {"answer": "处理时间过长，请简化您的问题后重试।", ...}   # 5 轮没收敛
```

`_handle_tool_calls` 做两件事:把模型的 tool_calls 作为 assistant 消息加入历史,然后逐个执行工具、把结果作为 `role=tool` 消息回填:
```python
def _handle_tool_calls(self, message):
    # 1) 把"模型决定调哪些工具"记进对话历史(assistant 角色)
    self.messages.append({
        "role": "assistant", "content": message.get("content",""),
        "tool_calls": [{"id": tc["id"], "type":"function",
                        "function": {"name": tc["function"]["name"],
                                     "arguments": tc["function"]["arguments"]}}
                       for tc in message["tool_calls"]]})
    # 2) 逐个执行,结果作为 tool 消息回填(靠 tool_call_id 和上面对应)
    for tool_call in message["tool_calls"]:
        name = tool_call["function"]["name"]
        args = json.loads(tool_call["function"]["arguments"])   # arguments 是 JSON 字符串
        result = TOOL_MAP[name](**args) if name in TOOL_MAP else f"未知工具 {name}"
        self.messages.append({"role": "tool", "content": result,
                              "tool_call_id": tool_call["id"]})
```

> **几个易错细节(精确点):**
> - `arguments` 是个 **JSON 字符串**(不是 dict),所以要 `json.loads`。模型生成的是文本,参数也是文本形式的 JSON。
> - 每个 tool_call 有个 `id`;回填结果时用 `tool_call_id` 指回去,**告诉模型"这是你那个调用的结果"**。多个工具并行调用时全靠这个 id 配对。
> - 对话历史里出现三种 role:`user`(你)、`assistant`(模型,可能带 tool_calls)、`tool`(工具结果)。下一轮把整段历史再发给模型,它就有了"我刚调了工具、结果是这个"的上下文。

### 6.4 `max_turns` 是干嘛的

> **防止模型陷入"调工具→看结果→又调工具→……"永不收敛。** 到 5 轮还没给出"没有 tool_calls 的最终答案"就强制停,返回"处理时间过长"。**§8 的 bug 正是触发了这个保护。**

### 6.5 真实成功案例(FC 的天气工具)

本地实测 `/fc/` 问"北京今天天气怎么样",真实返回:
```json
{"answer": "北京今天天气不错，**晴天**，气温 **25°C**，空气质量 **良**...",
 "tool_calls": [{"name": "get_weather", "arguments": {"city": "北京"}}]}
```
> 读这条:模型先返回 tool_calls 要调 `get_weather(city="北京")`;代码执行(假数据返回晴天 25°C);回填后模型组织成最终中文回答。`tool_calls` 字段记录了这次确实用了工具。**这证明换 DeepSeek 后,整个 Function Calling 循环跑通了。**

**动手**:在 `core/tools.py` 里给 Agent 加一个新工具(比如 `get_time()`),写好 schema,问一个会触发它的问题,看 tool_calls 日志。

---

## 7. Embeddings 与向量检索:RAG 的另一半

### 7.1 什么是 Embedding

> **术语:Embedding(向量/嵌入)。** 把一段文字交给 embedding 模型,它输出一串定长的数字(如 1024 个浮点数),叫"向量"。这串数字是这段文字**语义的坐标**。核心性质:**语义相近的文字,向量在空间里也相近。**

真实例子(从服务器实测 Jina):
```bash
$ curl https://api.jina.ai/v1/embeddings -H "Authorization: Bearer $JINA_API_KEY" \
   -d '{"model":"jina-embeddings-v3","task":"retrieval.passage","input":["测试文本"]}'
{"model":"jina-embeddings-v3","data":[{"index":0,
  "embedding":[0.03137793,-0.0162,0.12234088, ...(共1024个数)... ]}],
 "usage":{"total_tokens":14}}
```
> "测试文本"这四个字 → 变成 1024 个浮点数。这就是它的"语义坐标"。

### 7.2 怎么用向量"找相关":相似度

> **怎么判断两段文字语义近?** 算它们向量的**余弦相似度**(cosine similarity):把两个向量看成空间里的两个箭头,算它们夹角的余弦。
> - 夹角小(指向几乎同向)→ 余弦接近 1 → 语义很近。
> - 垂直 → 余弦 0 → 不相关。
> 公式:`cos(A,B) = (A·B) / (|A|·|B|)`(点积除以两个模长)。你不用手算,向量库(Chroma)内置了。

### 7.3 向量检索 = RAG 的"检索"环节(全流程)

```
【建库阶段(启动时跑一次)】
  文档 ─loader─▶ 原文 ─splitter─▶ 切成小块(500字/块) ─embedding─▶ 每块一个向量 ─▶ 存进 Chroma
【查询阶段(每次提问)】
  用户问题 ─embedding─▶ 问题向量 ─▶ Chroma 里找余弦最近的 k 块 ─▶ 返回这几块原文
```
本项目代码位置:`rag/loader.py`(加载)→ `rag/splitter.py`(切块)→ `rag/vectorstore.py`(embedding+存)→ `rag/retriever.py`(查询找最近)。检索到的原文,再交给 DeepSeek 组织答案 —— 这套"**检索 + 生成**"就是 **RAG(Retrieval-Augmented Generation)**。

真实检索输出(服务器上,问"Python 是谁创建的"):
```
检索到以下相关片段：
[1] Python 编程指南  第一章：Python 简介  Python 是一种高级、解释型、通用的编程语言。
    它由 Guido van Rossum 于 1991 年创建...
```
然后 RAG 的最终回答:
```
根据之前检索到的知识库内容：
> Python 是由 Guido van Rossum（吉多·范罗苏姆）于 1991 年创建的。
```
> **这证明 Jina embedding 全链路通了**:建库(把指南切块算向量)+ 查询(问题算向量找最近块)+ 生成(DeepSeek 据片段作答)。

### 7.4 为什么换 embedding 模型必须重建整个索引

通义的 `text-embedding-v3` 和 Jina 的 `jina-embeddings-v3`,**向量维度和"坐标系"都不同**。

> **因果:为什么不能混用?** 库里存的是旧模型(通义)的向量,查询时用新模型(Jina)的向量 —— **两套坐标系对不上**,"找最近"算出来是噪声。
> 所以换了 embedding 模型,**旧的 `chroma_db` 必须删掉,用新模型重新建库**。部署时就执行了 `rm -rf chroma_db`,让容器启动时用 Jina 重新建(实测日志 `[+] 构建向量数据库... RAG 工具初始化完成: 7 个文本块`)。
> 补充:`chroma_db` 在 `.gitignore` 里、也没打进镜像,所以每个新容器启动时都会现建。语料就 7 块,调 Jina 算 7 次向量,很快。

### 7.5 为什么手写 Jina 客户端(完整代码)

`rag/vectorstore.py` 里手写了个最小客户端,而不是用 langchain 自带的:
```python
class JinaEmbeddings:
    """最小 Jina 客户端,兼容 LangChain Embeddings 接口(Chroma 只需这两个方法)。"""
    def __init__(self, api_key, model="jina-embeddings-v3"):
        self.api_key = api_key; self.model = model

    def _embed(self, texts, task):
        resp = requests.post("https://api.jina.ai/v1/embeddings",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": self.model, "task": task, "input": texts}, timeout=30)
        resp.raise_for_status()
        data = resp.json()["data"]
        data.sort(key=lambda d: d["index"])           # 按 index 排,保证顺序对应输入
        return [d["embedding"] for d in data]

    def embed_documents(self, texts):                  # 建库:一批文本块 → 一批向量
        return self._embed(texts, task="retrieval.passage")
    def embed_query(self, text):                        # 查询:一个问题 → 一个向量
        return self._embed([text], task="retrieval.query")[0]
```
> **为什么不用 langchain 的 `JinaEmbeddings`?** 避免第三方封装的版本差异/暗坑。Chroma 需要的接口就两个方法(`embed_documents`/`embed_query`),自己写更透明可控。这是"**少依赖、可掌控**"的取舍。
> **`task` 参数(Jina v3 特性)**:建库用 `retrieval.passage`(这是"文档"),查询用 `retrieval.query`(这是"问题")。告诉模型这段文字的用途,**同一句话作为"文档"和作为"问题"算出的向量略有侧重**,检索更准。

### 7.6 本地 vs 托管 embedding(为什么没选本地)

| | 本地模型(sentence-transformers + torch) | Jina 托管 |
|---|---|---|
| 服务器负担 | 装 torch ~1GB,常驻内存 ~300-500MB | **零内存/磁盘负担** |
| 网络依赖 | 无(算法在本地跑) | 多一个海外 API(已实测可达) |
| 适合 | 内存充裕的机器 | **2GB 小机器(本项目)** |

服务器只有 1.6G 内存 + 2G swap,选了零负担的 Jina。

> **一个本地踩到的现象(值得记)**:在中国本机用 `curl` 直连 `api.jina.ai` **超时(000)**,但**本地 Docker 容器内却能连通**(成功建库)。说明 Docker Desktop 的网络出口和宿主机的不一样。**所以本地 RAG 检索由容器跑没problem,只是宿主机 `curl` 测不了。** ——再次印证"在哪运行在哪测"。

**动手**:把 `docs/python_guide.txt` 加几段你自己的内容,删掉 `chroma_db`,重启 rag 容器,问一个新内容相关的问题,看是否检索到。

---

## 8. 案例精讲:被 DeepSeek "用出来"的老 bug

本次最有教学价值的一段。

### 8.1 现象(真实日志)

切 DeepSeek 后,`/rag/` 问"什么是 Python 装饰器",返回 **"处理时间过长"**。容器日志:
```
[工具] search_docs({"query": "Python 装饰器 decorator"})
[工具返回] 检索到以下相关片段：...
[工具] execute_python({"code": "def my_decorator(func):\n    def wrapper():\n        ..."})
[工具返回] Error: syntax error - invalid syntax (<unknown>, line 2)
[工具] execute_python({"code": "# simple decorator...\ndef my_decorator(func): ..."})
[工具返回] Error: syntax error - invalid syntax (<unknown>, line 2)
[工具] execute_python({"code": "def my_decorator(func): ..."})       ← 第3次
[工具返回] Error: syntax error - invalid syntax (<unknown>, line 1)
[工具] execute_python({"code": ...})                                  ← 第4次,然后 max_turns
```
模型发的是**合法的** Python 装饰器代码,却报"语法错误",于是换个写法再试,4 次后撞上 `max_turns=5`。

### 8.2 根因:`execute_python` 名不副实(看源码)

```python
def safe_execute_python(code: str) -> str:
    code = code.strip()
    tree = ast.parse(code, mode='eval')      # ← 罪魁
    result = _eval_node(tree)
    return str(result)
```
> **术语:`ast.parse(code, mode='eval')` vs `mode='exec'`。**
> - `mode='eval'`:只能解析**单个表达式**(有返回值的那种,如 `2+3*4`、`[1,2]+[3]`)。**不能有 `def`、`print`、赋值、多行语句** —— 这些是"语句(statement)"不是"表达式(expression)"。
> - `mode='exec'`:能解析完整程序(多行、def、print……)。
>
> 这个函数用了 `mode='eval'`,本质是个**算术计算器**,不是通用 Python 执行器。给它一个 `def`,`ast.parse` 直接抛 `SyntaxError`(所以报在 `line 2`,即 `def` 那行)。
>
> 但工具的 `description` 写的是"安全执行一段受限的 Python 表达式,用于数学计算、数据结构验证等" —— **听起来像能跑程序。**

### 8.3 为什么通义没事、DeepSeek 才爆(因果链)

> 工具描述模糊 → **不同模型理解不同**。
> 通义千问较少主动调 `execute_python`,或只发简单表达式 → 不触发。
> DeepSeek **更"积极"用工具**:看到"装饰器",它想"写段 `def` 代码演示给用户" → 发给只认表达式的计算器 → `SyntaxError` → 它以为自己代码写错了,换个写法重试 → 死循环 → `max_turns` → "处理时间过长"。
>
> **这是个潜伏的老 bug:实现和描述早就不一致,通义没把它"用出来",DeepSeek 把它暴露了。** 换更主动的模型 = 把系统里所有"描述与实现不符"的地方都照一遍。

### 8.4 修法:让描述对齐实现 + 引导模型(三处改)

不是去扩 `execute_python` 的能力(那要做安全沙箱,超范围),而是**让描述诚实、报错会"教"模型、prompt 不诱导**:

1. **工具描述**(`core/tools.py`)改成强约束:
```python
"description": "纯算术计算器：只能计算单个算术表达式(数字四则运算、列表/字典字面量、索引)。
                不能定义函数、不能用 print、不能写多行代码或语句。
                只在需要精确数字计算时调用,其它问题请直接用文字回答。"
```
2. **报错信息**改成会引导模型停手:
```python
except SyntaxError as e:
    return ("Error: 本工具只支持单个算术表达式(如 2+3*4),不支持 def/print/import/语句/多行代码。"
            "请不要再调用本工具,直接用文字回答用户。")
```
3. **system prompt**(`core/agent.py`)松绑:把原来"**必须**用 execute_python"改成 "先用 search_docs 检索,然后**直接根据检索结果用文字回答**;execute_python 只是算术计算器,别拿它写示例代码"。

修完实测同一个问题,干净作答、无 loop。

> **教训(记一辈子):工具的 `description` 是模型唯一的"使用说明书"。描述和真实能力一旦不一致,迟早出事 —— 换个更主动的模型就触发。写工具时,描述必须诚实反映实现的边界。**

---

## 9. SSE 与 Nexus 多 agent(以及遗留的 async bug)

### 9.1 什么是 SSE

> **术语:SSE(Server-Sent Events,服务器推送事件)。** 普通 HTTP 是"一问一答":你发请求,服务器回一坨数据,结束。SSE 让服务器**保持连接、持续往客户端推一条条事件**,适合"实时进度"。Nexus 的多 agent 流程边想边推:`planner_thought`、`tool_call`、`tool_result`、`final_answer`……前端实时显示。
> 格式就是纯文本流,每条事件:`event: 类型\ndata: {json}\n\n`。

真实输出(服务器,问"用一句话介绍Python"):
```
event: planner_thought
data: {"content": "Plan generated: [{'step_id':1,'agent':'retriever',...}]"}

event: tool_call
data: {"agent":"retriever","tool":"search","args":{"query":"..."}}

event: tool_result
data: {"agent":"retriever","result":[{"content":"检索失败：object Response can't be used in 'await' expression",...}]}

event: final_answer
data: {"content":"Python是一种广泛使用的高级编程语言...", "critique":{"scores":{...},"passed":true}}
```

### 9.2 遗留 bug(明天的任务):同步/异步混用

注意上面的 `tool_result`:`检索失败：object Response can't be used in 'await' expression`。

> **术语:同步(sync)vs 异步(async)。**
> - 同步函数:调用就阻塞等结果,`r = client.get(url)`。
> - 异步函数:返回一个"协程/future",要 `await` 才拿到结果,`r = await client.get(url)`。
> - 关键:**只能 `await` 异步对象。`await` 一个同步函数的返回值 → 报 `object X can't be used in 'await' expression`。**
>
> 这条报错的意思:Nexus 的 retriever 里,某处对一个**同步的 httpx 返回值用了 `await`**(或反过来,异步上下文里用了同步 client)。后果:retriever 调 rag_app 的检索**直接失败**,所以 `result` 是"检索失败"。但因为 Nexus 的 LLM(DeepSeek)能凭自身知识答,`final_answer` 照样出来 —— **所以 `/nexus/` 表面正常,实际"检索"那一环是空转的。**
>
> **这与本次 provider 切换无关**(是 httpx 用法问题),所以留作明天单独修。定位起点:`core/agents/retriever.py`,找对 rag_app 的 HTTP 调用,核对用的是 `httpx.AsyncClient` 还是 `httpx.Client`、有没有该 `await` 的没 await / 不该 await 的 await 了。

---

## 10. 验证方法论:为什么"200 不算数"

> 反复强调:**"路由返回 200" ≠ "功能正常"。**

- 200 只说明"网页/接口能打开"。功能对不对,**必须发真实请求看真实结果**。
- **真实反例(上一轮)**:黑白改版部署后 `/iconforge/` 返回 200,点进去却是**空白页**(React 路由表漏了 `/iconforge`)。`curl` 测全是 200,把人骗了 —— 因为 nginx 把 index.html 返回了(200),但前端 JS 路由匹配不到。**只有用浏览器真点 / 或检查 bundle 里有没有这条路由,才暴露。**
- **这次的验证都打到"行为"层**:
  - FC:问天气 → 看是否真的触发 `get_weather` 且答出温度。
  - RAG:问**语料里确实有的**问题("Python 谁创建") → 看是否检索到正确片段(而不是问语料里没有的"装饰器",那样分不清是检索失败还是语料没有)。
  - Nexus:看是否吐 `final_answer`。
- **可达性都从服务器侧实测**(不是从本机猜):本机(中国)连不上 Jina,服务器(韩国)连得上。**在哪运行就在哪测。**
- **key 也先单独验**:部署前先用 `curl` 拿真实 key 打一次 DeepSeek、打一次 Jina,确认是 200/有数据,再动整个栈 —— **fail fast,别等整栈起来才发现 key 错。**

> 方法论凝练:**①验证打到"行为"层不是"状态码"层;②在"真实运行环境"测不是开发机猜;③外部依赖先单点验证再集成(fail fast)。**

---

## 11. 本次改动清单(文件级,便于复盘)

| 文件 | 改了什么 | 为什么 |
|---|---|---|
| `core/config.py` | 加 `LLM_BASE_URL/LLM_API_KEY/JINA_API_KEY`,带回退 | 配置通用化 |
| `core/llm.py` | 加 `from_config()`;`tools=None` 时不传该字段 | 集中读配置 + 兼容性 |
| `core/agent.py` | 直连 dashscope → `LLMClient`;改 system prompt | RAG 聊天走抽象 + 防 loop |
| `backends/fc_app/main.py` | 同上;`Dockerfile` 加 `COPY core/` | FC 聊天走抽象(需要 import core) |
| `eval/evaluator.py` | 直连 dashscope → `LLMClient` | LLM 评分也走抽象 |
| `backends/nexus_app/main.py` | `LLMClient.from_config()`;key 门槛改 `LLM_API_KEY` | 统一 |
| `rag/vectorstore.py` | `DashScopeEmbeddings` → 手写 `JinaEmbeddings` | embedding 换 Jina |
| `core/rag_tool.py` | key 门槛 `DASHSCOPE` → `JINA_API_KEY` | embedding 现在用 Jina key |
| `core/tools.py` | `execute_python` 描述/报错对齐实现 | 修 loop bug |
| `requirements.txt` / `nexus/requirements.txt` | 加 `openai` | 用 OpenAI SDK |
| `.env.example` | 通用键 + DeepSeek/Jina 示例 | 文档 |
| `tests/nexus/test_api.py` | 断言 `LLM_API_KEY` 而非 `DASHSCOPE_API_KEY` | 跟随 key 门槛改动 |

**部署步骤**:服务器 `.env` 改新键 → `git pull` → `rm -rf chroma_db` → `docker compose ... up -d --build rag fc nexus` → 从服务器侧实测三 demo。

---

## 12. 系统学习路径 + 自测题(带答案要点)

### 12.1 想吃透,按这个顺序补

1. **HTTP/网络基础**:状态码(2xx/4xx/5xx)、TCP/TLS、`curl` 的 `-w/-o/--resolve/-4/-6`。动手:对任意 API 跑一遍 §2 的诊断命令。
2. **DNS 与 CDN/GTM**:域名→IP、同名不同地区不同 IP。
3. **OpenAI API 规范**:`/chat/completions` 的请求/返回结构、`tools`/`tool_calls`。动手:`curl` 打一次 DeepSeek(§5.1 有真实例子)。
4. **Function Calling 全流程**:亲手实现一遍"模型要工具→执行→回填→作答"(§6 的循环)。
5. **Embeddings & 向量库**:embedding 是什么、余弦相似度、Chroma 存/查;为什么换模型要重建(§7)。
6. **async/await**:同步 vs 异步、`httpx.Client` vs `AsyncClient`(为修 §9 那个 bug 打底)。

### 12.2 自测题(能脱口答出即懂)

1. `curl` 返回 `000` 和 `401`,分别说明问题在哪一层?修法有何不同?
   <br>*要点:000=网络层(DNS/路由/TCP/TLS)没连上;401=网络通了、应用层鉴权失败。前者查网络,后者查 key/账号。*
2. 为什么大陆 dashscope key 打国际端点是 401 而不是超时?
   <br>*要点:能拿到状态码=网络通;401=大陆/国际是两套独立账号库,key 查无此人。*
3. DeepSeek 国内账号的 key 为什么能从韩国服务器调用?和阿里云区别在哪?
   <br>*要点:DeepSeek 单一平台、key 不绑区域、API 在全球可达云上;阿里云大陆/国际分裂。*
4. "OpenAI 兼容"具体兼容什么?为什么让"换供应商"变成"改两行配置"?
   <br>*要点:兼容请求/返回的 HTTP 结构;同一 SDK 只换 base_url+key;配合 LLMClient 的归一化,上层无感。*
5. Function Calling 里 `max_turns` 干嘛?这次为什么被触发?
   <br>*要点:防工具调用死循环;execute_python 对合法程序报语法错→模型反复重试→撞上限。*
6. 为什么换 embedding 模型,旧 `chroma_db` 必须删掉重建?
   <br>*要点:不同模型向量维度/坐标系不同,混用导致"找最近"失真。*
7. `execute_python` bug 的真正根因?为什么通义没事 DeepSeek 才爆?给写工具什么启示?
   <br>*要点:`ast.parse(mode='eval')` 只认表达式但描述像通用执行器;DeepSeek 更主动调它发程序触发;启示=工具描述必须对齐实现边界。*
8. 为什么说"路由 200 不等于功能正常"?各举一例。
   <br>*要点:200 只表示能打开;iconforge 空白页(路由漏)、RAG 要问语料内问题才验得准。*
9. Nexus 那条 `object Response can't be used in 'await'` 说明什么?往哪修?
   <br>*要点:对同步返回值用了 await(或异步上下文用了同步 client);看 retriever 的 httpx 用法。*

### 12.3 进阶可挖

- DeepSeek 现在的模型矩阵与定价(`deepseek-chat` 实际指向 `deepseek-v4-flash`)。
- Jina v3 的 `task` 参数(retrieval.passage/query/separation/classification)各适合什么场景。
- Chroma 底层:HNSW 近似最近邻索引怎么做到"在百万向量里快速找最近"。
- 给 `safe_execute_python` 做一个真正的安全沙箱(`mode='exec'` + 限制内置函数),需要注意哪些安全点。

---

> **本文配套**:同目录有 `.html` 和 `.docx` 版本(便于阅读/打印)。源码改动见 git 历史 `a82b450`(迁移)、`a82b450`(execute_python 修复)。下一步见 `docs/PROJECT-STATE.md` 第 0 条。
