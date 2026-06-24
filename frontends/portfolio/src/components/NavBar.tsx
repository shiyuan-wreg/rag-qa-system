import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import ThemeToggle from './ThemeToggle'

const ITEMS = [
  { to: '/', label: '首页' },
  { to: '/rag', label: 'AI 作品' },
  { to: '/learn', label: '学习' },
  { to: '/me', label: '个人' },
]

export default function NavBar() {
  const { pathname } = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)

  const isActive = (to: string) => {
    if (to === '/') return pathname === '/'
    return pathname.startsWith(to)
  }

  return (
    <nav className="sticky top-0 z-50 bg-surface border-b border-border">
      <div className="max-w-content mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          <Link to="/" className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-md bg-accent text-accent-text flex items-center justify-center text-xs font-bold">
              AI
            </div>
            <span className="font-bold text-primary">个人集成学习网站</span>
          </Link>

          <div className="hidden md:flex items-center gap-6">
            {ITEMS.map((it) => (
              <Link
                key={it.to}
                to={it.to}
                className={`text-sm font-medium transition-colors ${
                  isActive(it.to) ? 'text-primary' : 'text-tertiary hover:text-primary'
                }`}
              >
                {it.label}
              </Link>
            ))}
            <ThemeToggle />
          </div>

          <div className="flex md:hidden items-center gap-3">
            <ThemeToggle />
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="p-2 rounded-md text-tertiary hover:bg-surface-hover"
              aria-label="切换菜单"
            >
              {mobileOpen ? '✕' : '☰'}
            </button>
          </div>
        </div>
      </div>

      {mobileOpen && (
        <div className="md:hidden border-t border-border bg-surface px-4 py-3 space-y-2">
          {ITEMS.map((it) => (
            <Link
              key={it.to}
              to={it.to}
              onClick={() => setMobileOpen(false)}
              className={`block text-sm font-medium ${
                isActive(it.to) ? 'text-primary' : 'text-tertiary'
              }`}
            >
              {it.label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  )
}
