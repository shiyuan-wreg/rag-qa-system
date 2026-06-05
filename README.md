# RAG 智能文档问答系统

基于检索增强生成（Retrieval-Augmented Generation）技术的文档问答 Demo，支持上传 PDF/TXT 文档后通过自然语言提问获取精准回答。

## 项目概述

传统的大模型问答存在两个痛点：
1. **知识滞后**：模型训练数据有截止日期，无法回答最新信息
2. **幻觉问题**：对于专业领域内容，模型可能编造不存在的知识

RAG（检索增强生成）通过将用户私有文档向量化存储，在问答时先检索相关片段再交给大模型生成答案，既解决了知识更新问题，又显著降低了幻觉风险。

## 技术栈

| 层级 | 技术 | 说明 |
|---|---|---|
| 大模型 | 通义千问 (qwen-turbo) | 阿里云百炼平台，免费额度充足 |
| 向量嵌入 | text-embedding-v3 | 通义千问 Embedding 模型，1024 维 |
| 向量数据库 | Chroma | 轻量级、纯 Python、本地持久化 |
| 文档加载 | LangChain (TextLoader / PyPDFLoader) | 支持 TXT / PDF 格式 |
| 文本分块 | RecursiveCharacterTextSplitter | 按语义边界递归切分 |
| Web 框架 | FastAPI | 高性能异步 Web 框架 |
| 前端 | 原生 HTML + CSS + JS | 拖拽上传、对话式交互 |

## 功能特性

- [x] 支持 TXT / PDF 文档上传与解析
- [x] 文档自动切分、向量化、入库
- [x] 基于向量相似度检索相关文本片段
- [x] 结合检索结果调用大模型生成精准回答
- [x] 提供 Web 可视化界面（上传 + 对话）
- [x] 支持 curl / Postman 调用 REST API

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/你的用户名/rag-qa-system.git
cd rag-qa-system
```

### 2. 配置环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境（Windows）
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置 API Key

```bash
# 复制模板
cp .env.example .env

# 编辑 .env，填入你的通义千问 API Key
# 从阿里云百炼获取: https://bailian.console.aliyun.com/
```

### 4. 运行

```bash
# 方式一：FastAPI Web 服务
python -m uvicorn app:app --reload

# 方式二：命令行交互（纯 RAG 核心）
python rag.py
```

打开浏览器访问: http://127.0.0.1:8000

## 项目结构

```
rag-qa-system/
├── app.py                      # FastAPI 主应用（Web 服务）
├── rag.py                      # 完整 RAG 流程（命令行版）
├── step1_load_docs.py          # Step 1: 文档加载（学习用）
├── step2_split_text.py         # Step 2: 文本分块（学习用）
├── step3_build_vectorstore.py  # Step 3: 向量化 + 建库（学习用）
├── step4_rag_qa.py             # Step 4: 检索 + 问答（学习用）
├── test_api.py                 # API 连通性测试
├── sample_docs/                # 示例文档
│   └── python_guide.txt
├── .env.example                # 环境变量模板
├── .gitignore                  # Git 忽略规则
├── requirements.txt            # 依赖列表
└── README.md                   # 本文件
```

## RAG 核心流程

```
用户上传文档
    │
    ▼
┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│ Document    │───▶│ Recursive    │───▶│ Chroma       │
│ Loader      │    │ TextSplitter │    │ Vector Store │
│ (PDF/TXT)   │    │ (chunk_size) │    │ (Embedding)  │
└─────────────┘    └──────────────┘    └──────────────┘
                                              │
用户提问 ──▶ 问题向量化 ──▶ 相似度检索 ────────┘
                                              │
                                              ▼
                                    ┌──────────────┐
                                    │ 相关文本片段  │
                                    └──────────────┘
                                              │
                                              ▼
                                    ┌──────────────┐
                                    │ Prompt 拼接   │
                                    │ 系统指令 +    │
                                    │ 上下文 + 问题 │
                                    └──────────────┘
                                              │
                                              ▼
                                    ┌──────────────┐
                                    │ LLM (通义千问)│
                                    │ 生成最终答案  │
                                    └──────────────┘
```

## API 接口

### 上传文档

```bash
curl -X POST "http://127.0.0.1:8000/upload" \
     -F "file=@你的文档.pdf"
```

响应:
```json
{
  "message": "上传成功",
  "filename": "你的文档.pdf",
  "chunks": 15
}
```

### 问答

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "query=Python的异常处理怎么做"
```

响应:
```json
{
  "answer": "根据参考资料，Python 使用 try-except 语句处理异常...",
  "sources": [
    {"index": 1, "content": "try-except 语句用于捕获和处理异常..."},
    {"index": 2, "content": "finally 块中的代码无论是否发生异常都会执行..."}
  ]
}
```

## 核心参数说明

| 参数 | 默认值 | 说明 |
|---|---|---|
| `CHUNK_SIZE` | 500 | 每个文本块最大字符数，越大上下文越完整，检索精度可能下降 |
| `CHUNK_OVERLAP` | 50 | 块间重叠字符数，避免关键信息被切断 |
| `TOP_K` | 3 | 检索时返回最相关的片段数量 |
| `MODEL` | qwen-turbo | 大模型，可选 qwen-plus（更强但更贵）|

## 学习路径

本项目按 RAG 流水线拆分为 4 个学习脚本，建议按顺序阅读：

1. `step1_load_docs.py` — 理解 Document 对象和文档加载
2. `step2_split_text.py` — 理解为什么分块、chunk_size 和 overlap 的作用
3. `step3_build_vectorstore.py` — 理解 Embedding 和向量数据库
4. `step4_rag_qa.py` — 理解完整的检索 + 生成流程

## 演示截图

> 截图待补充：上传文档界面、问答对话界面

## 待优化项

- [ ] 支持更多文档格式（Word、Markdown）
- [ ] 接入真实天气/邮件等外部工具（转向 Agent 架构）
- [ ] 多轮对话上下文管理
- [ ] 生产环境部署（Docker + Gunicorn）

## 参考资源

- [LangChain RAG 官方教程](https://python.langchain.com/docs/tutorials/rag/)
- [通义千问 API 文档](https://help.aliyun.com/document_detail/611472.html)
- [Chroma 文档](https://docs.trychroma.com/)

## License

MIT
