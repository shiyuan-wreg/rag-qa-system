export interface ChangelogEntry {
  version: string
  date: string
  items: string[]
}

export const PAGE_CHANGELOGS: Record<string, ChangelogEntry[]> = {
  home: [
    {
      version: '0.2',
      date: '2026-06-24',
      items: ['新增 Hero 区与统一侧边栏', '增加页面级更新公告', '新增主题切换器', 'iframe 加载骨架屏'],
    },
    { version: '0.1', date: '2026-06-22', items: ['作品网格首页上线'] },
  ],
  rag: [{ version: '0.1', date: '2026-06-22', items: ['RAG 文档问答 Demo 上线'] }],
  fc: [{ version: '0.1', date: '2026-06-22', items: ['Function Calling Agent Demo 上线'] }],
  nexus: [{ version: '0.1', date: '2026-06-22', items: ['Nexus Multi-Agent 工作流 Demo 上线'] }],
  learn: [
    { version: '0.2', date: '2026-06-24', items: ['学习站接入门户统一侧边栏'] },
    { version: '0.1', date: '2026-06-22', items: ['Nexus 交互式学习站上线'] },
  ],
  doctomd: [{ version: '0.1', date: '2026-06-23', items: ['DocHub Markdown 文档站上线'] }],
  me: [{ version: '0.2', date: '2026-06-24', items: ['个人页上线'] }],
}
