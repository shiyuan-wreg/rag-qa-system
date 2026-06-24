export interface LearnNavModule {
  id: string
  title: string
  lessons: { id: string; title: string }[]
}

export const LEARN_NAV: LearnNavModule[] = [
  {
    id: 'fundamentals',
    title: '模块一：LLM 与 Agent 基础',
    lessons: [
      { id: 'llm-basics', title: 'LLM 的能力边界与工程约束' },
      { id: 'agent-intro', title: 'Agent 架构与 ReAct 范式' },
    ],
  },
  {
    id: 'rag-tools',
    title: '模块二：RAG 与工具',
    lessons: [
      { id: 'rag-overview', title: 'RAG 流程与向量数据库' },
      { id: 'tools', title: 'Function Calling 与工具设计' },
    ],
  },
  {
    id: 'nexus-arch',
    title: '模块三：Nexus 架构实现',
    lessons: [
      { id: 'multi-agent', title: 'Multi-Agent 协作模式' },
      { id: 'sse-ui', title: 'SSE 实时流与前端展示' },
    ],
  },
  {
    id: 'engineering',
    title: '模块四：工程化与求职',
    lessons: [
      { id: 'deployment', title: 'Docker 与云部署' },
      { id: 'career', title: '项目包装与面试准备' },
    ],
  },
]
