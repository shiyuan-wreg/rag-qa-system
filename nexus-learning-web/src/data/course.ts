import type { Module, Lesson } from '../types/course'

export const modules: Module[] = [
  {
    id: 'fundamentals',
    title: '模块一：LLM 与 Agent 基础',
    description: '理解大语言模型的能力边界、Agent 架构原理和 ReAct 范式',
    order: 1,
    lessons: [
      {
        id: 'llm-basics',
        moduleId: 'fundamentals',
        moduleTitle: '模块一：LLM 与 Agent 基础',
        order: 1,
        title: 'LLM 的能力边界与工程约束',
        description: '从 next-token prediction 出发，理解 Token、上下文窗口、Temperature 等核心概念对工程应用的影响。',
        objectives: [
          '解释 LLM 的 next-token prediction 机制',
          '估算一次 API 调用的 token 消耗和成本',
          '根据场景选择合适的 Temperature',
          '设计避免上下文溢出的提示词结构'
        ],
        prerequisites: [
          'Python 基本数据类型和函数',
          '了解 API 调用（request/response）',
          '能够理解 JSON 格式'
        ],
        keyConcepts: [
          'Autoregressive Generation',
          'Tokenization',
          'Context Window',
          'Temperature / Top-p / Top-k',
          'Prompt Injection'
        ],
        content: `## 1.1 自回归生成的本质

LLM 的核心数学本质是条件概率预测：

\`\`\`
P(token_n | token_1, token_2, ..., token_{n-1})
\`\`\`

给定已生成的所有 token，预测下一个 token 的概率分布，然后采样输出。

**工程影响**：

- **没有真正的推理记忆**：模型只能看到当前上下文内的信息。跨会话需要显式持久化。
- **输出具有随机性**：相同输入可能产生不同输出，关键任务需要低 Temperature 或多次采样。
- **知识边界严格**：模型只能基于训练数据中的模式生成，无法访问私有数据或实时信息。

## 1.2 Token 的经济学

Token 是计费单位，也是性能单位。模型的计费通常按每 1K token 计算。

**成本优化策略**：

- 精简系统提示，避免冗余说明。
- 对历史消息做摘要或截断。
- RAG 只传入相关片段，而非完整文档。
- 使用更便宜的模型处理简单任务。

## 1.3 采样参数的工程选择

**Temperature** 在数学上是对 softmax 输出分布的温度缩放：

\`\`\`
P_i ∝ e^(z_i / T)
\`\`\`

- T → 0：分布趋于尖锐，输出确定。
- T → ∞：分布趋于均匀，输出随机。

| 场景 | Temperature | Top-p | 说明 |
|------|-------------|-------|------|
| 工具调用参数生成 | 0.0 ~ 0.1 | 0.1 | 要求稳定、可解析 |
| JSON 结构化输出 | 0.0 ~ 0.2 | 0.1 | 减少格式错误 |
| 代码生成 | 0.2 ~ 0.4 | 0.5 | 兼顾确定性和多样性 |
| 创意写作 | 0.7 ~ 1.0 | 0.9 | 允许发散 |

## 1.4 上下文窗口与长上下文技术

上下文窗口限制是 RAG 和 Agent 系统存在的根本原因之一。

**应对策略**：

1. **截断**：丢弃最早的消息，简单但可能丢失关键信息。
2. **摘要**：把早期对话压缩成摘要，会损失细节。
3. **RAG 检索**：只在需要时检索相关信息，而非全部塞进上下文。
4. **长上下文模型**：如 GPT-4 128K、Kimi 200K，但成本更高、延迟更大，且存在"中间丢失"问题。`,
        codeLabs: [
          {
            id: 'token-cost',
            title: '上下文成本计算器',
            description: '编写一个函数，估算给定提示和模型的 API 成本。',
            starterCode: `def estimate_cost(system_prompt, user_prompt, input_price, output_price, expected_output_tokens=500):
    # 粗略估算：中文约 1.5 token/字，英文约 1.3 token/word
    input_text = system_prompt + user_prompt
    cn_chars = sum(1 for c in input_text if '一' <= c <= '鿿')
    en_words = len(input_text.split())
    input_tokens = int(cn_chars * 1.5 + en_words * 1.3)

    input_cost = (input_tokens / 1000) * input_price
    output_cost = (expected_output_tokens / 1000) * output_price

    return {
        "input_tokens": input_tokens,
        "output_tokens": expected_output_tokens,
        "total_cost": round(input_cost + output_cost, 6)
    }

print(estimate_cost("你是一位 Python 讲师。", "解释列表和元组区别。", 0.002, 0.006, 300))`,
            expectedOutput: '{"input_tokens": ..., "output_tokens": 300, "total_cost": ...}'
          }
        ],
        quizzes: [
          {
            id: 'q1-1',
            type: 'single',
            question: 'LLM 的核心能力本质上是什么？',
            options: [
              { id: 'a', text: '理解自然语言的语义' },
              { id: 'b', text: '根据前文预测下一个 token' },
              { id: 'c', text: '查询外部数据库' },
              { id: 'd', text: '执行符号推理' }
            ],
            correctAnswer: 'b',
            explanation: 'LLM 的核心是 next-token prediction：给定已生成的 token，预测下一个 token 的概率分布。它没有真正的理解或符号推理能力。'
          },
          {
            id: 'q1-2',
            type: 'single',
            question: '在需要稳定 JSON 输出的场景，Temperature 应该设为多少？',
            options: [
              { id: 'a', text: '0.0 ~ 0.2' },
              { id: 'b', text: '0.5 ~ 0.7' },
              { id: 'c', text: '0.8 ~ 1.0' },
              { id: 'd', text: '越大越好' }
            ],
            correctAnswer: 'a',
            explanation: 'JSON 输出要求格式稳定，Temperature 应接近 0，让模型选择概率最高的 token，减少格式错误。'
          },
          {
            id: 'q1-3',
            type: 'multiple',
            question: '以下哪些是应对长上下文限制的策略？',
            options: [
              { id: 'a', text: '截断早期消息' },
              { id: 'b', text: '对历史消息做摘要' },
              { id: 'c', text: '使用 RAG 只检索相关片段' },
              { id: 'd', text: '无限增加上下文窗口' }
            ],
            correctAnswer: ['a', 'b', 'c'],
            explanation: '截断、摘要、RAG 都是常见策略。上下文窗口受模型架构限制，不能无限增加，且长上下文成本更高。'
          }
        ],
        commonMistakes: [
          '认为 LLM 有真正的记忆，实际上它只在当前上下文内有效。',
          'Temperature 设太低导致创意任务输出重复。',
          '忽略系统提示和工具定义占用的输入 token 成本。',
          '上下文窗口填满后未做截断或摘要导致报错。'
        ],
        furtherReading: [
          { title: 'Attention Is All You Need' },
          { title: 'OpenAI Tokenization 文档' },
          { title: 'Lost in the Middle: How Language Models Use Long Contexts' }
        ],
        checklist: [
          '能解释 next-token prediction 机制',
          '能估算一次 API 调用的 token 成本',
          '能根据场景选择 Temperature 和 Top-p',
          '知道至少两种应对长上下文的方法'
        ]
      },
      {
        id: 'agent-react',
        moduleId: 'fundamentals',
        moduleTitle: '模块一：LLM 与 Agent 基础',
        order: 2,
        title: 'Agent 架构与 ReAct 范式',
        description: '理解 Agent 与普通 LLM 应用的区别，掌握 ReAct 推理-行动循环和 Function Calling 协议。',
        objectives: [
          '区分 LLM 应用、单 Agent、Multi-Agent 的架构差异',
          '用 ReAct 范式设计能调用工具的 Agent',
          '解释 Function Calling 的内部流程',
          '评估场景是否适合用 Agent 解决'
        ],
        prerequisites: [
          '理解 LLM 的概率生成机制',
          '能调用至少一家 LLM API'
        ],
        keyConcepts: [
          'Agent Loop',
          'Observation / Thought / Action',
          'Tool Schema（JSON Schema）',
          'Function Calling',
          'Plan-Execute 模式'
        ],
        content: `## 2.1 从 LLM 应用到 Agent 的演进

| 形态 | 输入 | 处理 | 输出 | 典型场景 |
|------|------|------|------|----------|
| LLM 应用 | prompt | 单次生成 | 文本 | 翻译、摘要 |
| 单 Agent | prompt + 工具 | 多轮思考-行动循环 | 文本/行动 | 计算器、搜索 |
| Multi-Agent | prompt + 工具 + 多个专家 | 任务分发、协作、评估 | 综合结果 | 复杂工作流 |

## 2.2 ReAct 范式的严格定义

ReAct 由 Princeton 和 Google Research 在 2022 年提出，核心思想是将推理（Reasoning）和行动（Acting）交错进行：

\`\`\`
Thought: 我需要先搜索相关信息。
Action: web_search(query="2024 Nobel Prize in Physics winner")
Observation: John J. Hopfield 和 Geoffrey E. Hinton 获奖。

Thought: 我已经找到答案。
Action: finish(answer="...")
\`\`\`

**为什么有效**：

- 把中间推理过程显式化，便于调试。
- 行动结果作为 observation 回到上下文，减少幻觉。
- 可以处理需要多步信息获取的任务。

## 2.3 Function Calling 的协议层

Function Calling 不是魔法，而是一个**结构化输出协议**：

1. 调用方提供一组工具定义（JSON Schema）。
2. 模型根据用户输入，决定是否输出 \`tool_calls\`。
3. 调用方解析 \`tool_calls\`，执行对应函数。
4. 函数结果以 \`tool\` / \`function\` 角色加入消息历史。
5. 模型根据函数结果生成最终回答。

## 2.4 Plan-Execute vs ReAct

| 模式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| ReAct | 灵活，能根据观察调整 | 可能陷入局部最优 | 信息不完全、需要探索 |
| Plan-Execute | 全局规划，执行稳定 | 计划错误时成本高 | 步骤明确、可分解 |

Nexus 的 Planner Agent 体现 Plan-Execute，Orchestrator 在计划执行过程中保留 ReAct 式的循环调整能力。`,
        codeLabs: [
          {
            id: 'react-loop',
            title: '最小 ReAct Agent',
            description: '实现一个能调用 calculate 工具的 ReAct 循环。',
            starterCode: `import json

class ReActAgent:
    def __init__(self, llm_client, tools):
        self.llm = llm_client
        self.tools = {tool["function"]["name"]: tool for tool in tools}
        self.messages = []

    def run(self, query, max_turns=5):
        self.messages.append({"role": "user", "content": query})
        for _ in range(max_turns):
            response = self.llm.chat(self.messages, tools=list(self.tools.values()))
            content = response["content"]
            tool_calls = response.get("tool_calls")

            if not tool_calls:
                return content

            self.messages.append({"role": "assistant", "content": content, "tool_calls": tool_calls})
            for tc in tool_calls:
                name = tc["function"]["name"]
                args = json.loads(tc["function"]["arguments"])
                result = self.execute_tool(name, args)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": str(result)
                })
        return "达到最大轮次"

    def execute_tool(self, name, args):
        if name == "calculate":
            return eval(args["expression"])  # 生产环境用 AST
        return "未知工具"`,
            expectedOutput: 'Agent 根据工具结果生成最终回答'
          }
        ],
        quizzes: [
          {
            id: 'q2-1',
            type: 'single',
            question: 'Agent 和普通 LLM 应用的本质区别是什么？',
            options: [
              { id: 'a', text: 'Agent 使用更大的模型' },
              { id: 'b', text: 'Agent 能调用外部工具并形成行动循环' },
              { id: 'c', text: 'Agent 不需要提示词工程' },
              { id: 'd', text: 'Agent 只能回答技术问题' }
            ],
            correctAnswer: 'b',
            explanation: 'Agent 的核心是能感知环境、做出决策、执行行动，并通过工具调用和观察结果形成循环。'
          },
          {
            id: 'q2-2',
            type: 'single',
            question: 'ReAct 中的 Observation 有什么作用？',
            options: [
              { id: 'a', text: '让模型展示推理过程' },
              { id: 'b', text: '把工具执行结果带回上下文，减少幻觉' },
              { id: 'c', text: '决定下一个 Thought 的主题' },
              { id: 'd', text: '结束 Agent 循环' }
            ],
            correctAnswer: 'b',
            explanation: 'Observation 是工具执行后的事实信息，模型基于它继续推理，而不是基于想象。'
          },
          {
            id: 'q2-3',
            type: 'code',
            question: 'Function Calling 返回的 tool_calls 中，函数参数通常以什么格式存在？',
            code: '{"tool_calls": [{"function": {"name": "get_weather", "arguments": "..."}}]}',
            correctAnswer: 'JSON 字符串',
            explanation: 'arguments 是一个 JSON 字符串，调用方需要用 json.loads 解析成字典后再执行工具。'
          }
        ],
        commonMistakes: [
          '不验证工具参数，直接执行模型生成的参数。',
          '忘记把工具结果加入上下文，导致模型看不到执行结果。',
          'max_turns 不设限，导致 Agent 可能无限循环。',
          '工具描述写得太模糊，模型无法判断何时调用。'
        ],
        furtherReading: [
          { title: 'ReAct: Synergizing Reasoning and Acting in Language Models' },
          { title: 'LangChain Agent 文档' },
          { title: 'OpenAI Function Calling 最佳实践' }
        ],
        checklist: [
          '能画出 ReAct 的 Thought-Action-Observation 循环',
          '能独立实现一个最小 Function Calling 流程',
          '能区分 Plan-Execute 和 ReAct 的适用场景',
          '知道 Agent 循环必须设置 max_turns'
        ]
      }
    ]
  },
  {
    id: 'rag-tools',
    title: '模块二：RAG 与工具',
    description: '掌握 RAG 系统设计和安全工具调用的核心技术',
    order: 2,
    lessons: [
      {
        id: 'rag-design',
        moduleId: 'rag-tools',
        moduleTitle: '模块二：RAG 与工具',
        order: 3,
        title: 'RAG 系统的设计与优化',
        description: '设计完整 RAG 流程，理解分块、Embedding、检索策略和评估方法。',
        objectives: [
          '设计完整 RAG 流程',
          '根据数据特点选择分块策略',
          '评估 RAG 检索质量和生成质量',
          '诊断 RAG 常见问题'
        ],
        prerequisites: [
          '理解 Embedding 和向量相似度',
          '能调用 LLM API'
        ],
        keyConcepts: [
          'Document Loader',
          'Text Splitter',
          'Embedding Model',
          'Vector Store',
          'Top-K / MMR'
        ],
        content: `## 3.1 RAG 的完整数据流

\`\`\`
离线阶段：
原始文档 → Loader 提取文本 → Splitter 分块 → Embedding 模型编码 → 存入 Vector Store

在线阶段：
用户 query → Embedding 模型编码 → Vector Store 相似度检索 → Top-K 片段 + query → LLM 生成回答
\`\`\`

## 3.2 文本分块策略

| 策略 | 说明 | 优点 | 缺点 |
|------|------|------|------|
| 固定长度 | 每 N 个字符切一块 | 简单 | 可能切断句子 |
| 按段落切 | 以换行为边界 | 语义完整 | 长度不均 |
| 重叠切分 | 相邻块有重叠 | 避免上下文丢失 | 存储量增加 |
| 语义切分 | 按语义边界切分 | 效果最好 | 实现复杂 |

Nexus 使用 \`RecursiveCharacterTextSplitter\`，优先按段落、句子切分。

## 3.3 检索策略

**相似度检索**：返回与 query 最相似的 K 个片段。

**MMR（最大边际相关性）**：在相似性和多样性之间做权衡，适合需要多角度信息的 query。

**相似度阈值过滤**：只返回相似度高于阈值的片段，避免硬凑无关结果。

## 3.4 RAG 评估

**检索评估**：Hit Rate、MRR、NDCG。

**生成评估**：LLM-as-a-Judge、BERTScore。`,
        codeLabs: [
          {
            id: 'rag-pipeline',
            title: '最小 RAG 流水线',
            description: '用 LangChain + Chroma 构建文档加载、分块、检索流程。',
            starterCode: `from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import DashScopeEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

loader = TextLoader("docs/python_guide.txt", encoding="utf-8")
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)

embeddings = DashScopeEmbeddings(
    model="text-embedding-v3",
    dashscope_api_key="your-key"
)
vectorstore = Chroma.from_documents(
    chunks,
    embeddings,
    persist_directory="./chroma_db"
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
results = retriever.invoke("Python 列表和元组有什么区别？")
for doc in results:
    print(doc.page_content[:200])`,
            expectedOutput: '打印 Top-3 相关文档片段'
          }
        ],
        quizzes: [
          {
            id: 'q3-1',
            type: 'single',
            question: 'RAG 主要解决 LLM 的哪两个问题？',
            options: [
              { id: 'a', text: '速度慢和成本高' },
              { id: 'b', text: '知识有限和幻觉' },
              { id: 'c', text: '不支持中文和代码' },
              { id: 'd', text: '无法多轮对话' }
            ],
            correctAnswer: 'b',
            explanation: 'RAG 通过检索外部真实信息，弥补 LLM 知识有限和容易幻觉的问题。'
          },
          {
            id: 'q3-2',
            type: 'single',
            question: 'MMR 检索策略的主要优势是什么？',
            options: [
              { id: 'a', text: '速度最快' },
              { id: 'b', text: '在相似性和多样性之间平衡' },
              { id: 'c', text: '不需要 Embedding' },
              { id: 'd', text: '只返回最相似的结果' }
            ],
            correctAnswer: 'b',
            explanation: 'MMR 通过多样性惩罚，避免返回内容高度重复的片段，覆盖更多角度。'
          }
        ],
        commonMistakes: [
          'chunk_size 过大导致检索不精确。',
          '不做来源标注，用户无法验证回答。',
          '检索结果为空时不处理，模型开始编造答案。',
          'Embedding 模型与语言不匹配，中文用英文模型。'
        ],
        furtherReading: [
          { title: 'Retrieval-Augmented Generation for Large Language Models: A Survey' },
          { title: 'LangChain RAG 文档' },
          { title: 'Hugging Face MTEB 排行榜' }
        ],
        checklist: [
          '能画出完整 RAG 数据流',
          '能根据场景选择分块策略和参数',
          '能解释 MMR 和相似度检索的区别',
          '能设计至少两个 RAG 评估指标'
        ]
      },
      {
        id: 'tool-safety',
        moduleId: 'rag-tools',
        moduleTitle: '模块二：RAG 与工具',
        order: 4,
        title: 'Function Calling 协议与安全实现',
        description: '设计 JSON Schema 工具定义，实现 AST 安全沙箱和 Tool Registry。',
        objectives: [
          '设计符合 JSON Schema 的工具定义',
          '实现安全 Python 代码执行沙箱',
          '处理工具调用失败和参数错误',
          '设计统一工具返回协议'
        ],
        prerequisites: [
          '理解 ReAct 和 Function Calling 流程',
          '了解 JSON Schema 基础'
        ],
        keyConcepts: [
          'JSON Schema',
          'AST',
          'Sandboxed Execution',
          'Tool Registry',
          '参数校验'
        ],
        content: `## 4.1 工具的三要素

一个可被 Agent 调用的工具需要：

1. **name**：唯一标识。
2. **description**：功能描述，帮助模型判断何时调用。
3. **parameters**：参数 schema，告诉模型参数类型和含义。

## 4.2 安全执行 Python 的原理

\`eval\` 和 \`exec\` 的问题在于执行任意代码。安全做法：

1. 用 \`ast.parse(code, mode='eval')\` 解析表达式。
2. 遍历 AST 节点。
3. 只允许白名单内的节点类型。
4. 解释执行白名单节点。

## 4.3 Tool Registry 的设计

Tool Registry 支持：

- 注册工具。
- 根据名字查找工具。
- 校验参数。
- 执行并捕获异常。
- 返回统一格式。`,
        codeLabs: [
          {
            id: 'ast-sandbox',
            title: 'AST 安全表达式求值',
            description: '实现一个只允许常数和四则运算的安全表达式求值器。',
            starterCode: `import ast
import operator

class SafeEvaluator:
    ALLOWED_NODES = (
        ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
        ast.USub, ast.UAdd,
    )

    def eval(self, expression):
        tree = ast.parse(expression, mode='eval')
        for node in ast.walk(tree):
            if not isinstance(node, self.ALLOWED_NODES):
                raise ValueError(f"Disallowed node: {type(node).__name__}")
        return self._eval_node(tree.body)

    def _eval_node(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.BinOp):
            ops = {
                ast.Add: operator.add, ast.Sub: operator.sub,
                ast.Mult: operator.mul, ast.Div: operator.truediv,
                ast.Pow: operator.pow,
            }
            return ops[type(node.op)](
                self._eval_node(node.left),
                self._eval_node(node.right)
            )
        raise ValueError(f"Unsupported node: {type(node).__name__}")

print(SafeEvaluator().eval("(2 + 3) * 4"))  # 20`,
            expectedOutput: '20'
          }
        ],
        quizzes: [
          {
            id: 'q4-1',
            type: 'single',
            question: '为什么 execute_python 工具不能用 eval 执行用户输入？',
            options: [
              { id: 'a', text: 'eval 不支持浮点数' },
              { id: 'b', text: 'eval 会执行任意代码，存在严重安全风险' },
              { id: 'c', text: 'eval 速度太慢' },
              { id: 'd', text: 'eval 不能处理字符串' }
            ],
            correctAnswer: 'b',
            explanation: 'eval 会执行任意 Python 代码，用户输入可能包含删除文件、执行系统命令等危险操作。'
          },
          {
            id: 'q4-2',
            type: 'single',
            question: '安全沙箱为什么通常用白名单而不是黑名单？',
            options: [
              { id: 'a', text: '白名单实现更简单' },
              { id: 'b', text: '黑名单难以覆盖所有绕过方式，白名单更安全' },
              { id: 'c', text: '白名单运行速度更快' },
              { id: 'd', text: '黑名单不支持 AST' }
            ],
            correctAnswer: 'b',
            explanation: 'Python AST 节点类型很多，黑名单很难穷尽所有危险组合。白名单只允许明确的节点类型，默认拒绝其他所有。'
          }
        ],
        commonMistakes: [
          '用 eval 执行用户输入。',
          '不校验工具参数，直接执行。',
          '工具返回格式不统一。',
          '异常信息泄露敏感路径或内部实现。'
        ],
        furtherReading: [
          { title: 'Python ast 模块官方文档' },
          { title: 'JSON Schema 官方规范' },
          { title: 'Tool Learning with Foundation Models' }
        ],
        checklist: [
          '能写出符合 JSON Schema 的工具定义',
          '能实现基于 AST 的安全表达式求值',
          '能实现 ToolRegistry 的注册、查找、执行、校验',
          '知道如何处理工具执行异常'
        ]
      }
    ]
  },
  {
    id: 'nexus-arch',
    title: '模块三：Nexus 架构实现',
    description: '深入理解 Nexus Multi-Agent 内核和消息总线机制',
    order: 3,
    lessons: [
      {
        id: 'message-bus',
        moduleId: 'nexus-arch',
        moduleTitle: '模块三：Nexus 架构实现',
        order: 5,
        title: 'Message Bus 与异步协作',
        description: '实现基于 asyncio.Queue 的消息总线，理解三种通信模式和异步问题处理。',
        objectives: [
          '实现消息总线',
          '理解点对点、广播、请求-响应模式',
          '处理超时和死锁问题',
          '解释消息总线优于函数调用的场景'
        ],
        prerequisites: [
          '理解 Python asyncio',
          '理解队列数据结构'
        ],
        keyConcepts: [
          'asyncio.Queue',
          'Pub/Sub',
          'Future / Task',
          'Timeout',
          'Deadlock'
        ],
        content: `## 5.1 消息总线的通信模式

**点对点**：Orchestrator → Planner

**广播**：Orchestrator → 所有订阅 Agent

**请求-响应**：Orchestrator send_and_wait Retriever，Retriever 返回 result

## 5.2 asyncio.Queue 的选择

\`asyncio.Queue\` 是协程安全的队列：

- \`await queue.get()\`：阻塞直到有消息。
- \`await queue.put(msg)\`：放入消息。

## 5.3 send_and_wait 的 Future 实现

核心思路：

1. Orchestrator 为每个 task_id 创建 Future。
2. 发送消息后等待 Future。
3. 收到结果时设置对应 Future 的结果。

## 5.4 为什么不用直接函数调用

| 维度 | 函数调用 | 消息总线 |
|------|----------|----------|
| 耦合 | 高 | 低 |
| 扩展性 | 新增 Agent 需改调用方 | 新增 Agent 只需订阅 |
| 异步 | 需显式 await | 天然异步 |
| 分布式 | 不支持 | 未来可换 Redis |`,
        codeLabs: [
          {
            id: 'message-bus-impl',
            title: '实现 MessageBus',
            description: '实现支持 publish、subscribe、send_and_wait 的消息总线。',
            starterCode: `import asyncio
from dataclasses import dataclass, field
from typing import Dict, Any
from uuid import uuid4

@dataclass
class Message:
    task_id: str
    sender: str
    recipient: str
    message_type: str
    payload: Dict[str, Any]
    message_id: str = field(default_factory=lambda: str(uuid4()))

class MessageBus:
    def __init__(self):
        self._queues: Dict[str, asyncio.Queue] = {}

    def subscribe(self, agent_id: str) -> asyncio.Queue:
        if agent_id not in self._queues:
            self._queues[agent_id] = asyncio.Queue()
        return self._queues[agent_id]

    async def publish(self, message: Message) -> None:
        if message.recipient == "broadcast":
            for queue in self._queues.values():
                await queue.put(message)
        else:
            queue = self._queues.get(message.recipient)
            if queue is None:
                raise ValueError(f"No subscriber for {message.recipient}")
            await queue.put(message)

    async def send_and_wait(self, recipient, message, timeout=30.0):
        await self.publish(message)
        queue = self.subscribe("orchestrator")
        deadline = asyncio.get_event_loop().time() + timeout
        while True:
            remaining = deadline - asyncio.get_event_loop().time()
            if remaining <= 0:
                raise asyncio.TimeoutError()
            msg = await asyncio.wait_for(queue.get(), timeout=remaining)
            if msg.sender == recipient and msg.task_id == message.task_id:
                return msg
            await queue.put(msg)`,
            expectedOutput: '消息总线支持点对点、广播和超时等待'
          }
        ],
        quizzes: [
          {
            id: 'q5-1',
            type: 'single',
            question: '消息总线相比直接函数调用的核心优势是什么？',
            options: [
              { id: 'a', text: '运行速度更快' },
              { id: 'b', text: '解耦 Agent 之间的依赖，便于扩展' },
              { id: 'c', text: '代码更短' },
              { id: 'd', text: '不需要异步' }
            ],
            correctAnswer: 'b',
            explanation: '消息总线让 Agent 只关心消息协议，不需要知道其他 Agent 的具体实现，新增 Agent 只需订阅消息。'
          },
          {
            id: 'q5-2',
            type: 'single',
            question: 'send_and_wait 中为什么要用 asyncio.Future 而不是从队列轮询？',
            options: [
              { id: 'a', text: 'Future 更节省内存' },
              { id: 'b', text: 'Future 是事件驱动的，收到结果立即唤醒，效率更高' },
              { id: 'c', text: 'Future 不需要 task_id' },
              { id: 'd', text: '队列不能超时' }
            ],
            correctAnswer: 'b',
            explanation: 'Future 让协程在结果到达时才被唤醒，而轮询需要不断尝试取消息并判断 task_id，效率低且代码复杂。'
          }
        ],
        commonMistakes: [
          'Future 没有清理导致内存泄漏。',
          'recipient 没启动导致 send_and_wait 一直超时。',
          '广播时把自己发的消息又收回来造成循环。',
          '在同步代码里调用 async publish。'
        ],
        furtherReading: [
          { title: 'Python asyncio 官方文档' },
          { title: 'RabbitMQ Pub/Sub 文档' },
          { title: 'Redis Pub/Sub 文档' }
        ],
        checklist: [
          '能独立实现 MessageBus',
          '能解释 Future 在 send_and_wait 中的作用',
          '能写出消息总线的单元测试',
          '能列举消息总线相比函数调用的优势和劣势'
        ]
      },
      {
        id: 'base-agent',
        moduleId: 'nexus-arch',
        moduleTitle: '模块三：Nexus 架构实现',
        order: 6,
        title: 'BaseAgent 与 Orchestrator',
        description: '设计可扩展的 Agent 基类，理解 Orchestrator 状态机和任务调度。',
        objectives: [
          '设计 Agent 基类',
          '实现 Orchestrator、Planner 等专业 Agent',
          '理解 Agent 职责边界',
          '设计 Agent 间消息协议'
        ],
        prerequisites: [
          '已实现 MessageBus',
          '理解抽象基类和 async/await'
        ],
        keyConcepts: [
          'BaseAgent',
          'Agent Loop',
          '消息协议',
          '职责分离',
          'SessionState'
        ],
        content: `## 6.1 BaseAgent 的设计

BaseAgent 是所有 Agent 的公共骨架，提供：

- 唯一的 agent_id
- 消息队列订阅
- 消息处理循环
- 发送消息和调用 LLM 的便利方法

## 6.2 Orchestrator 的状态机

\`\`\`
pending → planning → executing → summarizing → critiquing → done
\`\`\`

每个状态对应一次对外部 Agent 的调用。

## 6.3 为什么 Retriever 和 Executor 先 mock

Phase 1 的关键是验证**协作架构**，不是真实 RAG 和工具。mock 的好处：

- 降低复杂度，快速验证核心机制。
- 保证接口一致，Phase 2 替换实现时其他模块不用大改。
- 测试稳定，不依赖外部 API 和数据库。`,
        codeLabs: [
          {
            id: 'echo-agent',
            title: '实现 EchoAgent',
            description: '继承 BaseAgent，实现收到消息后返回内容的 EchoAgent。',
            starterCode: `class EchoAgent(BaseAgent):
    async def handle_message(self, message):
        await self.send_message(
            recipient=message.sender,
            message_type="result",
            payload={"echo": message.payload},
            task_id=message.task_id,
        )`,
            expectedOutput: 'Orchestrator 发送消息后收到 echo 结果'
          }
        ],
        quizzes: [
          {
            id: 'q6-1',
            type: 'single',
            question: 'BaseAgent 的 run 方法为什么用 asyncio.wait_for(queue.get(), timeout=0.5)？',
            options: [
              { id: 'a', text: '提高消息处理速度' },
              { id: 'b', text: '定期检查 _running 标志，响应 stop() 调用' },
              { id: 'c', text: '限制每条消息处理时间' },
              { id: 'd', text: '避免队列为空时崩溃' }
            ],
            correctAnswer: 'b',
            explanation: '如果直接 await queue.get()，队列会永久阻塞，无法响应 stop()。用 wait_for 超时后可以检查 _running 并优雅退出。'
          },
          {
            id: 'q6-2',
            type: 'single',
            question: 'Phase 1 中 Retriever 和 Executor 使用 mock 的主要原因是什么？',
            options: [
              { id: 'a', text: 'mock 比真实实现性能更好' },
              { id: 'b', text: '隔离 RAG 和工具复杂度，先验证协作架构' },
              { id: 'c', text: '真实实现代码太多，写不完' },
              { id: 'd', text: 'mock 更容易通过测试' }
            ],
            correctAnswer: 'b',
            explanation: 'Phase 1 聚焦 Multi-Agent 协作架构。mock 可以隔离 RAG 和 Tool Registry 的复杂度，确保核心机制稳定后再替换。'
          }
        ],
        commonMistakes: [
          'Agent 不调用 stop() 导致程序无法退出。',
          'handle_message 里没有 await。',
          'task_id 冲突。',
          '抽象方法未实现。'
        ],
        furtherReading: [
          { title: 'Python ABC 模块官方文档' },
          { title: 'LangChain Agent 源码' },
          { title: 'AutoGen ConversableAgent 设计' }
        ],
        checklist: [
          '能实现 BaseAgent 和至少一个子类',
          '能解释 Orchestrator 的状态机',
          '能设计 Agent 间消息协议',
          '能写出 Agent 的单元测试'
        ]
      }
    ]
  },
  {
    id: 'engineering',
    title: '模块四：工程化与求职',
    description: '掌握测试评估、工程化实践和简历面试技巧',
    order: 4,
    lessons: [
      {
        id: 'testing-eval',
        moduleId: 'engineering',
        moduleTitle: '模块四：工程化与求职',
        order: 7,
        title: '测试策略与 LLM 评估',
        description: '为 Agent 系统编写测试，设计 LLM-as-a-Judge 评估流程。',
        objectives: [
          '编写单元测试、集成测试和评估测试',
          '用 mock 隔离 LLM 调用',
          '设计 LLM-as-a-Judge 评估',
          '解释传统评估指标的局限性'
        ],
        prerequisites: [
          '已会用 pytest',
          '已理解 mock 和 monkeypatch'
        ],
        keyConcepts: [
          'pytest-asyncio',
          'Monkeypatch',
          'LLM-as-a-Judge',
          'BERTScore',
          'Regression Test'
        ],
        content: `## 7.1 Agent 系统测试的分层

| 层级 | 范围 | 示例 |
|------|------|------|
| 单元测试 | 单个函数/类 | MessageBus、SafeEvaluator |
| 集成测试 | 多个模块协作 | Orchestrator 完整流程 |
| 端到端测试 | 完整用户流程 | CLI 输入 → 最终输出 |
| 评估测试 | 回答质量 | test_cases.json 跑分 |

## 7.2 mock LLM 的原则

- 只 mock 不稳定或昂贵的依赖。
- 不 mock 被测模块自身的核心逻辑。
- mock 返回值要覆盖正常、异常、边界情况。

## 7.3 LLM-as-a-Judge

用更强的模型给回答打分，从 correctness、relevance、completeness、safety 等维度评估。

## 7.4 传统评估指标的局限性

| 指标 | 局限性 |
|------|--------|
| BLEU | 不适合开放式问答 |
| ROUGE | 只匹配 n-gram |
| BERTScore | 计算成本较高 |

Agent 系统更多用 LLM-as-a-Judge 和规则评估结合。`,
        codeLabs: [
          {
            id: 'llm-judge',
            title: '实现 LLM-as-a-Judge',
            description: '实现一个评估函数，对 Agent 回答从四个维度打分。',
            starterCode: `import json

def evaluate_answer(query, answer, llm_client):
    prompt = f"""请评估以下回答，从 correctness、relevance、completeness、safety 四个维度打分（0-1），并给出 overall 分数。

问题：{query}
回答：{answer}

请只输出 JSON：{{"correctness": ..., "relevance": ..., "completeness": ..., "safety": ..., "overall": ..., "feedback": "..."}}"""
    response = llm_client.chat([{"role": "user", "content": prompt}])
    return json.loads(response["content"])`,
            expectedOutput: '返回包含四个维度分数的 JSON 对象'
          }
        ],
        quizzes: [
          {
            id: 'q7-1',
            type: 'single',
            question: '为什么 Agent 系统不能完全依赖单元测试？',
            options: [
              { id: 'a', text: '单元测试太慢' },
              { id: 'b', text: 'LLM 输出随机，且 Agent 行为是多模块协作结果' },
              { id: 'c', text: '单元测试不能测异步代码' },
              { id: 'd', text: 'Agent 系统不需要测试' }
            ],
            correctAnswer: 'b',
            explanation: '单元测试只能保证非 LLM 部分正确，Agent 的整体行为和回答质量需要集成测试和评估测试。'
          },
          {
            id: 'q7-2',
            type: 'single',
            question: 'BERTScore 比 ROUGE 好在哪里？',
            options: [
              { id: 'a', text: '计算更快' },
              { id: 'b', text: '基于语义嵌入，能识别同义词和语义等价表达' },
              { id: 'c', text: '不需要参考答案' },
              { id: 'd', text: '只适用于英文' }
            ],
            correctAnswer: 'b',
            explanation: 'ROUGE 基于 n-gram 字面匹配，BERTScore 基于语义嵌入，能捕捉语义相似性。'
          }
        ],
        commonMistakes: [
          '测试覆盖不到异步分支。',
          'LLM mock 返回格式不对。',
          '评估 prompt 太开放导致输出不合法 JSON。',
          '只测 happy path，不测异常情况。'
        ],
        furtherReading: [
          { title: 'pytest-asyncio 官方文档' },
          { title: 'LLM-as-a-Judge: A Comprehensive Survey' },
          { title: 'BERTScore 官方仓库' }
        ],
        checklist: [
          '能为异步代码写 pytest 测试',
          '会 mock LLM 调用',
          '能实现 LLM-as-a-Judge',
          '知道 BLEU/ROUGE/BERTScore 的适用场景'
        ]
      },
      {
        id: 'interview',
        moduleId: 'engineering',
        moduleTitle: '模块四：工程化与求职',
        order: 8,
        title: '简历包装与面试表达',
        description: '用 STAR 法则描述项目，准备口述版介绍和高频面试题。',
        objectives: [
          '用 STAR 法则描述项目',
          '准备 3 分钟项目口述',
          '回答 Agent / RAG / Function Calling 高频题',
          '根据岗位调整简历关键词'
        ],
        prerequisites: [
          '已完成 Nexus Phase 1 或更高阶段实现'
        ],
        keyConcepts: [
          'STAR 法则',
          '技术关键词',
          '项目口述',
          '岗位匹配'
        ],
        content: `## 8.1 STAR 法则

STAR = Situation（背景）+ Task（任务）+ Action（行动）+ Result（结果）。

## 8.2 项目口述结构

1. 一句话定义项目（15 秒）。
2. 为什么做（30 秒）。
3. 技术架构和核心设计（90 秒）。
4. 挑战和解决（45 秒）。
5. 成果和收获（30 秒）。

## 8.3 AI Agent 岗位关键词

Agent、Multi-Agent、ReAct、Function Calling、RAG、Embedding、Chroma、LangChain、Tool Registry、LLM-as-a-Judge、Prompt Engineering、FastAPI、SSE、pytest、asyncio。

## 8.4 高频面试题示例

- 什么是 Agent？和普通 LLM 应用有什么区别？
- ReAct、CoT、ToT 有什么区别？
- RAG 解决了什么问题？文本怎么分块？
- Function Calling 的原理是什么？
- 你怎么评估 Agent 的回答质量？`,
        codeLabs: [
          {
            id: 'star-writing',
            title: '用 STAR 写项目描述',
            description: '用 STAR 法则写一段 Nexus 项目描述。',
            starterCode: `// 背景
"在学习 AI Agent 过程中，发现很多 demo 只停留在调用 API，缺乏真实应用场景和评估闭环。"

// 任务
"设计并实现一个面向 MOD 开发知识库的智能文档任务 Agent。"

// 行动
"整合 RAG 检索与 Function Calling，实现真实工具（代码执行、文件读取），
设计回答质量评估模块，编写 pytest 测试。"

// 结果
"Agent 能准确回答 Python/MOD 相关问题，支持多工具协同和自动评估，项目已开源到 GitHub。"`,
            expectedOutput: '一段 200-300 字的 STAR 项目描述'
          }
        ],
        quizzes: [
          {
            id: 'q8-1',
            type: 'single',
            question: 'STAR 法则中 A 代表什么？',
            options: [
              { id: 'a', text: 'Ability（能力）' },
              { id: 'b', text: 'Action（行动）' },
              { id: 'c', text: 'Achievement（成就）' },
              { id: 'd', text: 'Analysis（分析）' }
            ],
            correctAnswer: 'b',
            explanation: 'STAR = Situation（背景）+ Task（任务）+ Action（行动）+ Result（结果）。'
          },
          {
            id: 'q8-2',
            type: 'single',
            question: '面试中解释"为什么用 Multi-Agent"时，最不应该强调什么？',
            options: [
              { id: 'a', text: '职责分离，便于维护' },
              { id: 'b', text: '通过消息总线解耦' },
              { id: 'c', text: 'Multi-Agent 一定比单 Agent 性能好' },
              { id: 'd', text: '可以引入评估 Agent 做质量闭环' }
            ],
            correctAnswer: 'c',
            explanation: 'Multi-Agent 不一定性能更好，它带来的是架构清晰和可扩展性。不能为了用而用。'
          }
        ],
        commonMistakes: [
          '只说技术名词不讲解决什么问题。',
          '夸大项目难度，容易被追问穿帮。',
          '没有准备失败应对，要诚实说明 mock 和真实实现的边界。',
          '自我介绍和简历主线不一致。'
        ],
        furtherReading: [
          { title: 'Cracking the Coding Interview' },
          { title: '目标公司面经' },
          { title: 'STAR 面试法' }
        ],
        checklist: [
          '能用 STAR 写项目描述',
          '能 3 分钟口述项目',
          '能回答 10 个以上高频面试题',
          '能根据岗位调整简历关键词'
        ]
      }
    ]
  }
]

export const getLessonById = (id: string): Lesson | undefined => {
  for (const module of modules) {
    const lesson = module.lessons.find(l => l.id === id)
    if (lesson) return lesson
  }
  return undefined
}

export const getAllLessons = (): Lesson[] => {
  return modules.flatMap(m => m.lessons)
}

export const getNextLessonId = (currentId: string): string | null => {
  const lessons = getAllLessons()
  const index = lessons.findIndex(l => l.id === currentId)
  if (index === -1 || index === lessons.length - 1) return null
  return lessons[index + 1].id
}

export const getPrevLessonId = (currentId: string): string | null => {
  const lessons = getAllLessons()
  const index = lessons.findIndex(l => l.id === currentId)
  if (index <= 0) return null
  return lessons[index - 1].id
}
