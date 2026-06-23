export type Work = {
  slug: string
  title: string
  desc: string
  tech: string[]
  github?: string
  path: string        // 站内路由
}

export const WORKS: Work[] = [
  { slug: 'rag', title: 'RAG 文档问答', desc: '基于检索增强生成的私有知识库问答。',
    tech: ['RAG', 'Chroma', '通义千问', 'FastAPI'], path: '/rag' },
  { slug: 'fc', title: 'Function Calling Agent', desc: '大模型自动决策并调用工具完成任务。',
    tech: ['Function Calling', '通义千问', 'FastAPI'], path: '/fc' },
  { slug: 'nexus', title: 'Nexus Multi-Agent 工作流', desc: '多 Agent 协作的 AI 工作流助手，实时展示思考过程。',
    tech: ['Multi-Agent', 'FastAPI', 'SSE', '通义千问'], path: '/nexus' },
  { slug: 'learn', title: 'Nexus 交互式学习站', desc: 'LLM/Agent/RAG 的交互式课程与测验。',
    tech: ['React', 'Vite', 'TypeScript'], path: '/learn' },
  { slug: 'doctomd', title: 'DocHub Markdown 文档站', desc: '把 Markdown 文集一键转成可浏览的 HTML 文档站。',
    tech: ['FastAPI', 'Markdown', 'Jinja2'], path: '/doctomd' },
]
