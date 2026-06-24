import { Link } from 'react-router-dom'
import { Work } from '../data/works'
import IconBox from './IconBox'
import Tag from './Tag'

const TAG_COLORS = ['blue', 'green', 'purple', 'cyan', 'orange', 'red', 'slate']

export default function WorkCard({ work }: { work: Work }) {
  return (
    <Link
      to={work.path}
      className="group block bg-surface border border-border rounded-xl p-5 shadow-sm transition-all hover:shadow-md hover:border-border"
    >
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
