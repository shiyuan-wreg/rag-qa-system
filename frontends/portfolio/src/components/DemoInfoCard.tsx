import { Work } from '../data/works'
import Tag from './Tag'

const TAG_COLORS = ['blue', 'green', 'purple', 'cyan', 'orange', 'red', 'slate']

export default function DemoInfoCard({ work }: { work: Work }) {
  return (
    <div className="bg-surface border border-border rounded-xl p-5 shadow-sm">
      <h1 className="text-xl font-bold text-primary">{work.title}</h1>
      <p className="mt-2 text-sm text-secondary leading-relaxed">{work.desc}</p>
      <div className="mt-4 flex flex-wrap gap-2">
        {work.tech.map((t, idx) => (
          <Tag key={t} color={TAG_COLORS[idx % TAG_COLORS.length]}>
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
  )
}
