import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import ThemeToggle from './ThemeToggle'
import ParallaxToggle from './ParallaxToggle'
import Logo from './Logo'
import { useScrolled } from '../hooks/useScrolled'

const ITEMS = [
  { to: '/', label: '首页' },
  { to: '/rag', label: 'AI 作品' },
  { to: '/learn', label: '学习' },
  { to: '/changelog', label: '更新' },
  { to: '/me', label: '个人' },
]

function MenuIcon({ open }: { open: boolean }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {open ? (
        <>
          <line x1="18" y1="6" x2="6" y2="18" />
          <line x1="6" y1="6" x2="18" y2="18" />
        </>
      ) : (
        <>
          <line x1="4" y1="6" x2="20" y2="6" />
          <line x1="4" y1="12" x2="20" y2="12" />
          <line x1="4" y1="18" x2="20" y2="18" />
        </>
      )}
    </svg>
  )
}

export default function NavBar() {
  const { pathname } = useLocation()
  const [mobileOpen, setMobileOpen] = useState(false)
  const scrolled = useScrolled()

  const isActive = (to: string) => {
    if (to === '/') return pathname === '/'
    return pathname.startsWith(to)
  }

  return (
    <nav className={`sticky top-0 z-50 bg-surface/90 backdrop-blur border-b transition-all duration-300 ${
      scrolled ? 'border-strong shadow-md' : 'border-border'
    }`}>
      <div className="max-w-wide mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          <Link to="/" className="flex items-center gap-2.5">
            <Logo className="w-8 h-8 text-primary" />
            <span className="font-bold text-primary">个人集成学习网站</span>
          </Link>

          <div className="hidden md:flex items-center gap-6">
            {ITEMS.map((it) => (
              <Link
                key={it.to}
                to={it.to}
                className={`group relative font-mono text-sm tracking-widest uppercase transition-colors ${
                  isActive(it.to) ? 'text-primary' : 'text-secondary hover:text-primary'
                }`}
              >
                {it.label}
                <span className={`absolute -bottom-[17px] left-0 h-0.5 bg-accent transition-all duration-300 ${
                  isActive(it.to) ? 'w-full' : 'w-0 group-hover:w-full'
                }`} />
              </Link>
            ))}
            <ParallaxToggle />
            <ThemeToggle />
          </div>

          <div className="flex md:hidden items-center gap-3">
            <ParallaxToggle />
            <ThemeToggle />
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="p-2 rounded-md text-tertiary hover:bg-surface-hover"
              aria-label="切换菜单"
            >
              <MenuIcon open={mobileOpen} />
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
              className={`block text-base font-medium ${
                isActive(it.to)
                  ? 'text-primary'
                  : 'text-secondary'
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
