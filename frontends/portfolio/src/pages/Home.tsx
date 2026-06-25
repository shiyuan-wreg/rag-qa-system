import { useMemo, useState } from 'react'
import WorkCard from '../components/WorkCard'
import AnnouncementBoard from '../components/AnnouncementBoard'
import Hero from '../components/Hero'
import { WORKS } from '../data/works'
import { useScrollReveal } from '../hooks/useScrollReveal'

export default function Home() {
  const [query, setQuery] = useState('')
  useScrollReveal()

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

  return (
    <div>
      <Hero />

      <AnnouncementBoard />

      <section data-reveal className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <h2 className="text-xl font-bold text-primary">精选作品</h2>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="搜索作品..."
            className="w-full sm:w-64 px-3 py-2 text-sm rounded-lg border border-border bg-soft text-primary placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-link/30 transition-shadow"
          />
        </div>

        {filtered.length === 0 ? (
          <div className="text-center py-12 text-secondary text-sm">
            没有找到匹配“{query}”的作品
          </div>
        ) : (
          <div data-reveal className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {filtered.map((w) => (
              <WorkCard key={w.slug} work={w} />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
