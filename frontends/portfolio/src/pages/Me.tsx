import SidebarLayout from '../components/SidebarLayout'
import SidebarNav from '../components/SidebarNav'
import Tag from '../components/Tag'
import PageChangelog from '../components/PageChangelog'
import PageTransition from '../components/PageTransition'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { PAGE_CHANGELOGS } from '../data/changelogs'

const SKILLS = [
  'Python', 'FastAPI', 'RAG', 'LangChain', 'React', 'Docker', 'AI/Agent 工程',
]

const SECTIONS = [
  { key: 'skills', label: '技能栈' },
  { key: 'resume', label: '简历' },
  { key: 'projects', label: '项目' },
  { key: 'history', label: '版本历史' },
]

export default function Me() {
  useDocumentTitle('个人 · 个人集成学习网站')

  const allHistory = Object.entries(PAGE_CHANGELOGS).flatMap(([page, entries]) =>
    entries.map((e) => ({ page, ...e })),
  )

  return (
    <PageTransition>
      <PageChangelog pageKey="me" />
      <SidebarLayout
        sidebar={
          <div>
            <div className="text-xs font-semibold text-muted uppercase tracking-wider mb-3 px-3">
              关于我
            </div>
            <SidebarNav items={SECTIONS.map((s) => ({ key: s.key, to: `#${s.key}`, label: s.label }))} activeKey="skills" />
          </div>
        }
      >
        <div className="space-y-6">
          <section id="skills" className="bg-surface border border-border rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-primary mb-4">技能栈</h2>
            <div className="flex flex-wrap gap-2">
              {SKILLS.map((s) => (
                <Tag key={s} color="slate">{s}</Tag>
              ))}
            </div>
          </section>

          <section id="resume" className="bg-surface border border-border rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-primary mb-4">简历</h2>
            <a
              href="/resume.pdf"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-4 py-2 rounded-lg bg-accent text-accent-text text-sm font-medium hover:opacity-90"
            >
              下载简历(PDF)
            </a>
          </section>

          <section id="projects" className="bg-surface border border-border rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-primary mb-4">项目</h2>
            <ul className="list-disc pl-5 text-secondary text-sm space-y-1">
              <li>
                <a href="/quiz/" target="_blank" rel="noopener noreferrer" className="text-link hover:underline">
                  cs-quiz-app 面试题库(待集成)
                </a>
              </li>
            </ul>
          </section>

          <section id="history" className="bg-surface border border-border rounded-xl p-6 shadow-sm">
            <h2 className="text-lg font-bold text-primary mb-4">版本历史</h2>
            <div className="space-y-4">
              {allHistory
                .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
                .slice(0, 10)
                .map((e, idx) => (
                  <div key={idx} className="text-sm">
                    <span className="font-semibold text-primary">v{e.version}</span>
                    <span className="text-muted text-xs ml-2">{e.date}</span>
                    <span className="text-tertiary text-xs ml-2 uppercase">[{e.page}]</span>
                    <ul className="mt-1 ml-4 list-disc text-secondary">
                      {e.items.map((item, i) => (
                        <li key={i}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ))}
            </div>
          </section>
        </div>
      </SidebarLayout>
    </PageTransition>
  )
}
