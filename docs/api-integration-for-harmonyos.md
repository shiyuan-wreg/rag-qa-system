# ai-demos Agent 问答 API —— 对接指南(供鸿蒙端开发者/AI 阅读)

> **读者**:你是负责 **HarmonyOS(鸿蒙)端**「agent-console-ai」课程设计的开发者或 AI。
> **目的**:本文件告诉你如何让鸿蒙 App **通过 HTTP 调用 ai-demos 已实现的 Agent 问答能力**(RAG 文档问答 / Function Calling 工具问答),从而"沿用"其功能,而**无需把 ai-demos 的代码拷进鸿蒙项目**。
> **关系**:agent-console-ai 与 ai-demos 是**两个独立项目**。两者不合并代码、不共用仓库;鸿蒙端只作为 HTTP 客户端消费 ai-demos 暴露的接口。

---

## 1. 大图景

ai-demos 把两个 AI 能力做成了标准的 HTTP 服务(FastAPI),统一经 Nginx 对外:

| 能力 | 路径前缀 | 说明 |
|---|---|---|
| RAG 文档问答 | `/rag` | 基于私有知识库的检索增强问答,可调用 search_docs 等工具 |
| Function Calling 问答 | `/fc` | 大模型自动决策调用工具(天气/计算等) |

鸿蒙 App 本质是一个 HTTP 客户端(用 `@ohos.net.http`)。你只要向这些接口发请求、解析 JSON 即可——和调用任何 REST 后端一样。

---

## 2. Base URL

| 环境 | Base URL |
|---|---|
| 本地开发(ai-demos 在开发机用 docker-compose 跑) | `http://<开发机局域网IP>:8080`(鸿蒙真机不能用 127.0.0.1,要用开发机在局域网里的 IP,如 `http://192.168.x.x:8080`) |
| 部署后(ai-demos 上线到服务器+域名后) | `https://<ai-demos 的域名>` |

> 模拟器/真机访问"localhost"指的是设备自己,**不是你的开发机**。本地联调请用开发机局域网 IP,并确保两者同一 WiFi、开发机防火墙放行 8080。

---

## 3. 接口契约

所有接口都在上面的 Base URL 之后拼接。

### 3.1 POST `/rag/chat` —— RAG 问答

- **请求**:`Content-Type: application/x-www-form-urlencoded`(⚠️ **是表单,不是 JSON**),字段:
  - `query`(string,必填):用户问题
- **响应**:`200`,JSON:
  ```json
  {
    "answer": "字符串,模型最终回答",
    "tool_calls": [ { "...": "本轮调用过的工具记录(数组,可能为空)" } ],
    "error": false
  }
  ```
- **出错**:`{"error": "API Key 未配置"}`,HTTP 500。

### 3.2 POST `/fc/chat` —— Function Calling 问答

- **请求**:同上,表单字段 `query`。
- **响应**:JSON,结构同 `/rag/chat`(`answer` + `tool_calls`)。例如问"北京今天天气",`tool_calls` 会包含天气工具的调用记录。

### 3.3 POST `/rag/clear` 、 POST `/fc/clear` —— 清空对话历史

- **请求**:无 body。
- **响应**:`{"message": "对话历史已清空"}`。

### 3.4 POST `/rag/eval` —— (可选)跑内置评估

- 一般鸿蒙端用不到,跳过。

---

## 4. ⚠️ 必须知道的约束与坑

1. **请求是表单编码,不是 JSON**。鸿蒙端要发 `application/x-www-form-urlencoded`,body 形如 `query=你的问题`。发 JSON body 会失败。
2. **无鉴权**。这两个接口当前没有 token/header 校验(注意:这和 agent-console-ai 自己那套用 `X-Internal-Key` 的后端不同——那是另一个后端)。
3. **单一全局会话**:后端目前用一个全局 Agent 实例保存对话历史,**所有调用方共享同一段历史**,不是按用户/会话隔离的。多用户同时用会串话。课程演示单人使用没问题;若要多用户隔离,需要 ai-demos 后端改造(见第 6 节)。
4. **CORS 不影响你**:CORS 是浏览器机制。鸿蒙原生 HTTP 请求(`@ohos.net.http`)不受 CORS 限制,无需 ai-demos 配 CORS。(若你用的是 Web 组件里的浏览器 fetch,才需要后端加 CORS。)
5. **LLM 是通义千问**(dashscope),响应里中文为主。
6. **响应可能较慢**:每次 `chat` 要等大模型生成,几秒级,鸿蒙端请做好 loading 态与超时(建议 30s)。

---

## 5. 示例

### 5.1 curl(先用它确认接口通)

```bash
# RAG 问答
curl -X POST "http://192.168.1.10:8080/rag/chat" -d "query=列表和元组的区别"
# FC 问答
curl -X POST "http://192.168.1.10:8080/fc/chat"  -d "query=北京今天天气怎么样"
```

### 5.2 鸿蒙 ArkTS(概念示例,@ohos.net.http)

```typescript
import http from '@ohos.net.http';

async function askAgent(baseUrl: string, query: string): Promise<string> {
  const req = http.createHttp();
  const res = await req.request(`${baseUrl}/fc/chat`, {
    method: http.RequestMethod.POST,
    header: { 'Content-Type': 'application/x-www-form-urlencoded' },
    extraData: `query=${encodeURIComponent(query)}`,   // 表单编码,不是 JSON
    connectTimeout: 30000,
    readTimeout: 30000,
  });
  req.destroy();
  const data = JSON.parse(res.result as string);        // { answer, tool_calls, error }
  if (data.error) throw new Error(String(data.error));
  return data.answer as string;
}
```

---

## 6. 如果现有契约不满足你的需求

当前接口是为 ai-demos 自己的网页 demo 设计的(表单入参、全局会话、无鉴权)。如果鸿蒙端需要:
- **JSON 入参**、
- **按设备/用户隔离的多会话**、
- **接口鉴权(token)**、
- **流式返回(SSE)**

这些都属于 **ai-demos 后端的改造**,不应在鸿蒙端硬凑。请把需求提给 ai-demos 一侧(它后续 Phase 计划里本就要做 Nexus Web + SSE)。在那之前,鸿蒙端按本文档第 3 节的现有契约对接即可。

---

## 7. 自包含 vs 沿用(给课程提交的提醒)

如果课程要求作品**能离线、自包含地给老师跑**,那鸿蒙端应继续用 agent-console-ai **自己的后端**(它已有一套基于 Zhipu GLM 的实现)。"沿用 ai-demos" 适用于:ai-demos 已部署上线、现场联网演示时,把请求指向 ai-demos 的 `/rag` 或 `/fc`。两种模式可以并存(配置里切换 Base URL 即可)。

---

> 本文档基于 ai-demos 截至 2026-06-22 的后端实际契约(`backends/rag_app/main.py`、`backends/fc_app/main.py`)编写。若后端接口变更,请同步更新本文件。
