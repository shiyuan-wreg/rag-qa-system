import { Link, useLocation } from 'react-router-dom'

const ITEMS = [
  { to: '/', label: '首页' },
  { to: '/rag', label: 'AI作品' },
  { to: '/learn', label: '学习' },
  { to: '/me', label: '个人' },
]

export default function NavBar() {
  const { pathname } = useLocation()
  return (
    <nav className="flex gap-6 px-6 py-4 border-b bg-white sticky top-0 z-10">
      <span className="font-bold">个人集成学习网站</span>
      <div className="flex gap-4 ml-auto">
        {ITEMS.map((it) => (
          <Link key={it.to} to={it.to}
            className={pathname === it.to ? 'font-semibold text-blue-600' : 'text-gray-600'}>
            {it.label}
          </Link>
        ))}
      </div>
    </nav>
  )
}
