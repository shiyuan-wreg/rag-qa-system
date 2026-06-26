import { Work } from '../data/works'
import Tag from './Tag'

export default function DemoInfoCard({ work }: { work: Work }) {
  return (
    <div className="border-t border-border-subtle pt-5">
      <h2 className="px-3 text-xs font-semibold text-muted uppercase tracking-wider mb-3">
        关于这个作品
      </h2>
      <div className="hud-frame demo-info-card bg-surface-soft border border-border rounded-xl p-4">
        <h1 className="text-base font-bold text-primary">{work.title}</h1>
        <p className="mt-2 text-sm text-secondary leading-relaxed">{work.desc}</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {work.tech.map((t) => (
            <Tag key={t}>
              {t}
            </Tag>
          ))}
        </div>
        {work.github && (
          <a
            href={work.github}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-4 inline-flex text-sm font-medium text-link hover:underline"
          >
            查看源码 →
          </a>
        )}
      </div>
    </div>
  )
}
