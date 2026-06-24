import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import Button from '../components/Button'
import WorkCard from '../components/WorkCard'
import { WORKS } from '../data/works'
import { PAGE_CHANGELOGS } from '../data/changelogs'

export default function Home() {
  const [query, setQuery] = useState('')

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return WORKS
    return WORKS.filter(
      (w) =>
        w.title.toLowerCase().includes(q) ||
        w.desc.toLowerCase().includes(q) ||
        w.tech.some((t) => t.toLowerCase().includes(q)),
    )
  }, [query])

  const latestHome = PAGE_CHANGELOGS.home[0]

  return (
    <div>
      <section className="bg-hero border-b border-border-subtle">
        <div className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-20 text-center">
          {latestHome && (
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-accent-secondary-bg text-accent-secondary-text text-xs font-semibold mb-6">
              <span>v{latestHome.version}</span>
              <span>·</span>
              <span>{latestHome.items[0]}</span>
            </div>
          )}
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-extrabold text-primary tracking-tight">
            探索 AI 与 Agent 的工程实践
          </h1>
          <p className="mt-5 text-base md:text-lg text-secondary max-w-2xl mx-auto leading-relaxed">
            从 RAG、Function Calling 到 Multi-Agent 工作流，把分散的实验整合成一个可运行的作品集门户。
          </p>
          <div className="mt-8 flex items-center justify-center gap-3">
            <Link to="/rag">
              <Button>浏览作品</Button>
            </Link>
            <Link to="/learn">
              <Button variant="secondary">开始学习</Button>
            </Link>
          </div>
        </div>
      </section>

      <section className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <h2 className="text-xl font-bold text-primary">精选作品</h2>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="搜索作品..."
            className="w-full sm:w-64 px-3 py-2 text-sm rounded-lg border border-border bg-surface text-primary placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-link/30"
          />
        </div>

        {filtered.length === 0 ? (
          <div className="text-center py-12 text-secondary text-sm">
            没有找到匹配“{query}”的作品
          </div>
        ) : (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((w) => (
              <WorkCard key={w.slug} work={w} />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
