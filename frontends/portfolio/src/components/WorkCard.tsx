import { Link } from 'react-router-dom'
import { Work } from '../data/works'
import Icon from './Icon'
import Tag from './Tag'

export default function WorkCard({ work }: { work: Work }) {
  return (
    <Link
      to={work.path}
      className="work-card group block bg-surface border border-border rounded-lg p-5 shadow-sm"
    >
      <span className="work-card__scan" />
      <div className="work-card__inner">
        <div className="flex items-center justify-between">
          <span className="font-mono text-xs tracking-widest text-muted">{work.index}</span>
          <span className="w-9 h-9 rounded-md border border-border flex items-center justify-center text-secondary transition-colors group-hover:text-primary group-hover:border-strong">
            <Icon name={work.icon} />
          </span>
        </div>
        <h3 className="mt-4 font-semibold text-primary tracking-tight">{work.title}</h3>
        <p className="mt-1.5 text-sm text-secondary line-clamp-2">{work.desc}</p>
        <div className="mt-4 flex flex-wrap gap-2">
          {work.tech.map((t) => (
            <Tag key={t}>{t}</Tag>
          ))}
        </div>
      </div>
    </Link>
  )
}
