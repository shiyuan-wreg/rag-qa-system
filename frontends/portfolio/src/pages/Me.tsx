import { Link } from 'react-router-dom'
import SidebarLayout from '../components/SidebarLayout'
import SidebarNav from '../components/SidebarNav'
import Tag from '../components/Tag'
import WorkCard from '../components/WorkCard'
import PageTransition from '../components/PageTransition'
import { useDocumentTitle } from '../hooks/useDocumentTitle'
import { WORKS } from '../data/works'

const ROLE_TAGS = ['AI / Agent 开发', '全栈工程', 'RAG / LLM 应用']

// 技能按方向分组，制造层次而非一堆扁平标签。
const SKILL_GROUPS: { title: string; letter: string; bg: string; text: string; skills: string[] }[] = [
  { title: '语言', letter: '⌘', bg: '#eff6ff', text: '#1d4ed8', skills: ['Python', 'TypeScript', 'JavaScript', 'SQL'] },
  { title: 'AI / Agent', letter: 'A', bg: '#ecfeff', text: '#0e7490', skills: ['RAG', 'Function Calling', 'Multi-Agent', 'LangChain', 'Prompt 工程', '通义千问'] },
  { title: '后端', letter: 'B', bg: '#faf5ff', text: '#7e22ce', skills: ['FastAPI', 'REST API', 'SSE', 'Flask'] },
  { title: '前端', letter: 'F', bg: '#f0fdf4', text: '#15803d', skills: ['React', 'Vite', 'TailwindCSS', 'Vite + TS'] },
  { title: '工程化 / 部署', letter: 'D', bg: '#fff7ed', text: '#c2410c', skills: ['Docker', 'Nginx', 'Linux', 'Git', 'CI/CD'] },
]

const SECTIONS = [
  { key: 'skills', label: '技能栈' },
  { key: 'works', label: '作品' },
  { key: 'resume', label: '简历' },
  { key: 'history', label: '更新记录' },
]

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="flex items-center gap-2 text-lg font-bold text-primary mb-4">
      <span className="w-1 h-5 rounded-full bg-accent" />
      {children}
    </h2>
  )
}

