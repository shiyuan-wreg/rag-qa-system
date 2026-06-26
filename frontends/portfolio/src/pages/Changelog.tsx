import PageTransition from '../components/PageTransition'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { CHANGELOGS } from '../data/changelogs'

export default function Changelog() {
  useDocumentTitle('更新公告 · 个人集成学习网站')

  const notes = CHANGELOGS

  return (
    <PageTransition>
      <div className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <header className="mb-8">
          <h1 className="text-2xl md:text-3xl font-extrabold text-primary tracking-tight">更新公告</h1>
          <p className="mt-2 text-sm md:text-base text-secondary">
            站点与各子作品的版本迭代记录，共 {notes.length} 条更新。
          </p>
        </header>

        <div className="space-y-4">
          {notes.map((note) => (
            <article
              key={note.version}
              className="hud-frame rounded-xl border border-border bg-surface shadow-sm hover:shadow-md transition-shadow p-5"
            >
              <div className="flex items-center gap-2 flex-wrap mb-3">
                <span className="font-mono text-xs tracking-wide text-muted">
                  v{note.version}
                </span>
                <span className="font-mono text-xs tracking-wide text-muted">{note.date}</span>
              </div>
              <ul className="space-y-1.5">
                {note.items.map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-secondary">
                    <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-strong shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </div>
    </PageTransition>
  )
}
