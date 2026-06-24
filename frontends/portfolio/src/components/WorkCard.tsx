import { Link } from 'react-router-dom'
import { Work } from '../data/works'
import IconBox from './IconBox'
import Tag from './Tag'

const WORK_ACCENT: Record<string, { top: string; glow: string }> = {
  rag: { top: '#3b82f6', glow: 'rgba(59, 130, 246, 0.15)' },
  fc: { top: '#8b5cf6', glow: 'rgba(139, 92, 246, 0.15)' },
  nexus: { top: '#06b6d4', glow: 'rgba(6, 182, 212, 0.15)' },
  learn: { top: '#10b981', glow: 'rgba(16, 185, 129, 0.15)' },
  doctomd: { top: '#f59e0b', glow: 'rgba(245, 158, 11, 0.15)' },
}

const TAG_COLORS = ['blue', 'green', 'purple', 'cyan', 'orange', 'red', 'slate']

export default function WorkCard({ work }: { work: Work }) {
  const accent = WORK_ACCENT[work.slug] ?? { top: 'var(--accent-primary)', glow: 'var(--glow-accent)' }

  return (
    <Link
      to={work.path}
      className="group relative block bg-surface border border-border rounded-xl p-5 shadow-sm transition-all hover:shadow-glow hover:-translate-y-0.5 overflow-hidden"
    >
      <div
        className="absolute top-0 left-0 right-0 h-1 transition-all group-hover:h-1.5"
        style={{ backgroundColor: accent.top }}
      />
      <div className="flex items-start gap-4">
        <IconBox letter={work.icon.letter} bg={work.icon.bg} text={work.icon.text} />
        <div className="min-w-0">
          <h3 className="font-bold text-primary group-hover:text-link transition-colors">
            {work.title}
          </h3>
          <p className="mt-1 text-sm text-secondary line-clamp-2">{work.desc}</p>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap gap-2">
        {work.tech.map((t, idx) => (
          <Tag key={t} color={TAG_COLORS[idx % TAG_COLORS.length]}>
            {t}
          </Tag>
        ))}
      </div>
    </Link>
  )
}
