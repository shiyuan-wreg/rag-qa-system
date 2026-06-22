import { Link } from 'react-router-dom'
import { WORKS } from '../data/works'

export default function Home() {
  return (
    <div className="max-w-5xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2">个人集成学习网站</h1>
      <p className="text-gray-600 mb-8">AI 应用与 Agent 相关作品的集中展示。</p>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {WORKS.map((w) => (
          <Link key={w.slug} to={w.path}
            className="block p-5 border rounded-lg hover:shadow transition">
            <h3 className="font-semibold mb-1">{w.title}</h3>
            <p className="text-sm text-gray-600">{w.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  )
}
