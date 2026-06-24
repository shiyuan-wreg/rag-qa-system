export interface ChangelogEntry {
  version: string
  date: string
  items: string[]
}

export interface FlatChangelogEntry extends ChangelogEntry {
  page: string
}

// 各子站在便签上的简短标签
export const PAGE_LABELS: Record<string, string> = {
  home: '门户',
  rag: 'RAG',
  fc: 'Function Calling',
  nexus: 'Nexus',
  doctomd: 'DocHub',
  learn: '学习站',
  me: '个人页',
}

export const PAGE_CHANGELOGS: Record<string, ChangelogEntry[]> = {
  home: [
    {
      version: '0.3',
      date: '2026-06-24',
      items: ['首页新增更新公告板', '新增更新公告详情页', '学习页加宽、进度移入侧边栏', 'Demo/Learn 沉浸式页面移除顶部公告条'],
    },
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
    { version: '0.3', date: '2026-06-24', items: ['正文区域加宽', '学习进度由顶部移入侧边栏'] },
    { version: '0.2', date: '2026-06-24', items: ['学习站接入门户统一侧边栏'] },
    { version: '0.1', date: '2026-06-22', items: ['Nexus 交互式学习站上线'] },
  ],
  doctomd: [{ version: '0.1', date: '2026-06-23', items: ['DocHub Markdown 文档站上线'] }],
  me: [{ version: '0.2', date: '2026-06-24', items: ['个人页上线'] }],
}

// 拍平为所有条目,补充 page 字段,按日期降序。
export function getAllChangelogs(): FlatChangelogEntry[] {
  return Object.entries(PAGE_CHANGELOGS)
    .flatMap(([page, entries]) => entries.map((e) => ({ ...e, page })))
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime() || b.version.localeCompare(a.version))
}

