import { useState } from 'react'
import { PAGE_CHANGELOGS, type ChangelogEntry } from '../data/changelogs'

export default function PageChangelog({ pageKey }: { pageKey: string }) {
  const [expanded, setExpanded] = useState(false)
  const entries = PAGE_CHANGELOGS[pageKey]
  if (!entries || entries.length === 0) return null

  const latest = entries[0]

  return (
    <div className="bg-accent-secondary-bg border-b border-border-subtle">
      <div className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-2.5">
        <div className="flex items-start sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3 text-sm">
            <span className="shrink-0 px-2 py-0.5 rounded-full bg-accent text-accent-text text-xs font-semibold">
              v{latest.version}
            </span>
            <span className="text-accent-secondary-text">
              {latest.items.join(' · ')}
            </span>
          </div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-tertiary hover:text-primary whitespace-nowrap"
          >
            {expanded ? '收起历史' : '查看历史'}
          </button>
        </div>

        {expanded && (
          <div className="mt-3 pl-12 space-y-2 border-t border-border-subtle pt-3">
            {entries.map((e: ChangelogEntry) => (
              <div key={e.version} className="text-sm">
                <span className="font-semibold text-primary">v{e.version}</span>
                <span className="text-muted text-xs ml-2">{e.date}</span>
                <ul className="mt-1 ml-4 list-disc text-secondary">
                  {e.items.map((item, idx) => (
                    <li key={idx}>{item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
