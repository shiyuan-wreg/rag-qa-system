# Agent Console AI Service

Agent Console 的 Python AI 服务，作为 Java 后端与 ai-demos 之间的代理层。

## 职责

- 接收 Java 后端的 `/agent/chat` 请求
- 调用 ai-demos 的 `/fc/chat` 完成 Function Calling
- 实现 Reflection 流程：Draft -> Reflect -> Revise
- 返回完整的调用链路 steps

## 运行

```bash
cd C:\Users\hzs17\Desktop\ai-demos\agent-console-ai
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
python run.py
```

## 配置

复制 `.env.example` 为 `.env`：

```text
AI_DEMOS_BASE_URL=http://localhost:8001
INTERNAL_KEY=changeme
MAX_TIMEOUT=30
```

无需配置 LLM API Key，ai-demos 自己管理 dashscope Key。
