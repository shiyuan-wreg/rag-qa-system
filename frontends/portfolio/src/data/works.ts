export type Work = {
  slug: string
  index: string            // 编号,如 '01'
  title: string
  desc: string
  tech: string[]
  github?: string
  path: string
  icon: string             // /icons/{slug}.svg
}

export const WORKS: Work[] = [
  {
    slug: 'rag',
    index: '01',
    title: 'RAG 文档问答',
    desc: '基于检索增强生成的私有知识库问答。',
    tech: ['RAG', 'Chroma', '通义千问', 'FastAPI'],
    path: '/rag',
    icon: '/icons/rag.svg',
  },
  {
    slug: 'fc',
    index: '02',
    title: 'Function Calling Agent',
    desc: '大模型自动决策并调用工具完成任务。',
    tech: ['Function Calling', '通义千问', 'FastAPI'],
    path: '/fc',
    icon: '/icons/fc.svg',
  },
  {
    slug: 'nexus',
    index: '03',
    title: 'Nexus Multi-Agent 工作流',
    desc: '多 Agent 协作的 AI 工作流助手，实时展示思考过程。',
    tech: ['Multi-Agent', 'FastAPI', 'SSE', '通义千问'],
    path: '/nexus',
    icon: '/icons/nexus.svg',
  },
  {
    slug: 'learn',
    index: '04',
    title: 'Nexus 交互式学习站',
    desc: 'LLM/Agent/RAG 的交互式课程与测验。',
    tech: ['React', 'Vite', 'TypeScript'],
    path: '/learn',
    icon: '/icons/learn.svg',
  },
  {
    slug: 'doctomd',
    index: '05',
    title: 'DocHub Markdown 文档站',
    desc: '把 Markdown 文集一键转成可浏览的 HTML 文档站。',
    tech: ['FastAPI', 'Markdown', 'Jinja2'],
    path: '/doctomd',
    icon: '/icons/doctomd.svg',
  },
  {
    slug: 'iconforge',
    index: '06',
    title: 'IconForge 图标净化器',
    desc: '上传图标自选净化:位图转矢量 / 去除白边 / 彩色转黑色,导出干净单色 SVG。',
    tech: ['FastAPI', 'Pillow', 'potrace', 'SVG'],
    path: '/iconforge',
    icon: '/icons/iconforge.svg',
  },
]
