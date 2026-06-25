import type { IconName } from '../components/Icon'

export type Work = {
  slug: string
  index: string            // 编号,如 '01'
  title: string
  desc: string
  tech: string[]
  github?: string
  path: string
  icon: IconName
  changelog: { version: string; date: string; items: string[] }[]
}

export const WORKS: Work[] = [
  {
    slug: 'rag',
    index: '01',
    title: 'RAG 文档问答',
    desc: '基于检索增强生成的私有知识库问答。',
    tech: ['RAG', 'Chroma', '通义千问', 'FastAPI'],
    path: '/rag',
    icon: 'file-search',
    changelog: [
      { version: '0.1', date: '2026-06-22', items: ['RAG 文档问答 Demo 上线'] },
    ],
  },
  {
    slug: 'fc',
    index: '02',
    title: 'Function Calling Agent',
    desc: '大模型自动决策并调用工具完成任务。',
    tech: ['Function Calling', '通义千问', 'FastAPI'],
    path: '/fc',
    icon: 'terminal',
    changelog: [
      { version: '0.1', date: '2026-06-22', items: ['Function Calling Agent Demo 上线'] },
    ],
  },
  {
    slug: 'nexus',
    index: '03',
    title: 'Nexus Multi-Agent 工作流',
    desc: '多 Agent 协作的 AI 工作流助手，实时展示思考过程。',
    tech: ['Multi-Agent', 'FastAPI', 'SSE', '通义千问'],
    path: '/nexus',
    icon: 'workflow',
    changelog: [
      { version: '0.1', date: '2026-06-22', items: ['Nexus Multi-Agent 工作流 Demo 上线'] },
    ],
  },
  {
    slug: 'learn',
    index: '04',
    title: 'Nexus 交互式学习站',
    desc: 'LLM/Agent/RAG 的交互式课程与测验。',
    tech: ['React', 'Vite', 'TypeScript'],
    path: '/learn',
    icon: 'graduation-cap',
    changelog: [
      { version: '0.2', date: '2026-06-24', items: ['学习站接入门户统一侧边栏'] },
      { version: '0.1', date: '2026-06-22', items: ['Nexus 交互式学习站上线'] },
    ],
  },
  {
    slug: 'doctomd',
    index: '05',
    title: 'DocHub Markdown 文档站',
    desc: '把 Markdown 文集一键转成可浏览的 HTML 文档站。',
    tech: ['FastAPI', 'Markdown', 'Jinja2'],
    path: '/doctomd',
    icon: 'file-text',
    changelog: [
      { version: '0.1', date: '2026-06-23', items: ['DocHub Markdown 文档站上线'] },
    ],
  },
]
