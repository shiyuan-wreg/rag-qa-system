# Kairos 技术概念地图

> 以 Kairos 项目为中心，按层级组织技术概念。每个概念统一使用 7 字段模板。  
> 使用方式：遇到新概念时，先判断它属于哪一层，再按模板补充。

## 使用决策树

```
1. 这个概念在 Kairos 里出现吗？
   ├── 是 → 放入地图对应层级
   └── 否 → 放入"待归档区"
2. 它是基础概念还是高级特性？
   ├── 基础概念 → 填完 7 个字段，能口头解释
   └── 高级特性 → 只填定义/原因/相关概念
3. 它影响项目运行吗？
   ├── 是 → 必须找到代码/配置中的实际使用位置
   └── 否 → 了解即可
4. 我现在能讲清楚吗？
   ├── 能 → 标记 ✅
   └── 不能 → 24 小时内再复习一次
```

## 1. 基础设施层

### 1.1 版本控制

#### Git
#### GitHub

### 1.2 容器化

#### Docker
#### Docker Compose

### 1.3 Web 服务器与代理

#### Nginx

### 1.4 服务器与运维

#### Linux / SSH / 域名与 SSL

## 2. 后端服务层

### 2.1 语言与运行时

#### Python
#### Uvicorn

### 2.2 Web 框架

#### FastAPI

### 2.3 各 demo 后端

#### RAG
#### FC
#### Nexus
#### DocHub
#### IconForge

### 2.4 共享核心模块

#### core/agent.py
#### core/llm.py
#### core/rag_tool.py

## 3. 前端门户层

### 3.1 语言与类型

#### TypeScript
#### JavaScript（ES6+）

### 3.2 UI 框架

#### React

### 3.3 样式

#### TailwindCSS

### 3.4 构建与路由

#### Vite
#### React Router

### 3.5 门户与 demo 集成

#### iframe 嵌入机制

## 4. AI / Agent 能力层

### 4.1 大模型基础

#### LLM（DeepSeek）
#### Token / Prompt / Completion
#### 温度 / 上下文窗口

### 4.2 嵌入与检索

#### Embedding（Jina）
#### 向量数据库（Chroma）

### 4.3 Agent 模式

#### RAG 流程
#### Function Calling
#### Multi-Agent 协作

### 4.4 评估与监控

#### 测试用例 / eval

## 5. 数据与存储层

### 5.1 向量数据

#### Chroma

### 5.2 结构化数据

#### SQLite

### 5.3 文档数据

#### Markdown
#### HTML

### 5.4 静态资源

#### 图片 / 字体 / dist

## 6. 工具链与开发体验

### 6.1 包管理

#### npm
#### pip

### 6.2 测试

#### pytest

### 6.3 终端与脚本

#### Git Bash
#### shell 脚本

### 6.4 AI 辅助开发

#### Claude Code

## 面试问法汇总

（待 Task 8 填充）