export default function Me() {
  useDocumentTitle('个人 · 个人集成学习网站')

  return (
    <PageTransition>
      <div className="max-w-content mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* 顶部定位区 */}
        <section className="relative overflow-hidden rounded-2xl border border-border bg-hero shadow-sm">
          <div
            className="absolute inset-0 pointer-events-none"
            style={{ backgroundImage: 'radial-gradient(circle at 15% 120%, var(--glow-accent), transparent 50%)' }}
          />
          <div className="relative flex flex-col sm:flex-row items-center sm:items-start gap-6 p-6 sm:p-8">
            {/* 头像（图形化，无个人信息） */}
            <div
              className="w-20 h-20 rounded-2xl flex items-center justify-center shrink-0 shadow-md text-accent-text"
              style={{ background: 'linear-gradient(135deg, var(--accent-primary), var(--text-link))' }}
            >
              <svg width="38" height="38" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="16 18 22 12 16 6" />
                <polyline points="8 6 2 12 8 18" />
              </svg>
            </div>

            <div className="flex-1 text-center sm:text-left min-w-0">
              <div className="flex flex-wrap justify-center sm:justify-start gap-2 mb-3">
                {ROLE_TAGS.map((t) => (
                  <span key={t} className="px-2.5 py-0.5 rounded-full bg-accent-secondary-bg text-accent-secondary-text text-xs font-semibold">
                    {t}
                  </span>
                ))}
              </div>
              <h1 className="text-2xl md:text-3xl font-extrabold text-primary tracking-tight">
                构建可运行的 AI / Agent 应用
              </h1>
              <p className="mt-3 text-sm md:text-base text-secondary leading-relaxed max-w-2xl">
                从 RAG、Function Calling 到 Multi-Agent 工作流，专注把大模型能力工程化、产品化，整合成可部署、可演示的完整作品。
              </p>
              <div className="mt-5 flex flex-wrap justify-center sm:justify-start gap-3">
                <a href="#works" className="inline-flex items-center px-4 py-2 rounded-lg bg-accent text-accent-text text-sm font-medium hover:opacity-90 transition-opacity">
                  浏览作品
                </a>
                <a
                  href="https://github.com/shiyuan-wreg"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg border border-border bg-surface text-primary text-sm font-medium hover:bg-surface-hover transition-colors"
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                    <path d="M12 .5C5.7.5.5 5.7.5 12c0 5.1 3.3 9.4 7.9 10.9.6.1.8-.2.8-.6v-2c-3.2.7-3.9-1.4-3.9-1.4-.5-1.3-1.3-1.7-1.3-1.7-1.1-.7.1-.7.1-.7 1.2.1 1.8 1.2 1.8 1.2 1 1.8 2.7 1.3 3.4 1 .1-.8.4-1.3.7-1.6-2.6-.3-5.3-1.3-5.3-5.7 0-1.3.5-2.3 1.2-3.1-.1-.3-.5-1.5.1-3.1 0 0 1-.3 3.3 1.2a11.5 11.5 0 0 1 6 0C17 4.6 18 4.9 18 4.9c.6 1.6.2 2.8.1 3.1.8.8 1.2 1.8 1.2 3.1 0 4.4-2.7 5.4-5.3 5.7.4.4.8 1.1.8 2.2v3.3c0 .4.2.7.8.6 4.6-1.5 7.9-5.8 7.9-10.9C23.5 5.7 18.3.5 12 .5z" />
                  </svg>
                  GitHub
                </a>
              </div>
            </div>
          </div>
        </section>

        <SidebarLayout
          sidebar={
            <div>
              <div className="text-xs font-semibold text-muted uppercase tracking-wider mb-3 px-3">导航</div>
              <SidebarNav items={SECTIONS.map((s) => ({ key: s.key, to: `#${s.key}`, label: s.label }))} activeKey="skills" />
            </div>
          }
        >
          <div className="space-y-6">
            {/* 技能栈分组 */}
            <section id="skills" className="bg-surface border border-border rounded-xl p-6 shadow-sm">
              <SectionTitle>技能栈</SectionTitle>
              <div className="grid sm:grid-cols-2 gap-4">
                {SKILL_GROUPS.map((g) => (
                  <div key={g.title} className="bg-surface-soft border border-border-subtle rounded-lg p-4">
                    <div className="flex items-center gap-2.5 mb-3">
                      <span
                        className="w-8 h-8 rounded-md flex items-center justify-center text-sm font-bold shrink-0"
                        style={{ backgroundColor: g.bg, color: g.text }}
                      >
                        {g.letter}
                      </span>
                      <span className="font-semibold text-primary text-sm">{g.title}</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {g.skills.map((s) => (
                        <Tag key={s}>{s}</Tag>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </section>

            {/* 作品卡片区 */}
            <section id="works" className="bg-surface border border-border rounded-xl p-6 shadow-sm">
              <SectionTitle>作品</SectionTitle>
              <div className="grid sm:grid-cols-2 gap-5">
                {WORKS.map((w) => (
                  <WorkCard key={w.slug} work={w} />
                ))}
              </div>
            </section>

            {/* 简历 */}
            <section id="resume" className="bg-surface border border-border rounded-xl p-6 shadow-sm">
              <SectionTitle>简历</SectionTitle>
              <p className="text-sm text-secondary mb-4">完整的项目经历与技术细节见简历文件。</p>
              <a
                href="/resume.pdf"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg bg-accent text-accent-text text-sm font-medium hover:opacity-90 transition-opacity"
              >
                下载简历(PDF)
              </a>
            </section>

            {/* 更新记录 */}
            <section id="history" className="bg-surface border border-border rounded-xl p-6 shadow-sm">
              <SectionTitle>更新记录</SectionTitle>
              <p className="text-sm text-secondary mb-4">站点与各子作品的完整版本迭代记录。</p>
              <Link
                to="/changelog"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-lg border border-border bg-surface text-primary text-sm font-medium hover:bg-surface-hover transition-colors"
              >
                查看全部更新 →
              </Link>
            </section>
          </div>
        </SidebarLayout>
      </div>
    </PageTransition>
  )
}
