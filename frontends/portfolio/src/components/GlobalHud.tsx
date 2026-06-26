import { useTheme } from '../hooks/useTheme'
import { getLatestChangelog } from '../data/changelogs'

export default function GlobalHud() {
  const { theme } = useTheme()
  if (theme !== 'machine') return null
  const version = getLatestChangelog()?.version ?? '0.0.0'
  return (
    <div
      aria-hidden="true"
      className="fixed bottom-3 right-4 z-40 pointer-events-none font-mono text-[10px] tracking-widest uppercase"
      style={{ color: 'var(--accent-primary)', opacity: 0.4, textShadow: '0 0 6px rgba(255,215,0,0.25)' }}
    >
      v{version} · MONITORING
    </div>
  )
}
