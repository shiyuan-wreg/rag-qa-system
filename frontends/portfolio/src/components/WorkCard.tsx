import { Link } from 'react-router-dom'
import { Work } from '../data/works'
import Tag from './Tag'

export default function WorkCard({ work, style }: { work: Work; style?: React.CSSProperties }) {
  return (
    <Link
      to={work.path}
      className="hud-frame work-card group block bg-surface border border-border rounded-lg p-5 shadow-md"
      style={style}
    >
      <span className="work-card__scan" />
      <div className="work-card__inner">
        <div className="flex items-center justify-between">
          <span className="font-mono text-xs tracking-widest text-muted">{work.index}</span>
          <span className="w-10 h-10 rounded-md border border-border flex items-center justify-center overflow-hidden transition-colors group-hover:border-strong">
            <img src={work.icon} alt="" className="demo-icon w-6 h-6 object-contain" />
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
