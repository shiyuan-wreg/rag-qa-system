import { useTheme, type Theme } from '../hooks/useTheme'

const THEMES: { key: Theme; label: string }[] = [
  { key: 'mono-light', label: '极简' },
  { key: 'light', label: '浅色' },
  { key: 'deepblue', label: '深蓝' },
  { key: 'cyber', label: '赛博' },
  { key: 'machine', label: '监控' },
]

export default function ThemeToggle() {
  const { theme, setTheme } = useTheme()

  return (
    <div className="inline-flex items-center gap-1 rounded-lg border border-border p-1 bg-soft">
      {THEMES.map((t) => {
        const active = theme === t.key
        return (
          <button
            key={t.key}
            onClick={() => setTheme(t.key)}
            className={[
              'px-2.5 py-1 text-xs font-medium rounded-md transition-all',
              active
                ? 'bg-accent text-accent-text shadow-sm'
                : 'text-tertiary hover:text-primary hover:bg-surface-hover',
            ].join(' ')}
            aria-pressed={active}
          >
            {t.label}
          </button>
        )
      })}
    </div>
  )
}
