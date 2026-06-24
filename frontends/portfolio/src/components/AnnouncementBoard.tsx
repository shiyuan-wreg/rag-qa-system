import { Link } from 'react-router-dom'
import { getAllChangelogs, PAGE_LABELS } from '../data/changelogs'

export default function AnnouncementBoard() {
  // 只展示全站最近一次更新，整块卡片点击进入详情页。
  const latest = getAllChangelogs()[0]
  if (!latest) return null

  return (
    <section className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 pt-10">
      <Link
        to="/changelog"
        className="block group rounded-xl border border-border bg-surface shadow-sm hover:shadow-md hover:border-accent/50 transition-all overflow-hidden"
      >
        <div className="flex items-center justify-between gap-3 px-5 py-3 border-b border-border-subtle bg-surface-soft">
          <div className="flex items-center gap-2 flex-wrap">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-accent shrink-0">
              <path d="m3 11 18-5v12L3 14v-3z" />
              <path d="M11.6 16.8a3 3 0 1 1-5.8-1.6" />
            </svg>
            <span className="font-semibold text-primary text-sm">更新公告</span>
            <span className="px-2 py-0.5 rounded-full bg-accent text-accent-text text-xs font-semibold">
              v{latest.version}
            </span>
            <span className="text-xs text-muted">{latest.date}</span>
            <span className="text-xs text-tertiary border border-border rounded px-1.5">
              {PAGE_LABELS[latest.page] ?? latest.page}
            </span>
          </div>
          <span className="text-xs text-tertiary group-hover:text-accent transition-colors whitespace-nowrap">
            查看全部 →
          </span>
        </div>

        <div className="px-5 py-4">
          <ul className="grid sm:grid-cols-2 gap-x-6 gap-y-2">
            {latest.items.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-secondary">
                <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-accent shrink-0" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </Link>
    </section>
  )
}
