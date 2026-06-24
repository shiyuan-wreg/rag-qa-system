import { Link } from 'react-router-dom'

export interface SidebarNavItem {
  key: string
  to: string
  label: string
  icon?: { letter: string; bg: string; text: string }
}

export default function SidebarNav({ items, activeKey }: { items: SidebarNavItem[]; activeKey: string }) {
  return (
    <nav className="space-y-1">
      {items.map((it) => {
        const active = activeKey === it.key
        return (
          <Link
            key={it.key}
            to={it.to}
            className={[
              'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all',
              active
                ? 'bg-accent-secondary-bg text-accent-secondary-text shadow-sm'
                : 'text-tertiary hover:bg-surface-hover hover:text-primary',
            ].join(' ')}
          >
            {it.icon && (
              <span
                className="w-6 h-6 rounded-md flex items-center justify-center text-[11px] font-bold shrink-0 shadow-sm"
                style={{ backgroundColor: it.icon.bg, color: it.icon.text }}
              >
                {it.icon.letter}
              </span>
            )}
            {it.label}
          </Link>
        )
      })}
    </nav>
  )
}
