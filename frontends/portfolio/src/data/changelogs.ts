export interface ChangelogEntry {
  version: string // 全站统一版本，三段号 x.y.z
  date: string
  items: string[]
}

// 全站统一更新公告，按版本从新到旧排列。
// 版本约定：大模块更新进 minor（0.3.0 → 0.4.0），其下的细分小更新 / 修复进 patch（0.4.0 → 0.4.1）。
export const CHANGELOGS: ChangelogEntry[] = [
  {
    version: '0.4.1',
    date: '2026-06-26',
    items: [
      'LLM 出口整体切换到 DeepSeek（聊天）+ Jina（RAG 向量），海外服务器直连可用',
      '修复 Nexus 检索 Agent 的 httpx 异步 bug，多 Agent 流程恢复真实知识库检索',
    ],
  },
  {
    version: '0.4.0',
    date: '2026-06-25',
    items: [
      '门户整体改版为黑白科技风：故障风标题、打字机副标题、网格与噪点质感',
      '新增 IconForge 图标净化器（第 6 个作品）：位图转矢量 / 去除白边 / 彩色转黑',
    ],
  },
  {
    version: '0.3.0',
    date: '2026-06-24',
    items: [
      '新增 Hero 区与统一侧边栏，iframe 加载骨架屏',
      '新增主题切换器',
      '首页新增更新公告板与独立公告详情页',
      '学习站正文加宽，学习进度移入侧边栏',
      '个人页上线',
    ],
  },
  {
    version: '0.2.0',
    date: '2026-06-23',
    items: ['新增 DocHub Markdown 文档站（第 5 个作品）'],
  },
  {
    version: '0.1.0',
    date: '2026-06-22',
    items: [
      '作品网格首页上线',
      'RAG 文档问答、Function Calling Agent、Nexus Multi-Agent 三个 Demo 上线',
      'Nexus 交互式学习站上线',
    ],
  },
]

// 最新一条（公告板用）。CHANGELOGS 已按版本从新到旧维护，取首条即可。
export function getLatestChangelog(): ChangelogEntry | undefined {
  return CHANGELOGS[0]
}
